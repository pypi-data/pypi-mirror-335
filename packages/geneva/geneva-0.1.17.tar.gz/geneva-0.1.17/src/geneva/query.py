# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import json
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

import pyarrow as pa

# Self is not available in python 3.10
from typing_extensions import Self, override  # noqa: UP035

from geneva.db import connect
from geneva.table import Table

if TYPE_CHECKING:
    from lance import LanceDataset


class Query(ABC):
    """Present a Query"""

    @abstractmethod
    def to_batches(self, batch_size: int | None = None) -> Iterator[pa.RecordBatch]: ...

    @property
    @abstractmethod
    def schema(self) -> pa.Schema: ...

    @abstractmethod
    def to_dict(self) -> dict: ...

    @staticmethod
    def from_dict(data: dict[str, Any] | str) -> "Query":
        if isinstance(data, str):
            data: dict = json.loads(data)

        match data["type"]:
            case "scan":
                db = connect(data["db"])
                table = db.open_table(data["table"])
                return Scan(table, columns=data["columns"])
            case "projection":
                return Projection(
                    Query.from_dict(data["source"]),
                    columns=[Column(name) for name in data["columns"]],
                )
            case "filter":
                return Filter(Query.from_dict(data["source"]), data["filter"])
            case _:
                raise ValueError(f"Unknown query type: {data['type']}")

    def filter(self, filter: str) -> "Query":  # noqa: A002
        return Filter(self, filter)

    def cache(self) -> Self:
        return self

    def shuffle(self) -> Self:
        return self


class Column:
    """Present a Column in the Table."""

    def __init__(self, name: str) -> None:
        """Define a column."""
        self.name = name

    def alias(self, alias: str) -> "Column":
        return AliasColumn(self, alias)

    def blob(self) -> "Column":
        return BlobColumn(self)

    def apply(self, batch: pa.RecordBatch) -> tuple[str, pa.Array]:
        return (self.name, batch[self.name])


class BlobColumn(Column):
    def __init__(self, col: Column) -> None:
        self.inner = col


class AliasColumn(Column):
    def __init__(self, col: Column, alias: str) -> None:
        self.col = col
        self._alias = alias

    def apply(self, batch: pa.RecordBatch) -> tuple[str, pa.Array]:
        _, arr = self.col.apply(batch)
        return (self._alias, arr)


class Projection(Query):
    def __init__(self, source: Query, columns: list[Column]) -> None:
        self.source = source
        self.columns = columns
        col_names = [col.name for col in columns]
        if col_names:
            self.source = source.with_columns(col_names)

    def with_columns(self, columns: list[str]) -> Self:
        return Projection(self.source, [Column(name) for name in columns])

    def with_row_id(self) -> Self:
        self.source = self.source.with_row_id()
        return self

    def take_rows(self, rows: list[int]) -> pa.Table:
        return self.source.take_rows(rows)

    @override
    def to_dict(self) -> dict:
        return {
            "type": "projection",
            "source": self.source.to_dict(),
            "columns": [col.name for col in self.columns],
        }

    @property
    def schema(self) -> pa.Schema:
        return self.source.schema

    @override
    def to_batches(
        self,
        batch_size: int | None = None,
    ) -> Iterator[dict[str, pa.Array] | pa.RecordBatch]:
        yield from self.source.to_batches(batch_size)


class Filter(Query):
    def __init__(self, source: Query, filter: str) -> None:  # noqa: A002
        self.source = source
        self._filter = filter

    @property
    def schema(self) -> pa.Schema:
        return self.source.schema

    def to_dict(self) -> dict:
        return {
            "type": "filter",
            "source": self.source.to_dict(),
            "filter": self._filter,
        }

    def to_batches(self, batch_size: int | None = None) -> Iterator[pa.RecordBatch]:
        self.source.source._filter = self._filter
        yield from self.source.to_batches(batch_size)


