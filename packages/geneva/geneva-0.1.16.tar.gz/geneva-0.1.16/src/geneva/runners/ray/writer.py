# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import heapq
import logging
import re
import uuid
from collections.abc import Iterator
from typing import cast

import attrs
import lance
import lance.file
import pyarrow as pa
import ray
import ray.actor
import ray.util.queue

from geneva.checkpoint import CheckpointStore

_LOG = logging.getLogger(__name__)


def _combine_chunks(arr: pa.Array) -> pa.Array:
    if isinstance(arr, pa.ChunkedArray):
        assert len(arr.chunks) == 1
        return arr.chunks[0]
    return arr


def _align_batch_to_row_address(batch: pa.RecordBatch) -> pa.RecordBatch:
    """
    align a single batch to _rowaddr column, which is assumed to be
    * present, and
    * sorted
    In addition, the arraies in the batch are not pa.ChunkedArray
    if no "holes", non-contiguous row addr, is present, this function
    will return the input batch

    for any "holes" in the batch, nulls are filled in place
    """

    if "_rowaddr" not in batch.schema.names:
        raise ValueError(
            "No _rowaddr column found in the batch,"
            " please make sure the scanner is configured with with_row_address=True"
        )

    rowaddr: pa.Array = batch["_rowaddr"]

    rowaddr_start = rowaddr[0].as_py()
    rowaddr_end = rowaddr[-1].as_py()

    num_phyical_rows_in_range = rowaddr_end - rowaddr_start + 1

    if num_phyical_rows_in_range == batch.num_rows:
        return batch

    # TODO: this is inefficient in python, do it in rust
    data_dict = {
        "_rowaddr": pa.array(range(rowaddr_start, rowaddr_end + 1), type=pa.uint64()),
    }
    for name in batch.schema.names:
        if name == "_rowaddr":
            continue

        arr = batch[name]

        def _iter(name=name):  # noqa: ANN202
            next_idx = rowaddr_start
            for val, row_addr in zip(
                batch[name].to_pylist(), rowaddr.to_pylist(), strict=False
            ):
                while next_idx < row_addr:
                    yield None
                    next_idx += 1
                yield val
                next_idx += 1

        data_dict[name] = pa.array(_iter(), type=arr.type)

    return batch.from_pydict(data_dict, schema=batch.schema)


def _buffer_and_sort_batches(
    num_logical_rows: int,
    store: CheckpointStore,
    queue: ray.util.queue.Queue,
) -> Iterator[pa.RecordBatch]:
    """
    buffer batches from the queue, which is yields a tuple of
    * serial number of the batch -- currently the offset of the batch
    * the data key dict of the batch

    serial number can arrive out of order, so we need to buffer them
    until we have the next expected serial number. In most cases, the
    serial number is the offset of the batch, and we keep track of the
    expected serial number in the variable `written_rows`
    """
    written_rows = 0
    buffer: list[tuple[int, dict[str, str]]] = []
    while written_rows < num_logical_rows:
        while not buffer or buffer[0][0] != written_rows:
            try:
                batch: tuple[int, dict[str, str]] = queue.get()
            except (
                ray.exceptions.ActorDiedError,
                ray.exceptions.ActorUnavailableError,
            ):
                _LOG.exception("Writer failed to read from checkpoint queue, exiting")
                ray.actor.exit_actor()

            heapq.heappush(buffer, batch)

        data = heapq.heappop(buffer)[1]
        rowaddr_arr = None
        data_dict = {}
        for key, value in data.items():
            current_rowaddr_arr = store[value]["_rowaddr"]
            if rowaddr_arr is None:
                rowaddr_arr = current_rowaddr_arr

            if rowaddr_arr != current_rowaddr_arr:
                raise ValueError(
                    "Row address column mismatch, this means we are receving"
                    " checkpoints that are not aligned to each other"
                )

            data_dict[key] = _combine_chunks(store[value]["data"])
        data_dict["_rowaddr"] = rowaddr_arr

        res = pa.RecordBatch.from_pydict(data_dict)
        yield res
        written_rows += res.num_rows


