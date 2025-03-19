# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

# Use lance lake with Google Dataflow

import logging
import os
import re
import uuid
from collections.abc import Callable, Iterator

import more_itertools

from geneva import DockerWorkspacePackager

try:
    import apache_beam as beam
    from apache_beam.internal import pickler
    from apache_beam.options.pipeline_options import (
        GoogleCloudOptions,
        PipelineOptions,
        SetupOptions,
        StandardOptions,
    )
    from apache_beam.pipeline import Pipeline
    from apache_beam.transforms.combiners import Top
except ImportError as err:
    raise ImportError(
        "apache_beam is required for this module, pip install geneva[dataflow]",
    ) from err


import attrs
import lance
import lance.commit
import pyarrow as pa

from geneva.apply import LanceRecordBatchUDFApplier, plan_read
from geneva.checkpoint import CheckpointStore
from geneva.debug.logger import CheckpointStoreErrorLogger
from geneva.runners.dataflow.reshuffle import ReshuffleByFragmentChunks
from geneva.transformer import UDF

_LOG = logging.getLogger(__name__)


@attrs.define
class DataflowOptions:
    """Dataflow Options"""

    runner: str = attrs.field(
        default="DataflowRunner",
    )
    region: str = attrs.field(
        default="us-central1",
    )
    project: str = attrs.field(
        default=os.environ.get("GENEVA_DATAFLOW_PROJECT", ""),
    )
    temp_location: str = attrs.field(
        default=os.environ.get(
            "GENEVA_DATAFLOW_TEMP_LOCATION",
            f"{os.environ.get('GENEVA_DATAFLOW_GCS', '')}/temp",
        ),
    )
    staging_location: str = attrs.field(
        default=os.environ.get(
            "GENEVA_DATAFLOW_STAGING_LOCATION",
            f"{os.environ.get('GENEVA_DATAFLOW_GCS', '')}/staging",
        ),
    )
    docker_image: str | None = attrs.field(
        default=os.environ.get("GENEVA_DATAFLOW_DOCKER_IMAGE"),
    )
    disk_size_gb: int = attrs.field(
        default=100,
    )
    machine_type: str = attrs.field(
        default=os.environ.get("GENEVA_DATAFLOW_MACHINE_TYPE", "n2-highmem-16"),
    )

    _GPU_MACHINES = [
        "g2",  # L4
        # "a2", disallow A100 for now
        # "a3", disallow H100 for now
    ]

    _ARM_MACHINES = [
        "c4a",
    ]

    _X86_MACHINES = [
        "n2",
        "c3",
        "c3d",
        "c4",
    ]

    _ALL_MACHINES = _GPU_MACHINES + _ARM_MACHINES + _X86_MACHINES

    @property
    def is_arm(self) -> bool:
        return any(
            self.machine_type.startswith(f"{machine}-")
            for machine in self._ARM_MACHINES
        )

    @machine_type.validator
    def _validate_machine_type(self, attribute, value) -> None:
        if not any(value.startswith(f"{machine}-") for machine in self._ALL_MACHINES):
            raise ValueError(
                f"machine_type must start with one of {self._ALL_MACHINES}"
            )

    @property
    def is_cuda(self) -> bool:
        return any(
            self.machine_type.startswith(f"{machine}-")
            for machine in self._GPU_MACHINES
        )

    @property
    def additional_options(self) -> list[str]:
        if self.is_cuda:
            return [
                # enable GPU
                "--dataflow_service_options=worker_accelerator=type:nvidia-l4;count:1;install-nvidia-driver;use_nvidia_mps",
                # make sure we don't spin up tons of containers and waste memory
                "--experiments=no_use_multiple_sdk_containers",
            ]
        if self.runner in {"DirectRunner", "direct"}:
            return [
                "--direct_num_workers=0",
                "--direct_running_mode=multi_threading",
            ]
        return []


def map_with_value(  # noqa: ANN201
    fn: Callable,
):
    def _wrapped(x):  # noqa: ANN202
        return x, fn(x)

    return _wrapped


def extract_frag_id_as_key(x):  # noqa: ANN201
    return x[0].frag_id, x


def write_fragment(  # noqa: ANN201
    uri: str,
    column_name: str,
    store: CheckpointStore,
):
    dataset = lance.dataset(uri)
    # MASSIVE HACK: open up an API to get the field id from the column name
    field_id = re.compile(rf'name: "{column_name}", id: (?P<field_id>[\d]*),').findall(
        str(dataset.lance_schema)
    )
    assert len(field_id) == 1
    field_id = int(field_id[0])

    def _write_fragment(x):  # noqa: ANN202
        frag_id, checkpoint_keys = x
        _LOG.info("Writing fragment %s, with %d keys", frag_id, len(checkpoint_keys))
        batches: list[dict[str, str]] = list(checkpoint_keys)

        def _iter() -> Iterator[pa.RecordBatch]:
            for batch in batches:
                res = {key: store[value]["data"] for key, value in batch.items()}
                yield pa.RecordBatch.from_pydict(res)

        it = more_itertools.peekable(_iter())
        rbr = pa.RecordBatchReader.from_batches(it.peek().schema, it)

        # TODO: this doesn't support struct or complex schema yet
        new_data = lance.fragment.write_fragments(
            rbr,
            uri,
            max_rows_per_file=1 << 31,
            max_bytes_per_file=1 << 40,
        )

        assert len(new_data) == 1
        new_data = new_data[0]
        assert len(new_data.files) == 1
        new_datafile = new_data.files[0]

        new_datafile.fields = [field_id]
        new_datafile.column_indices = [0]

        return frag_id, new_datafile

    return _write_fragment


