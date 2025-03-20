# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

from pathlib import Path

import cloudpickle
import lance
import pyarrow as pa
import pyarrow.compute as pc
import pytest

from geneva import InMemoryCheckpointStore, connect, udf
from geneva.apply import LanceRecordBatchUDFApplier, plan_read
from geneva.debug.logger import CheckpointStoreErrorLogger


def test_create_plan(tmp_path: Path) -> None:
    db = connect(tmp_path)
    tbl = db.create_table("tbl", pa.table({"a": [1, 2, 3]}))

    plans = list(plan_read(tbl.uri, batch_size=16))
    assert len(plans) == 1
    plan = plans[0]
    assert plan.uri == tbl.uri
    assert plan.offset == 0
    assert plan.limit == 3


def test_create_plan_with_diverse_shuffle(tmp_path: Path) -> None:
    ds = lance.write_dataset(
        pa.table({"a": range(1024)}), tmp_path / "tbl", max_rows_per_file=16
    )

    plans = list(plan_read(ds.uri, batch_size=1, task_shuffle_diversity=4))
    assert len(plans) == 1024
    plan = plans[0]
    assert plan.uri == ds.uri
    assert plan.offset == 0
    assert plan.limit == 1


@udf(input_columns=["a"])
def one(*args, **kwargs) -> int:
    return 1


def test_applier(tmp_path: Path) -> None:
    db = connect(tmp_path)
    tbl = db.create_table("tbl", pa.table({"a": [1, 2, 3]}))

    plans = list(plan_read(tbl.uri, batch_size=16))
    assert len(plans) == 1
    plan = plans[0]
    assert plan.uri == tbl.uri
    assert plan.offset == 0
    assert plan.limit == 3

    store = InMemoryCheckpointStore()
    applier = LanceRecordBatchUDFApplier(
        udfs={"one": one},
        checkpoint_store=store,
    )
    result = applier.run(plan)
    assert len(result) == 1
    batch = pa.RecordBatch.from_pydict(
        {name: store[key]["data"] for name, key in result.items()}
    )
    assert len(batch) == 3
    assert batch.to_pydict() == {"one": [1, 1, 1]}


@udf()
def errors_on_three(a: int) -> int:
    if a == 3:
        raise ValueError("This is an error")
    return 1


def test_applier_error_logging(tmp_path: Path) -> None:
    db = connect(tmp_path)
    tbl = db.create_table("tbl", pa.table({"a": [1, 2, 3]}))

    plans = list(plan_read(tbl.uri, batch_size=16))
    assert len(plans) == 1
    plan = plans[0]
    assert plan.uri == tbl.uri
    assert plan.offset == 0
    assert plan.limit == 3

    store = InMemoryCheckpointStore()
    error_logger = CheckpointStoreErrorLogger("job_id", store)
    applier = LanceRecordBatchUDFApplier(
        udfs={
            "one": errors_on_three,
        },
        checkpoint_store=store,
        error_logger=error_logger,
    )
    with pytest.raises(RuntimeError):
        applier.run(plan)

    assert len(list(error_logger.list_errors())) == 1
    error_id = list(error_logger.list_errors())[0]
    error = error_logger.get_error_row(error_id).to_pylist()[0]
    assert error["error"] == "This is an error"
    assert error["udf"] == cloudpickle.dumps(errors_on_three)
    assert error["seq"] == 0


def test_plan_with_filter(tmp_path: Path) -> None:
    db = connect(tmp_path)

    tbl = db.create_table("t", pa.table({"a": range(100)}))
    tbl.add(pa.table({"a": range(100, 200)}))
    tbl.add(pa.table({"a": range(200, 300)}))
    tbl.add(pa.table({"a": range(300, 400)}))

    fragments = tbl.get_fragments()
    assert len(fragments) == 4

    tasks = list(plan_read(tbl.uri, filter="a > 100 AND a % 2 == 0"))
    assert len(tasks) == 3


def test_plan_with_row_address(tmp_path: Path) -> None:
    db = connect(tmp_path)

    tbl = db.create_table("t", pa.table({"a": range(100)}))

    fragments = tbl.get_fragments()
    assert len(fragments) == 1

    tasks = list(plan_read(tbl.uri))
    assert len(tasks) == 1

    for batch in tasks[0].to_batches():
        assert "_rowaddr" in batch.column_names


def test_udf_with_arrow_params(tmp_path: Path) -> None:
    @udf(data_type=pa.int32())
    def batch_udf(a: pa.Array, b: pa.Array) -> pa.Array:
        assert a == pa.array([1, 2, 3])
        assert b == pa.array([4, 5, 6])
        return pc.add(a, b)

    db = connect(tmp_path)
    tbl = db.create_table("t", pa.table({"a": [1, 2, 3], "b": [4, 5, 6]}))

    store = InMemoryCheckpointStore()
    applier = LanceRecordBatchUDFApplier(
        udfs={
            "c": batch_udf,
        },
        checkpoint_store=store,
    )
    result = applier.run(next(plan_read(tbl.uri, batch_size=16)))
    assert len(result) == 1
    batch = pa.RecordBatch.from_pydict(
        {name: store[key]["data"] for name, key in result.items()}
    )
    assert batch == pa.RecordBatch.from_pydict(
        {"c": pa.array([5, 7, 9], type=pa.int32())},
    )
