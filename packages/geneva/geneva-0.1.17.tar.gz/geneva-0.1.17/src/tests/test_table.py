# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

from pathlib import Path

import pyarrow as pa
from pyarrow.fs import FileSystem, FileType

from geneva import connect, udf
from geneva.packager import DockerUDFPackager


def test_add_virtual_column(tmp_path: Path) -> None:
    db = connect(tmp_path)

    # create a basic table
    tbl = pa.Table.from_pydict({"id": [1, 2, 3, 4, 5, 6]})
    table = db.create_table("table1", tbl)

    @udf(data_type=pa.int64())
    def double_id(id: int):  # noqa A002
        return id * 2

    table.add_columns(
        {"id2": double_id},
        packager=DockerUDFPackager(
            # use prebuilt image tag so we don't have to build the image
            prebuilt_docker_img="test-image:latest"
        ),
    )

    schema = table.schema

    assert len(schema) == 2
    field = schema.field("id2")
    assert field is not None
    assert field.type == pa.int64()

    assert len(field.metadata) == 4
    assert field.metadata[b"virtual_column"] == b"true"
    assert field.metadata[b"virtual_column.udf_backend"] == b"DockerUDFSpecV1"
    assert field.metadata[b"virtual_column.udf_name"] == b"double_id"

    # check that the UDF was actually uploaded
    fs, root_path = FileSystem.from_uri(f"{str(tmp_path)}/table1.lance")
    file_info = fs.get_file_info(
        f"{root_path}/{field.metadata[b'virtual_column.udf'].decode('utf-8')}"
    )
    assert file_info.type is not FileType.NotFound


def test_alter_virtual_column(tmp_path: Path) -> None:
    db = connect(tmp_path)

    # create a basic table
    tbl = pa.Table.from_pydict({"id": [1, 2, 3, 4, 5, 6]})
    table = db.create_table("table1", tbl)

    @udf(data_type=pa.int64())
    def double_id(id: int):  # noqa A002
        return id * 2

    table.add_columns(
        {"id2": double_id},
        packager=DockerUDFPackager(
            # use prebuilt image tag so we don't have to build the image
            prebuilt_docker_img="test-image:latest"
        ),
    )

    schema = table.schema
    field = schema.field("id2")
    assert field.metadata[b"virtual_column.udf_name"] == b"double_id"

    # now check that we can replace the UDF with a new version:
    @udf(data_type=pa.int64())
    def triple_id(id: int):  # noqa A002
        return id * 3

    table.alter_columns(
        *[
            {
                "path": "id2",
                "virtual_column": triple_id,
                "packager": DockerUDFPackager(prebuilt_docker_img="test-image:latest"),
            }
        ]
    )

    schema = table.schema
    field = schema.field("id2")
    assert field.metadata[b"virtual_column"] == b"true"
    assert field.metadata[b"virtual_column.udf_name"] == b"triple_id"
    assert field.metadata[b"virtual_column.udf_backend"] == b"DockerUDFSpecV1"

    # check that the UDF was actually uploaded
    fs, root_path = FileSystem.from_uri(f"{str(tmp_path)}/table1.lance")
    file_info = fs.get_file_info(
        f"{root_path}/{field.metadata[b'virtual_column.udf'].decode('utf-8')}"
    )
    assert file_info.type is not FileType.NotFound
