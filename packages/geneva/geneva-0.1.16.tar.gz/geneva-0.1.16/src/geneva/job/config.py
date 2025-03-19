import attrs

from geneva.checkpoint import CheckpointConfig, CheckpointStore
from geneva.config import ConfigBase


@attrs.define
class JobConfig(ConfigBase):
    checkpoint: CheckpointConfig = attrs.field(default=CheckpointConfig("in_memory"))

    batch_size: int = attrs.field(default=10240, converter=int)

    task_shuffle_diversity: int = attrs.field(default=8, converter=int)

    # TODO: infer this from UDF and runtime memory directly
    applier_batch_size: int = attrs.field(default=1024, converter=int)

    @classmethod
    def name(cls) -> str:
        return "job"

    def make_checkpoint_store(self) -> CheckpointStore:
        return (self.checkpoint or CheckpointConfig("in_memory")).make()
