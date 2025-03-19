# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

# reshuffle tasks by fragment ID and batch them together

import apache_beam as beam
from apache_beam import PTransform, pvalue, typehints
from apache_beam.runners.pipeline_context import PipelineContext

from geneva.apply import ReadTask

_MAX_BUCKET_SIZE = 8192


@typehints.with_input_types(ReadTask)
@typehints.with_output_types(ReadTask)
class ReshuffleByFragmentChunks(PTransform):
    """
    Reshuffle tasks by fragment ID and batch them together.
    """

    _URN = "LanceShuffleByFragmentChunks"

    def __init__(self, bucket_size=_MAX_BUCKET_SIZE) -> None:
        self.bucket_size = bucket_size

    def expand(
        self,
        input_or_inputs: pvalue.PValue,
    ) -> pvalue.PCollection:
        return (
            input_or_inputs
            | "AddFragIDandChunkIdKey"
            >> beam.Map(lambda x: ((x.frag_id, x.offset // self.bucket_size), x))
            | "GroupByFragIDandChunkId" >> beam.GroupByKey()
            | "ExtractTask" >> beam.FlatMap(lambda x: x[1])
        )  # type: ignore

    def to_runner_api_parameter(
        self,
        unused_context: PipelineContext,
    ) -> tuple[str, None]:
        return self._URN, None

    @staticmethod
    @PTransform.register_urn(_URN, None)
    def from_runner_api_parameter(
        unused_ptransform,
        unused_parameter,
        unused_context,
    ) -> "ReshuffleByFragmentChunks":
        return ReshuffleByFragmentChunks()