def sort_and_collect_batch(x):  # noqa: ANN201
    (frag_id, data) = x
    _LOG.info("Sorting %d keys for frag: %s", len(data), frag_id)
    data = list(data)
    data.sort(key=lambda x: x[0].offset)

    return frag_id, [x[1] for x in data]


def commit_fragments(  # noqa: ANN201
    uri: str,
    version: int,
):
    def _commit_fragments(x) -> None:
        _LOG.info("Committing %d fragments", len(x))
        operation = lance.LanceOperation.DataReplacement(
            replacements=[
                lance.LanceOperation.DataReplacementGroup(
                    fragment_id=fragment_id,
                    new_file=new_file,
                )
                for (fragment_id, new_file) in x
            ]
        )
        lance.LanceDataset.commit(uri, operation, read_version=version)

    return _commit_fragments


def run_dataflow_add_column(
    uri: str,
    columns: list[str],
    transforms: dict[str, UDF],
    checkpoint_store: CheckpointStore,
    dataflow_options: DataflowOptions,
    /,
    job_id: str | None = None,
    batch_size: int = 512,
    read_version: int | None = None,
    test_run: bool = True,
    **kwargs,
) -> Pipeline | None:
    is_cuda = any(udf.cuda for udf in transforms.values())

    if is_cuda and not dataflow_options.is_cuda:
        _LOG.info(
            "CUDA UDFs detected, but dataflow machine type is not cuda,"
            " setting machine type to use L4 GPU"
        )
        dataflow_options.machine_type = "g2-standard-8"

    if (
        dataflow_options.docker_image is None
        and dataflow_options.runner == "DataflowRunner"
    ):
        _LOG.warning("No docker image specified, building one")
        tag = uuid.uuid4().hex
        packager = DockerWorkspacePackager(**kwargs)
        docker_image = packager.build(tag, platform="linux/amd64", cuda=is_cuda)
        packager.push(tag)
    else:
        docker_image = dataflow_options.docker_image

    pipeline_args = [
        "--runner",
        dataflow_options.runner,
        "--project",
        dataflow_options.project,
        "--region",
        dataflow_options.region,
        "--temp_location",
        dataflow_options.temp_location,
        "--staging_location",
        dataflow_options.staging_location,
        "--experiments=use_runner_v2",
        "--dataflow_service_options=enable_dynamic_thread_scaling",
        # we use flexrs, meaning we enable dataflow shuffle service
        # we don't need a lot of disk space
        "--disk_size_gb=75",
        # TODO: DO NOT HARDCODE HARDWARE CONFIG
        "--machine_type=" + dataflow_options.machine_type,
        "--flexrs_goal=SPEED_OPTIMIZED",
        "--max_num_workers=1024",
        "--dataflow_service_options=min_num_workers=4",
        *dataflow_options.additional_options,
    ]
    if dataflow_options.runner == "DataflowRunner":
        if docker_image is None:
            raise ValueError("Docker image must be specified for DataflowRunner")
        pipeline_args += ["--sdk_container_image=" + docker_image]

    try:
        import prefect
        from prefect.exceptions import MissingContextError

        try:
            job_id = job_id or prefect.context.get_run_context().flow_run.id.hex
            _LOG.info("Using prefect job id: %s", job_id)
        except MissingContextError:
            job_id = None
    except ImportError:
        job_id = None

    job_id = job_id or uuid.uuid4().hex

    # We use the save_main_session option because one or more DoFn's in this
    # workflow rely on global context (e.g., a module imported at module level).
    pipeline_options = PipelineOptions(pipeline_args)
    # we usually submit from a local environment, don't want save the main session
    pipeline_options.view_as(SetupOptions).save_main_session = False
    # always use cloudpickle
    pipeline_options.view_as(SetupOptions).pickle_library = pickler.USE_CLOUDPICKLE
    # otherwise __exit__ will wait for the job to finish
    pipeline_options.view_as(StandardOptions).no_wait_until_finish = True
    # set the job name

    applier = LanceRecordBatchUDFApplier(
        udfs=transforms,
        checkpoint_store=checkpoint_store,
        error_logger=CheckpointStoreErrorLogger(job_id, checkpoint_store),
    )

    if read_version is None:
        read_version = lance.dataset(uri).version

    output_column = list(transforms.keys())[0]

    table_name = uri.split("/")[-1].split(".")[0]
    name = f"{table_name}-{output_column}-{job_id[:8]}"
    pipeline_options.view_as(GoogleCloudOptions).job_name = name.replace("_", "-")
    # The pipeline will be run on exiting the with block.
    with Pipeline(options=pipeline_options) as p:
        pcol = (
            p
            | beam.Create([None])
            | "CreateTasks"
            >> beam.FlatMap(
                lambda _: plan_read(uri, columns, batch_size=batch_size, **kwargs)
            )
        )

        if test_run:
            pcol = (
                pcol
                | "ExtractFragIDForSample" >> beam.Map(lambda x: (x.frag_id, x))
                | "GroupByFragIDForSample" >> beam.GroupByKey()
                | "TakeSmallestFragID" >> Top.Smallest(1)
                | beam.FlatMap(lambda x: x[0][1])
            )

        pcol = (
            pcol
            | ReshuffleByFragmentChunks()
            | "Apply UDFs" >> beam.Map(map_with_value(applier.run))
            | "ExtractFragID" >> beam.Map(extract_frag_id_as_key)
            | "GroupByKey" >> beam.GroupByKey()
            | "SortAndCollectBatch" >> beam.Map(sort_and_collect_batch)
            | "WriteFragments"
            >> beam.Map(write_fragment(uri, output_column, checkpoint_store))
            | "Collect" >> beam.combiners.ToList()
            | "Commit" >> beam.Map(commit_fragments(uri, read_version))
        )

    return p
