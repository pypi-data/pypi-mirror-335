# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import hashlib
import itertools
import logging
import random
from collections.abc import Callable, Iterator
from typing import TypeVar

import attrs
import lance
import more_itertools
import pyarrow as pa

from geneva.checkpoint import (
    CheckpointStore,
)
from geneva.debug.logger import ErrorLogger, NoOpErrorLogger
from geneva.query import Scan
from geneva.transformer import UDF

_LOG = logging.getLogger(__name__)


@attrs.define(order=True)
class ReadTask:
    uri: str
    columns: list[str]
    frag_id: int
    offset: int
    limit: int

    version: int | None = None
    filter: str | None = None

    with_row_address: bool = False

    def to_batches(self, *, batch_size=32) -> Iterator[pa.RecordBatch]:
        uri_parts = self.uri.split("/")
        name = ".".join(uri_parts[-1].split(".")[:-1])
        db = "/".join(uri_parts[:-1])
        scan = (
            Scan.from_uri(db, name, version=self.version)
            .with_columns(self.columns)
            .with_fragments([self.frag_id])
            .with_filter(self.filter)
            .with_offset(self.offset)
            .with_limit(self.limit)
        )
        if self.with_row_address:
            scan = scan.with_row_address()
        yield from scan.to_batches(batch_size)

    def checkpoint_key(self) -> str:
        hasher = hashlib.md5()
        hasher.update(
            f"{self.uri}:{self.version}:{self.columns}:{self.frag_id}:{self.offset}:{self.limit}:{self.filter}".encode(),
        )
        return hasher.hexdigest()


@attrs.define
class LanceRecordBatchUDFApplier:
    udfs: dict[str, UDF] = attrs.field()
    checkpoint_store: CheckpointStore = attrs.field()
    error_logger: ErrorLogger = attrs.field(default=NoOpErrorLogger())

    batch_size: int = 32

    @property
    def output_schema(self) -> pa.Schema:
        return pa.schema(
            [pa.field(name, fn.data_type) for name, fn in self.udfs.items()],
        )

    def _run(self, task: ReadTask) -> dict[str, str]:
        data_key = task.checkpoint_key()
        _LOG.debug("Running task %s", task)
        # track the batch sequence number so we can checkpoint any errors
        # when reproducing locally we can seek to the erroring batch quickly

        # prepare the schema
        fields = []
        for name, fn in self.udfs.items():
            fields.append(pa.field(name, fn.data_type, metadata=fn.field_metadata))

        res = {}
        batch = None
        for name, fn in self.udfs.items():
            checkpoint_key = f"{data_key}:{fn.checkpoint_key}"
            if checkpoint_key in self.checkpoint_store:
                _LOG.info("Using cached result for %s", checkpoint_key)
                res[name] = checkpoint_key
                continue
            arrs = []
            row_addrs = []
            # PERF203 -- don't try-except inside the loop
            # so I had to move the loop inside the try-except
            # and need some loop state tracking for error logggin
            seq = 0
            # TODO: add caching for the input data
            try:
                for _seq, batch in enumerate(
                    task.to_batches(batch_size=self.batch_size)
                ):
                    seq = _seq
                    arrs.append(fn(batch))
                    row_addrs.append(batch["_rowaddr"])
            except Exception as e:
                self.error_logger.log_error(e, task, fn, seq)
                raise e

            arr = pa.concat_arrays(arrs)
            row_addr_arr = pa.concat_arrays(row_addrs)
            self.checkpoint_store[checkpoint_key] = pa.RecordBatch.from_pydict(
                {"data": arr, "_rowaddr": row_addr_arr},
                schema=pa.schema(
                    [pa.field("data", fn.data_type), pa.field("_rowaddr", pa.uint64())]
                ),
            )
            res[name] = checkpoint_key

        return res

    def run(self, task: ReadTask) -> dict[str, str]:
        try:
            return self._run(task)
        except Exception as e:
            logging.exception("Error running task %s: %s", task, e)
            raise RuntimeError(f"Error running task {task}") from e

    def status(self, task: ReadTask) -> dict[str, str]:
        data_key = task.checkpoint_key()
        return {
            name: f"{data_key}:{fn.checkpoint_key}" in self.checkpoint_store
            for name, fn in self.udfs.items()
        }  # type: ignore


def _plan_read(
    uri: str,
    columns: list[str] | None = None,
    *,
    read_version: int | None = None,
    batch_size: int = 512,
    filter: str | None = None,  # noqa: A002
    num_frags: int | None = None,
) -> Iterator[ReadTask]:
    """Make Plan for Reading Data from a Dataset"""
    if columns is None:
        columns = []
    dataset = lance.dataset(uri)
    if read_version is not None:
        dataset = dataset.checkout_version(read_version)

    for idx, frag in enumerate(dataset.get_fragments()):
        if num_frags is not None and idx >= num_frags:
            break
        frag_rows = frag.count_rows(filter=filter)
        for offset in range(0, frag_rows, batch_size):
            limit = min(batch_size, frag_rows - offset)
            yield ReadTask(
                uri=uri,
                version=read_version,
                columns=columns,
                frag_id=frag.fragment_id,
                offset=offset,
                limit=limit,
                filter=filter,
                with_row_address=True,
            )


