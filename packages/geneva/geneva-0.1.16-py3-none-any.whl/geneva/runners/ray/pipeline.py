# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import contextlib
import functools
import hashlib
import logging
import random
import uuid
from collections.abc import Iterator
from typing import cast

import attrs
import bidict
import lance
import pyarrow as pa
import ray.actor
import ray.data
import ray.exceptions
import ray.util.queue

from geneva.apply import LanceRecordBatchUDFApplier, ReadTask, plan_read
from geneva.checkpoint import CheckpointStore
from geneva.debug.logger import CheckpointStoreErrorLogger
from geneva.job.config import JobConfig
from geneva.runners.ray.actor_pool import ActorPool
from geneva.runners.ray.writer import FragmentWriter
from geneva.tqdm import tqdm
from geneva.transformer import UDF

_LOG = logging.getLogger(__name__)

_SIMULATE_WRITE_FAILURE = False


@contextlib.contextmanager
def _simulate_write_failure(flag: bool) -> Iterator[None]:
    global _SIMULATE_WRITE_FAILURE
    current = _SIMULATE_WRITE_FAILURE
    try:
        _SIMULATE_WRITE_FAILURE = flag
        yield
    finally:
        _SIMULATE_WRITE_FAILURE = current


@ray.remote
@attrs.define
class ApplierActor:
    applier: LanceRecordBatchUDFApplier

    def run(self, task) -> tuple[ReadTask, dict[str, str]]:
        return task, self.applier.run(task)


ApplierActor: ray.actor.ActorClass = cast(ray.actor.ActorClass, ApplierActor)


def _get_fragment_dedupe_key(
    uri: str, frag_id: int, output_column: str, transform: UDF
) -> str:
    key = f"{uri}:{frag_id}:{output_column}:{transform.checkpoint_key}"
    return hashlib.sha256(key.encode()).hexdigest()