class Scan(Query):
    def __init__(
        self,
        table: Table,
        columns: list[str] | None = None,
        with_row_id: bool = False,
        with_row_address: bool = False,
        filter: str | None = None,  # noqa: A002
    ) -> None:
        self.table = table
        self._columns = columns
        self._with_row_id = with_row_id
        self._with_row_address = with_row_address
        self._filter = filter
        # Which columns are blobs?
        self._blob_columns: list[str] = []
        self._offset: int | None = None
        self._limit: int | None = None
        self._fragment_ids: list[int] | None = None

    @classmethod
    def from_uri(cls, db: str, name: str, *, version: int | None = None) -> Self:
        table = connect(db).open_table(name)
        return cls(
            table=table,
        )

    def with_filter(self, filter: str | None) -> Self:  # noqa: A002
        self._filter = filter
        return self

    def with_columns(self, columns: list[str]) -> Self:
        self._columns = columns
        return self

    def with_row_id(self) -> Self:
        """
        Include auto-incremented row id in the result
        WARNING: NOT A STABLE FEATURE
        """
        self._with_row_id = True
        return self

    def with_offset(self, offset: int) -> Self:
        self._offset = offset
        return self

    def with_limit(self, limit: int) -> Self:
        self._limit = limit
        return self

    def with_fragments(self, fragments: list[int] | int) -> Self:
        self._fragment_ids = [fragments] if isinstance(fragments, int) else fragments
        return self

    def with_row_address(self) -> Self:
        """
        Include the physical row address in the result
        WARNING: INTERNAL API DETAIL
        """
        self._with_row_address = True
        return self

    def __repr__(self) -> str:
        return (
            f"Scan({self.table}, columns={self._columns}, "
            f"with_row_id={self._with_row_id},"
            f" with_row_address={self._with_row_address}, filter={self._filter})"
        )

    @override
    def to_dict(self) -> dict:
        return {
            "type": "scan",
            "db": str(self.table._conn.uri),
            "table": self.table._name,
            "columns": self._columns,
            "with_row_id": self._with_row_id,
            "with_row_address": self._with_row_address,
            "filter": self._filter,
            "fragments": self._fragment_ids,
            "offset": self._offset,
            "limit": self._limit,
        }

    def _scan_schema(self) -> pa.Schema:
        original_schema: pa.Schema = self.table.schema
        if self._columns:
            fields = [original_schema.field(col) for col in self._columns]
        else:
            fields = [original_schema.field(name) for name in original_schema.names]
        return pa.schema(fields)

    @property
    def schema(self) -> pa.Schema:
        scan_schema = self._scan_schema()
        fields = [scan_schema.field(name) for name in scan_schema.names]
        if self._with_row_id:
            fields += [pa.field("_rowid", pa.int64())]
        if self._with_row_address:
            fields += [pa.field("_rowaddr", pa.int64())]
        return pa.schema(fields)

    def take_rows(self, rows: list[int]) -> pa.Table:
        return self.table._ltbl.to_lance()._take_rows(rows, self._columns)

    def _has_blob_columns(self) -> bool:
        schema = self.schema
        for field in schema:
            if field.metadata and field.metadata.get(b"lance-encoding:blob") == b"true":
                return True
        return False

    @override
    def to_batches(self, batch_size: int | None = None) -> Iterator[pa.RecordBatch]:
        if self._has_blob_columns():
            self.with_row_id()

        schema = self._scan_schema()
        blob_columns = []
        normal_columns = []
        for field in schema:
            if field.metadata and field.metadata.get(b"lance-encoding:blob") == b"true":
                blob_columns.append(field.name)
            else:
                normal_columns.append(field.name)
        if len(blob_columns) > 0:
            self.with_row_id()

        if isinstance(self.table._ltbl, Query):
            for batch in self.table._ltbl.to_batches():
                yield batch
            return

        table_handle: LanceDataset = self.table._ltbl.to_lance()
        fragments = None
        if self._fragment_ids:
            fragments = [table_handle.get_fragment(fid) for fid in self._fragment_ids]

        for batch in table_handle.scanner(
            columns=normal_columns,
            with_row_id=self._with_row_id,
            with_row_address=self._with_row_address,
            filter=self._filter,
            batch_size=batch_size,
            offset=self._offset,
            limit=self._limit,
            fragments=fragments,
        ).to_batches():
            if blob_columns:
                ret = batch.to_pydict()
                for blob_column in blob_columns:
                    files = table_handle.take_blobs(
                        batch["_rowid"].to_pylist(),
                        blob_columns[0],
                    )
                    ret[blob_column] = files
                yield ret
            else:
                yield batch