@attrs.define
class _LanceReadPlanIterator(Iterator[ReadTask]):
    it: Iterator[ReadTask]
    total: int

    def __iter__(self) -> Iterator[ReadTask]:
        return self

    def __next__(self) -> ReadTask:
        return next(self.it)

    def __len__(self) -> int:
        return self.total


def _num_tasks(
    *,
    uri: str,
    read_version: int | None = None,
    batch_size: int = 512,
) -> int:
    return sum(
        -(-frag.count_rows() // batch_size)
        for frag in (lance.dataset(uri, version=read_version)).get_fragments()
    )


T = TypeVar("T")


def _buffered_shuffle(it: Iterator[T], buffer_size: int) -> Iterator[T]:
    """Shuffle an iterator using a buffer of size buffer_size
    not perfectly random, but good enough for spreading out IO
    """
    # Initialize the buffer with the first buffer_size items from the iterator
    buffer = []
    # Fill the buffer with up to buffer_size items initially
    try:
        for _ in range(buffer_size):
            item = next(it)
            buffer.append(item)
    except StopIteration:
        pass

    while True:
        # Select a random item from the buffer
        index = random.randint(0, len(buffer) - 1)
        item = buffer[index]

        # Try to replace the selected item with a new one from the iterator
        try:
            next_item = next(it)
            buffer[index] = next_item
            # Yield the item AFTER replacing it in the buffer
            # this way the buffer is always contiguous so we can
            # simply yield the buffer at the end
            yield item
        except StopIteration:
            yield from buffer
            break


R = TypeVar("R")


def diversity_aware_shuffle(
    it: Iterator[T],
    key: Callable[[T], R],
    *,
    diversity_goal: int = 4,
    buffer_size: int = 1024,
) -> Iterator[T]:
    """A shuffle iterator that is aware of the diversity of the data
    being shuffled. The key function should return a value that is
    is used to determine the diversity of the data. The diversity_goal
    is the number of unique values that should be in the buffer at any
    given time. if the buffer is full, the items is yielded in a round-robin
    fashion. This is useful for shuffling tasks that are diverse, but

    This algorithm is bounded in memory by the buffer_size, so it is reasonably
    efficient for large datasets.
    """

    # NOTE: this is similar to itertools.groupby, but with a buffering limit

    buffer: dict[R, list[T]] = {}
    buffer_total_size = 0

    peekable_it = more_itertools.peekable(it)

    def _maybe_consume_from_iter() -> bool:
        nonlocal buffer_total_size
        item = peekable_it.peek(default=None)
        if item is None:
            return False
        key_val = key(item)
        if key_val not in buffer and len(buffer) < diversity_goal:
            buffer[key_val] = []
        else:
            return False

        # if the buffer still has room, add the item
        if buffer_total_size < buffer_size:
            buffer[key_val].append(item)
            buffer_total_size += 1
        else:
            return False

        next(peekable_it)
        return True

    while _maybe_consume_from_iter():
        ...

    production_counter = 0

    def _next_key() -> T | None:
        nonlocal buffer_total_size, production_counter
        if not buffer_total_size:
            return None

        # TODO: add warning about buffer size not big enough for diversity_goal
        buffer_slot = production_counter % len(buffer)
        key = next(itertools.islice(buffer.keys(), buffer_slot, buffer_slot + 1))
        assert key in buffer
        key_buffer = buffer[key]

        buffer_total_size -= 1
        item = key_buffer.pop(0)
        if not key_buffer:
            del buffer[key]

        # try to fill the removed buffer slot
        _maybe_consume_from_iter()
        production_counter += 1
        return item

    while (item := _next_key()) is not None:
        yield item


def plan_read(
    uri: str,
    columns: list[str] | None = None,
    *,
    read_version: int | None = None,
    batch_size: int = 512,
    filter: str | None = None,  # noqa: A002
    shuffle_buffer_size: int = 0,
    task_shuffle_diversity: int | None = None,
    num_frags: int | None = None,
    **kwargs,
) -> Iterator[ReadTask]:
    """Make Plan for Reading Data from a Dataset"""
    it = _plan_read(
        uri,
        columns=columns,
        read_version=read_version,
        batch_size=batch_size,
        filter=filter,
        num_frags=num_frags,
    )
    # same as no shuffle
    if shuffle_buffer_size > 1 and task_shuffle_diversity is None:
        it = _buffered_shuffle(it, buffer_size=shuffle_buffer_size)
    elif task_shuffle_diversity is not None:
        buffer_size = max(4 * task_shuffle_diversity, shuffle_buffer_size)
        it = diversity_aware_shuffle(
            it,
            key=lambda task: task.checkpoint_key(),
            diversity_goal=task_shuffle_diversity,
            buffer_size=buffer_size,
        )

    return _LanceReadPlanIterator(
        it, _num_tasks(uri=uri, read_version=read_version, batch_size=batch_size)
    )