def run_ray_add_column(
    uri: str,
    columns: list[str],
    transforms: dict[str, UDF],
    *,
    checkpoint_store: CheckpointStore | None = None,
    read_version: int | None = None,
    job_id: str | None = None,
    concurrency: int = 8,
    batch_size: int | None = None,
    applier_batch_size: int | None = None,
    test_run: bool = True,
    **kwargs,
) -> None:
    # prepare job parameters
    config = JobConfig.get()

    batch_size = batch_size or config.batch_size
    applier_batch_size = applier_batch_size or config.applier_batch_size
    checkpoint_store = checkpoint_store or config.make_checkpoint_store()
    if "task_shuffle_diversity" not in kwargs:
        kwargs["task_shuffle_diversity"] = config.task_shuffle_diversity

    if read_version is None:
        read_version = lance.dataset(uri).version

    job_id = job_id or uuid.uuid4().hex

    assert len(transforms) == 1, "Only one column can be added at a time"

    udf = list(transforms.values())[0]
    applier = LanceRecordBatchUDFApplier(
        udfs=transforms,
        checkpoint_store=checkpoint_store,
        error_logger=CheckpointStoreErrorLogger(job_id, checkpoint_store),
        batch_size=applier_batch_size,
    )

    actor = ApplierActor

    actor = actor.options(num_cpus=udf.num_cpus)
    if udf.memory:
        actor = actor.options(memory=udf.memory)

    pool = ActorPool(functools.partial(actor.remote, applier=applier), concurrency)

    plan = tqdm(
        plan_read(
            uri,
            columns,
            batch_size=batch_size,
            read_version=read_version,
            **kwargs,
        )
    )

    table_name = uri.split("/")[-1].split(".")[0]
    output_column = list(transforms.keys())[0]
    pbar_prefix = f"[{table_name} - {output_column}]"

    ds = lance.dataset(uri, version=read_version)
    writer_pbar = tqdm(total=len(ds.get_fragments()), position=1)
    writer_pbar.set_description(f"{pbar_prefix} Writing Fragments")

    @functools.lru_cache
    def _fragment_is_done(frag_id: int) -> bool:
        dedupe_key = _get_fragment_dedupe_key(
            uri, frag_id, output_column, transforms[output_column]
        )
        if dedupe_key in checkpoint_store:
            writer_pbar.update(1)
            return True
        return False

    applier_iter = pool.map_unordered(
        lambda actor, value: actor.run.remote(value),
        # the API says list, but iterables are fine
        filter(lambda task: not _fragment_is_done(task.frag_id), plan),
    )

    writers = {}
    writer_queues: dict[int, ray.util.queue.Queue] = {}
    writer_futs_to_id = bidict.bidict()
    writer_task_cache = {}

    plan.set_description(f"{pbar_prefix} Applying UDFs")

    def _make_writer(frag_id) -> None:
        queue = ray.util.queue.Queue()
        writer = FragmentWriter.remote(
            uri,
            output_column,
            checkpoint_store,
            frag_id,
            queue,
            align_physical_rows=True,
        )
        writer_queues[frag_id] = queue
        writers[frag_id] = writer
        writer_futs_to_id[writer.write.remote()] = frag_id

    def _shutdown_writer(frag_id) -> None:
        actor_handle: ray.actor.ActorHandle = writers[frag_id]
        ray.kill(actor_handle)
        del writers[frag_id]
        writer_queue: ray.util.queue.Queue = writer_queues[frag_id]
        writer_queue.shutdown()
        del writer_queues[frag_id]
        fut = writer_futs_to_id.inverse[frag_id]
        del writer_futs_to_id[fut]

    def _restart_writer(frag_id) -> None:
        while True:
            try:
                _LOG.exception("Failed to commit fragments, restarting writer")
                _shutdown_writer(frag_id)
                _make_writer(frag_id)
                for task in writer_task_cache[frag_id]:
                    writer_queues[frag_id].put(task)
                _LOG.info("Restarted writer for fragment %d", frag_id)
                break
            # we need to keep retrying if our queue gets killed while we are
            # trying to put. There isn't a "safe_put_queue" method because we
            # could stack overflow from
            # _restart_writer -> safe_put_queue -> _restart_writer -> ...
            except (
                ray.exceptions.ActorDiedError,
                ray.exceptions.ActorUnavailableError,
            ):
                continue

    def _commit(frag_id, fut) -> None:
        nonlocal read_version
        _LOG.debug("Committing fragment id: %d", frag_id)

        try:
            fut_frag_id, new_file = ray.get(fut)
            assert fut_frag_id == frag_id
        except (ray.exceptions.ActorDiedError, ray.exceptions.ActorUnavailableError):
            _restart_writer(frag_id)
            return

        operation = lance.LanceOperation.DataReplacement(
            replacements=[
                lance.LanceOperation.DataReplacementGroup(
                    fragment_id=frag_id,
                    new_file=new_file,
                )
            ]
        )

        lance.LanceDataset.commit(uri, operation, read_version=read_version)
        read_version += 1

        _shutdown_writer(frag_id)
        del writer_task_cache[frag_id]

        writer_pbar.update(1)
        dedupe_key = _get_fragment_dedupe_key(
            uri, frag_id, output_column, transforms[output_column]
        )
        checkpoint_store[dedupe_key] = pa.RecordBatch.from_pydict({})

    for item in applier_iter:
        plan.set_description(
            f"{pbar_prefix} workers: {len(pool._future_to_actor)} Applying UDFs"
        )

        task: ReadTask = item[0]
        result = item[1]

        frag_id = task.frag_id
        if frag_id not in writers:
            _LOG.debug("Creating writer for fragment %d", frag_id)
            _make_writer(frag_id)
            writer_task_cache[frag_id] = []

        writer_task_cache[frag_id].append((task.offset, result))
        try:
            writer_queues[frag_id].put((task.offset, result))
        except (ray.exceptions.ActorDiedError, ray.exceptions.ActorUnavailableError):
            _restart_writer(frag_id)
        # save the task result before the fragment is committed
        # in the even the fragment writer fails we can restart it easily

        # FAULT INJECTION: simulate write failure for testing
        if _SIMULATE_WRITE_FAILURE and random.random() < 0.5:
            if random.random() < 0.5:
                ray.kill(writers[frag_id])
            else:
                ray.kill(writer_queues[frag_id].actor)

        ready, _ = ray.wait(list(writer_futs_to_id.keys()), timeout=0)
        for fut in ready:
            frag_id = writer_futs_to_id[fut]
            _commit(frag_id, fut)

    # commit any remaining fragments
    # need to keep retry until all fragments are committed
    while writer_futs_to_id:
        for fut, frag_id in list(writer_futs_to_id.items()):
            _commit(frag_id, fut)