def _make_filler_batch(
    fill_start: int,
    fill_end: int,
    schema: pa.Schema,
) -> pa.RecordBatch:
    """
    make a filler batch that fills the range [fill_start, fill_end]"""
    rowaddr_arr = pa.array(range(fill_start, fill_end), type=pa.uint64())
    data_dict = {
        name: pa.array(
            [None] * (fill_end - fill_start), type=schema.field_by_name(name).type
        )
        for name in schema.names
        if name != "_rowaddr"
    }
    data_dict["_rowaddr"] = rowaddr_arr
    return pa.RecordBatch.from_pydict(data_dict, schema=schema)


def _align_batches_to_physical_layout(
    num_physical_rows: int,
    num_logical_rows: int,
    frag_id: int,
    batches: Iterator[pa.RecordBatch],
) -> Iterator[pa.RecordBatch]:
    """
    same as _buffer_and_sort_batches,
    but also align the batches to the physical rows layout
    """

    if num_logical_rows > num_physical_rows:
        raise ValueError(
            "Logical rows should be greater than or equal to physical rows"
        )

    next_batch_rowaddr = 0

    schema = None

    for batch in map(
        _align_batch_to_row_address,
        batches,
    ):
        # skim the schema from the stream
        # we expect at least one batch, otherwise the whole fragment has been
        # deleted and the metadata would have been deleted by lance so we wouldn't
        # be here because no writer would be created
        if schema is None:
            schema = batch.schema

        incoming_local_rowaddr = batch["_rowaddr"][0].as_py() & 0xFFFFFFFF
        if incoming_local_rowaddr != next_batch_rowaddr:
            fill_start = frag_id << 32 | next_batch_rowaddr
            yield _make_filler_batch(fill_start, batch["_rowaddr"][0].as_py(), schema)
            next_batch_rowaddr = incoming_local_rowaddr

        yield batch
        next_batch_rowaddr += batch.num_rows

    if schema is None:
        raise ValueError("No batches found")

    # fill the rest of the rows at the end
    if next_batch_rowaddr < num_physical_rows:
        fill_start = frag_id << 32 | next_batch_rowaddr
        fill_end = frag_id << 32 | num_physical_rows
        yield _make_filler_batch(fill_start, fill_end, schema)


@ray.remote(num_cpus=1)
@attrs.define
class FragmentWriter:
    uri: str
    column_name: str
    store: CheckpointStore

    fragment_id: int

    checkpoint_keys: ray.util.queue.Queue

    align_physical_rows: bool = False

    def write(self) -> tuple[int, lance.fragment.DataFile]:
        dataset = lance.dataset(self.uri)
        frag = dataset.get_fragment(self.fragment_id)
        if frag is None:
            raise ValueError(f"Fragment {self.fragment_id} not found")
        num_physical_rows = frag.physical_rows
        num_logical_rows = frag.count_rows()

        import more_itertools

        # we always write files that physically align with the fragment
        it = _buffer_and_sort_batches(
            num_logical_rows,
            self.store,
            self.checkpoint_keys,
        )
        if self.align_physical_rows:
            it = _align_batches_to_physical_layout(
                num_physical_rows,
                num_logical_rows,
                self.fragment_id,
                it,
            )

        it = more_itertools.peekable(it)

        file_id = str(uuid.uuid4())

        with lance.file.LanceFileWriter(
            f"{self.uri}/data/{file_id}.lance",
            it.peek().schema,
        ) as writer:
            for batch in it:
                writer.write_batch(batch)

        # MASSIVE HACK: open up an API to get the field id from the column name
        field_id = re.compile(
            rf'name: "{self.column_name}", id: (?P<field_id>[\d]*),'
        ).findall(str(dataset.lance_schema))
        assert len(field_id) == 1
        field_id = int(field_id[0])

        new_datafile = lance.fragment.DataFile(
            f"{file_id}.lance",
            [field_id],
            [0],
            2,
            0,
        )

        new_datafile.fields = [field_id]
        new_datafile.column_indices = [0]

        return self.fragment_id, new_datafile


FragmentWriter: ray.actor.ActorClass = cast(ray.actor.ActorClass, FragmentWriter)
