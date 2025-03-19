# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import tempfile

import pyarrow as pa
import pytest

from geneva.checkpoint import (
    ArrowFsCheckpointStore,
    CheckpointStore,
    InMemoryCheckpointStore,
    LanceCheckpointStore,
)


@pytest.mark.parametrize(
    "store",
    [
        InMemoryCheckpointStore(),
        ArrowFsCheckpointStore(f"{tempfile.mkdtemp()}/new_dir"),
        LanceCheckpointStore(f"{tempfile.mkdtemp()}/new_dir"),
    ],
)
def test_checkpoint(store: CheckpointStore) -> None:
    store["key"] = pa.RecordBatch.from_pydict({"a": [1, 2, 3]})
    assert "key" in store
    assert "key" in list(store.list_keys())
    assert store["key"].to_pydict() == {"a": [1, 2, 3]}
