# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import itertools
from pathlib import Path
from typing import Any

import lance
import pyarrow as pa
import pytest

from geneva import LanceCheckpointStore, udf

try:
    from geneva.runners.dataflow.dataflow import (
        DataflowOptions,
        run_dataflow_add_column,
    )
except ImportError:
    pytest.skip("failed to import geneva.runners.dataflow", allow_module_level=True)


@udf(data_type=pa.int32(), batch_size=8)
def add_one(a) -> int:
    return a + 1


@pytest.mark.parametrize(
    "shuffle_config",
    [
        {
            "batch_size": batch_size,
            "shuffle_buffer_size": shuffle_buffer_size,
            "task_shuffle_diversity": task_shuffle_diversity,
        }
        for (
            batch_size,
            shuffle_buffer_size,
            task_shuffle_diversity,
        ) in itertools.product(
            range(1, 5),
            [0, 1, 3, 16],
            [None, 1, 3, 16],
        )
    ],
)
def test_run_dataflow_add_column(
    tmp_path: Path, shuffle_config: dict[str, Any]
) -> None:
    data = {"a": pa.array(range(1024))}
    tbl = pa.Table.from_pydict(data)
    ckp_store = LanceCheckpointStore(str(tmp_path / "ckp"))

    tbl_path = tmp_path / "foo.lance"
    ds = lance.write_dataset(tbl, tbl_path, max_rows_per_file=16)

    def return_none(batch: pa.RecordBatch) -> pa.RecordBatch:
        return pa.RecordBatch.from_pydict(
            {"b": pa.array([None] * batch.num_rows, pa.int32())}
        )

    new_frags = []
    new_schema = None
    for frag in ds.get_fragments():
        new_fragment, new_schema = frag.merge_columns(return_none, columns=["a"])
        new_frags.append(new_fragment)

    assert new_schema is not None
    merge = lance.LanceOperation.Merge(new_frags, new_schema)
    lance.LanceDataset.commit(tbl_path, merge, read_version=ds.version)

    run_dataflow_add_column(
        str(tbl_path),
        ["a"],
        {"b": add_one},
        ckp_store,
        DataflowOptions(
            runner="DirectRunner",
        ),
        test_run=False,
        **shuffle_config,
    ).result.wait_until_finish()

    ds = lance.dataset(tbl_path)

    assert ds.to_table().to_pydict() == {
        "a": list(range(1024)),
        "b": [x + 1 for x in range(1024)],
    }


def test_dataflow_runner_test_run(tmp_path: Path) -> None:
    data = {"a": pa.array(range(100))}
    tbl = pa.Table.from_pydict(data)
    ckp_store = LanceCheckpointStore(str(tmp_path / "ckp"))

    tbl_path = tmp_path / "foo.lance"
    # do it twice to have two fragments
    ds = lance.write_dataset(tbl, tbl_path)

    data = {"a": pa.array(range(100, 200))}
    tbl = pa.Table.from_pydict(data)
    ds = lance.write_dataset(tbl, tbl_path, mode="append")

    def return_none(batch: pa.RecordBatch) -> pa.RecordBatch:
        return pa.RecordBatch.from_pydict(
            {"b": pa.array([None] * batch.num_rows, pa.int32())}
        )

    new_frags = []
    new_schema = None
    for frag in ds.get_fragments():
        new_fragment, new_schema = frag.merge_columns(return_none, columns=["a"])
        new_frags.append(new_fragment)

    assert new_schema is not None
    merge = lance.LanceOperation.Merge(new_frags, new_schema)
    lance.LanceDataset.commit(tbl_path, merge, read_version=ds.version)

    run_dataflow_add_column(
        str(tbl_path),
        ["a"],
        {"b": add_one},
        ckp_store,
        DataflowOptions(
            runner="DirectRunner",
        ),
        batch_size=8,
        test_run=True,
    ).result.wait_until_finish()

    ds = lance.dataset(tbl_path)

    assert ds.to_table().to_pydict() == {
        "a": list(range(200)),
        "b": [x + 1 for x in range(100)] + [None] * 100,
    }
