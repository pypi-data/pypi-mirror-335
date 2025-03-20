# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import itertools
from pathlib import Path

import lance
import pyarrow as pa
import pytest

from geneva import LanceCheckpointStore, udf

try:
    from geneva.runners.ray.pipeline import _simulate_write_failure, run_ray_add_column
except ImportError:
    import pytest

    pytest.skip("failed to import geneva.runners.ray", allow_module_level=True)


def make_new_ds(tbl_path: Path) -> None:
    data = {"a": pa.array(range(256))}
    tbl = pa.Table.from_pydict(data)

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


# 0.1 cpu so we don't wait for provisioning in the tests
@udf(data_type=pa.int32(), batch_size=8, num_cpus=0.1)
def add_one(a) -> int:
    return a + 1


@pytest.mark.parametrize(
    "shuffle_config",
    [
        {
            "applier_batch_size": applier_batch_size,
            "batch_size": batch_size,
            "shuffle_buffer_size": shuffle_buffer_size,
            "task_shuffle_diversity": task_shuffle_diversity,
        }
        for (
            applier_batch_size,
            batch_size,
            shuffle_buffer_size,
            task_shuffle_diversity,
        ) in itertools.product(
            [2, 3],
            [1, 2, 3],
            [0, 3, 16],
            [None, 1, 3],
        )
    ],
)
def test_run_ray_add_column(tmp_path: Path, shuffle_config) -> None:
    tbl_path = tmp_path / "foo.lance"
    make_new_ds(tbl_path)

    ckp_store = LanceCheckpointStore(str(tmp_path / "ckp"))
    run_ray_add_column(
        str(tbl_path),
        ["a"],
        {"b": add_one},
        checkpoint_store=ckp_store,
        **shuffle_config,
    )

    ds = lance.dataset(tbl_path)
    assert ds.to_table().to_pydict() == {
        "a": list(range(256)),
        "b": [x + 1 for x in range(256)],
    }


@pytest.mark.parametrize("_", range(16))
def test_run_ray_add_column_write_fault(_: int, tmp_path: Path) -> None:  # noqa: PT019
    tbl_path = tmp_path / "foo.lance"
    make_new_ds(tbl_path)

    ckp_store = LanceCheckpointStore(str(tmp_path / "ckp"))

    with _simulate_write_failure(True):
        run_ray_add_column(
            str(tbl_path), ["a"], {"b": add_one}, checkpoint_store=ckp_store
        )

    ds = lance.dataset(tbl_path)
    assert ds.to_table().to_pydict() == {
        "a": list(range(256)),
        "b": [x + 1 for x in range(256)],
    }


def test_run_ray_add_column_with_deletes(tmp_path: Path) -> None:  # noqa: PT019
    tbl_path = tmp_path / "foo.lance"
    make_new_ds(tbl_path)

    ds = lance.dataset(tbl_path)
    ds.delete("a % 2 == 1")

    ckp_store = LanceCheckpointStore(str(tmp_path / "ckp"))

    run_ray_add_column(str(tbl_path), ["a"], {"b": add_one}, checkpoint_store=ckp_store)

    ds = lance.dataset(tbl_path)
    assert ds.to_table().to_pydict() == {
        "a": list(range(0, 256, 2)),
        "b": [x + 1 for x in range(0, 256, 2)],
    }
