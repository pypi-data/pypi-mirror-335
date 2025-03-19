# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import hashlib
import logging
import os
import uuid
from collections.abc import Iterable, Iterator
from datetime import timedelta
from functools import cached_property
from typing import Any, Literal

import cloudpickle
import lance
import lancedb
import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
from lancedb.common import VECTOR_COLUMN_NAME
from lancedb.index import IndexConfig
from lancedb.query import LanceQueryBuilder
from lancedb.query import Query as LanceQuery
from lancedb.table import IndexStatistics
from lancedb.table import LanceTable as LanceLocalTable
from lancedb.table import Table as LanceTable
from pyarrow.fs import FileSystem, LocalFileSystem

# Python 3.10 compatibility
from typing_extensions import Never, override  # noqa: UP035

from geneva.db import Connection
from geneva.docker.packager import DockerWorkspacePackager
from geneva.packager import DockerUDFPackager, UDFPackager
from geneva.transformer import UDF
from geneva.utils.arrow import datafusion_type_name

_LOG = logging.getLogger(__name__)


class Table(LanceTable):
    """Table in Geneva.

    A Table is a Lance dataset
    """

    def __init__(
        self,
        conn: Connection,
        name: str,
        *,
        version: int | None = None,
        storage_options: dict[str, str] | None = None,
        index_cache_size: int | None = None,
        **kwargs,
    ) -> None:
        self._conn_uri = conn.uri
        self._name = name

        self._conn = conn

        base_uri = conn._uri.removesuffix("/")
        self._uri = f"{base_uri}/{name}.lance"
        self._version: int | None = version
        self._index_cache_size = index_cache_size
        self._storage_options = storage_options

        # Load table
        self._ltbl  # noqa

    def __repr__(self) -> str:
        return f"<Table {self._name}>"

    # TODO: This annotation sucks
    def __reduce__(self):  # noqa: ANN204
        return (self.__class__, (self._conn, self._name))

    def get_fragments(self) -> list[lance.LanceFragment]:
        return self._ltbl.to_lance().get_fragments()

    @cached_property
    def _ltbl(self) -> lancedb.table.Table:
        # remote db, open table directly
        if self._conn_uri.startswith("db://"):
            tbl = self._conn._connect.open_table(self._name)
            if self._version:
                tbl.checkout(self._version)
            return tbl

        # object store db, open table from file
        view_file_path = os.path.join(self._uri, "view.json")
        fs, path = pa.fs.FileSystem.from_uri(view_file_path)
        file_info = fs.get_file_info(path)
        if file_info.type == pa.fs.FileType.NotFound:
            tbl = self._conn._connect.open_table(self._name)
            if self._version:
                tbl.checkout(self._version)
            return tbl

        fs, parent_dir = pa.fs.FileSystem.from_uri(self._uri)
        fs.create_dir(parent_dir, recursive=True)
        with fs.open_input_file(path) as f:
            q_json = f.read().decode("utf-8")
            from .query import Query

            return Query.from_dict(q_json)

    @property
    def name(self) -> str:
        """Get the name of the table."""
        return self._name

    @property
    def version(self) -> int:
        """Get the current version of the table"""
        return self._ltbl.version

    @property
    def schema(self) -> pa.Schema:
        """The Arrow Schema of the Table."""
        return self._ltbl.schema

    @property
    def uri(self) -> str:
        return self._uri

    @property
    def embedding_functions(self) -> Never:
        raise NotImplementedError("Embedding functions are not supported.")

    def add(
        self,
        data,
        mode: str = "append",
        on_bad_vectors: str = "error",
        fill_value: float = 0.0,
    ) -> None:
        self._ltbl.add(
            data,
            mode=mode,
            on_bad_vectors=on_bad_vectors,
            fill_value=fill_value,
        )

    def checkout(self, version: int) -> None:
        self._version = version
        self._ltbl.checkout(version)

    def checkout_latest(self) -> None:
        self._ltbl.checkout_latest()

    def add_columns(
        self,
        mapping: dict[str, UDF],
        *,
        input_columns: list[str] | None = None,
        packager: UDFPackager | None = None,
        **kwargs,
    ) -> None:
        if len(mapping) != 1:
            raise ValueError("Only one UDF is supported for now.")

        _LOG.info("Adding column: udf=%s", mapping)
        col_name = next(iter(mapping))
        udf = mapping[col_name]

        # TODO -- eventually we need to support more different types via SQL
        # or have another way to pass more complex types into this
        self._ltbl.add_columns(
            {col_name: f"CAST(NULL as {datafusion_type_name(udf.data_type)})"}
        )

        packager = packager or DockerUDFPackager()
        self._configure_virtual_column(col_name, udf, packager)

    def alter_columns(self, *alterations: Iterable[dict[str, Any]]) -> None:
        basic_column_alterations = []
        for alter in alterations:
            if "virtual_column" in alter:
                if "path" not in alter:
                    raise ValueError("path is required to alter virtual virtual_column")
                if not isinstance(alter["virtual_column"], UDF):
                    raise ValueError("virtual_column must be a UDF")

                if "packager" not in alter:
                    packager = DockerUDFPackager()
                else:
                    packager = alter["packager"]
                    if not isinstance(packager, UDFPackager):
                        raise ValueError("packager must be a UDFPackager")

                col_name = alter["path"]
                udf = alter["virtual_column"]

                self._configure_virtual_column(col_name, udf, packager)

            else:
                basic_column_alterations.append(alter)

        if len(basic_column_alterations) > 0:
            self._ltbl.alter_columns(*basic_column_alterations)

    def package_udf(self, col_name: str, udf: UDF) -> tuple[str, bytes]:
        image_tag = uuid.uuid4().hex

        packager = DockerWorkspacePackager()
        _LOG.info("Building UDF image: %s", image_tag)
        image_name = packager.build(image_tag, platform="linux/amd64", cuda=udf.cuda)
        _LOG.info("Pushing UDF image: %s", image_tag)
        packager.push(image_tag)
        _LOG.info("Pushed UDF image: %s", image_tag)

        udf_pickle = cloudpickle.dumps(udf)

        return (image_name, udf_pickle)

    def _configure_virtual_column(
        self,
        col_name: str,
        udf: UDF,
        packager: UDFPackager,
    ) -> None:
        """
        Configure a column to be a virtual column for the given UDF.

        This procedure includes:
        - Packaging the UDF
        - Uploading the UDF to the dataset
        - Updating the field metadata to include the UDF information

        Note that the column should already exist on the table.
        """
        udf_spec = packager.marshal(udf)

        # upload the UDF to the dataset URL
        if not isinstance(self._ltbl, LanceLocalTable):
            raise TypeError(
                "adding udf column is currently only supported for local tables"
            )

        # upload the packaged UDF to some location inside the dataset:
        ds = self._ltbl.to_lance()
        fs, root_uri = FileSystem.from_uri(ds.uri)
        checksum = hashlib.sha256(udf_spec.udf_payload).hexdigest()
        udf_location = f"_udfs/{checksum}"

        # TODO -- only upload the UDF if it doesn't exist
        if isinstance(fs, LocalFileSystem):
            # Object storage filesystems like GCS and S3 will create the directory
            # automatically, but local filesystem will not, so we create explicitly
            fs.create_dir(f"{root_uri}/_udfs")

        with fs.open_output_stream(f"{root_uri}/{udf_location}") as f:
            f.write(udf_spec.udf_payload)

        field_metadata = {
            "virtual_column": "true",
            "virtual_column.udf_backend": udf_spec.backend,
            "virtual_column.udf_name": udf_spec.name,
            "virtual_column.udf": "_udfs/" + checksum,
        }

        # Add the column metadata:
        self._ltbl.replace_field_metadata(col_name, field_metadata)

    def create_index(
        self,
        metric: str = "L2",
        num_partitions: int | None = None,
        num_sub_vectors: int | None = None,
        vector_column_name: str = VECTOR_COLUMN_NAME,
        replace: bool = True,
        accelerator=None,
        index_cache_size=None,
        *,
        index_type: Literal[
            "IVF_FLAT",
            "IVF_PQ",
            "IVF_HNSW_SQ",
            "IVF_HNSW_PQ",
        ] = "IVF_PQ",
        num_bits: int = 8,
        max_iterations: int = 50,
        sample_rate: int = 256,
        m: int = 20,
        ef_construction: int = 300,
    ) -> None:
        """Create Vector Index"""
        self._ltbl.create_index(
            metric,
            num_partitions or 256,
            num_sub_vectors or 96,
            vector_column_name,
            replace,
            accelerator,
            index_cache_size,
            index_type=index_type,
            num_bits=num_bits,
            max_iterations=max_iterations,
            sample_rate=sample_rate,
            m=m,
            ef_construction=ef_construction,
        )

    @override
    def create_fts_index(
        self,
        field_names: str | list[str],
        ordering_field_names: str | list[str] | None = None,
        *,
        replace: bool = False,
        writer_heap_size: int | None = None,
        tokenizer_name: str | None = None,
        with_position: bool = True,
        base_tokenizer: Literal["simple", "raw", "whitespace"] = "simple",
        language: str = "English",
        max_token_length: int | None = 40,
        lower_case: bool = True,
        stem: bool = False,
        remove_stop_words: bool = False,
        ascii_folding: bool = False,
        **_kwargs,
    ) -> None:
        self._ltbl.create_fts_index(
            field_names,
            ordering_field_names,  # type: ignore
            replace=replace,
            writer_heap_size=writer_heap_size,
            tokenizer_name=tokenizer_name,
            with_position=with_position,
            base_tokenizer=base_tokenizer,
            language=language,
            max_token_length=max_token_length,
            lower_case=lower_case,
            stem=stem,
            remove_stop_words=remove_stop_words,
            ascii_folding=ascii_folding,
        )

    @override
    def create_scalar_index(
        self,
        column: str,
        *,
        replace: bool = True,
        index_type: Literal["BTREE", "BITMAP", "LABEL_LIST"] = "BTREE",
    ) -> None:
        self._ltbl.create_scalar_index(
            column,
            replace=replace,
            index_type=index_type,
        )

    @override
    def _do_merge(self, other: "Table", on: list[str], how: str) -> Never:
        raise NotImplementedError("Merging tables is not supported.")

    @override
    def _execute_query(
        self,
        query: LanceQuery,
        batch_size: int | None = None,
    ) -> pa.RecordBatchReader:
        return self._ltbl._execute_query(query, batch_size=batch_size)

    def list_versions(self) -> list[dict[str, Any]]:
        return self._ltbl.list_versions()

    @override
    def cleanup_old_versions(
        self,
        older_than: timedelta | None = None,
        *,
        delete_unverified=False,
    ) -> "lance.CleanupStats":
        return self._ltbl.cleanup_old_versions(
            older_than,
            delete_unverified=delete_unverified,
        )

    def to_batches(self, batch_size: int | None = None) -> Iterator[pa.RecordBatch]:
        from .query import Query

        if isinstance(self._ltbl, Query):
            return self._ltbl.to_batches(batch_size)
        return self._ltbl.to_lance().to_batches(batch_size)

    def scanner(
        self,
        columns: list[str] | dict[str, str] | None = None,
        filter: str | pc.Expression | None = None,  # noqa: A002
        limit: int | None = None,
        offset: int | None = None,
        batch_size: int | None = None,
        batch_readahead: int | None = None,
        fragment_readahead: int | None = None,
        scan_in_order: bool | None = None,
        *,
        with_row_id: bool | None = None,
        with_row_address: bool | None = None,
        use_stats: bool | None = None,
        fast_search: bool | None = None,
        io_buffer_size: int | None = None,
        late_materialization: bool | list[str] | None = None,
        use_scalar_index: bool | None = None,
        **kwargs,
    ) -> lance.LanceScanner | Iterator[pa.RecordBatch]:
        from .query import Query

        if isinstance(self._ltbl, Query):
            return self._ltbl.to_batches()

        return self._ltbl.to_lance().scanner(
            columns=columns,
            filter=filter,
            limit=limit,
            offset=offset,
            batch_size=batch_size,
            batch_readahead=batch_readahead,
            fragment_readahead=fragment_readahead,
            scan_in_order=scan_in_order,
            with_row_id=with_row_id,
            with_row_address=with_row_address,
            use_stats=use_stats,
            fast_search=fast_search,
            io_buffer_size=io_buffer_size,
            late_materialization=late_materialization,
            use_scalar_index=use_scalar_index,
        )

    def search(
        self,
        query: list | pa.Array | pa.ChunkedArray | np.ndarray | None = None,
        vector_column_name: str | None = None,
        query_type: Literal["vector", "fts", "hybrid", "auto"] = "auto",
        ordering_field_name: str | None = None,
        fts_columns: str | list[str] | None = None,
    ) -> LanceQueryBuilder:
        return self._ltbl.search(
            query=query,
            vector_column_name=vector_column_name,
            query_type=query_type,
            fts_columns=fts_columns,
        )

    @override
    def drop_columns(self, columns: Iterable[str]) -> None:
        self._ltbl.drop_columns(columns)

    @override
    def to_arrow(self) -> pa.Table:
        return self._ltbl.to_arrow()

    @override
    def count_rows(self, filter: str | None = None) -> int:
        return self._ltbl.count_rows(filter)

    @override
    def update(
        self,
        where: str | None = None,
        values: dict | None = None,
        *,
        values_sql: dict[str, str] | None = None,
    ) -> None:
        self._ltbl.update(where, values, values_sql=values_sql)

    @override
    def delete(self, where: str) -> None:
        self._ltbl.delete(where)

    @override
    def list_indices(self) -> Iterable[IndexConfig]:
        return self._ltbl.list_indices()

    @override
    def index_stats(self, index_name: str) -> IndexStatistics | None:
        return self._ltbl.index_stats(index_name)

    @override
    def optimize(
        self,
        *,
        cleanup_older_than: timedelta | None = None,
        delete_unverified: bool = False,
    ) -> None:
        return self._ltbl.optimize(
            cleanup_older_than=cleanup_older_than,
            delete_unverified=delete_unverified,
        )

    @override
    def compact_files(self) -> None:
        self._ltbl.compact_files()

    # TODO: This annotation sucks
    def take_blobs(self, indices: list[int] | pa.Array, column: str):  # noqa: ANN201
        return self._ltbl.to_lance().take_blobs(indices, column)

    def uses_v2_manifest_paths(self) -> bool:
        return self._ltbl.uses_v2_manifest_paths()

    def migrate_v2_manifest_paths(self) -> None:
        return self._ltbl.migrate_v2_manifest_paths()
