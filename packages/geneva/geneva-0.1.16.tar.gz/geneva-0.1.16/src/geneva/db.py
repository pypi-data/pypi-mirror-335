# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import os
from collections.abc import Iterable
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Optional
from urllib.parse import urlparse

import attrs
import lancedb
import pyarrow as pa
from lancedb import DBConnection
from lancedb.common import DATA, Credential
from lancedb.pydantic import LanceModel
from overrides import override

from geneva.checkpoint import CheckpointStore
from geneva.config import CONFIG_LOADER, ConfigBase
from geneva.remote.client import RestfulLanceDBClient

if TYPE_CHECKING:
    from flightsql import FlightSQLClient

    from geneva.job.client import JobClient
    from geneva.runners.dataflow import DataflowOptions
    from geneva.table import Table


class Connection(DBConnection):
    """Geneva Connection."""

    def __init__(
        self,
        uri: str,
        *,
        region: str = "us-east-1",
        api_key: Credential | None = None,
        host_override: str | None = None,
        storage_options: dict[str, str] | None = None,
        checkpoint_store: CheckpointStore | None = None,
        dataflow_options: Optional["DataflowOptions"] = None,
        **kwargs,
    ) -> None:
        super().__init__()
        self._uri = uri
        self._region = region
        self._api_key = api_key
        self._host_override = host_override
        self._storage_options = storage_options
        self._ldb: DBConnection | None = None
        self._checkpoint_store = checkpoint_store

        self._flight_client: FlightSQLClient | None = None

        # Dataflow Options
        self._dataflow_options = dataflow_options

    def __repr__(self) -> str:
        return f"<LanceLake uri={self.uri}>"

    def __getstate__(self) -> dict:
        return {
            "uri": self._uri,
            "api_key": self._api_key,
            "host_override": self._host_override,
            "storage_options": self._storage_options,
            "region": self._region,
        }

    def __setstate__(self, state) -> None:
        self.__init__(state.pop("uri"), **state)

    def __enter__(self) -> "Connection":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
        return None  # Don't suppress exceptions

    def close(self) -> None:
        """Close the connection."""
        if self._flight_client is not None:
            self._flight_client.close()

    @cached_property
    def _connect(self) -> DBConnection:
        """Returns the underlying lancedb connection."""
        if self._ldb is None:
            self._ldb = lancedb.connect(
                self.uri,
                region=self._region,
                api_key=self._api_key,
                host_override=self._host_override,
                storage_options=self._storage_options,
            )
        return self._ldb

    @cached_property
    def flight_client(self) -> "flightsql.FlightSQLClient":  # noqa: F821
        from flightsql import FlightSQLClient

        if self._flight_client is not None:
            return self._flight_client
        url = urlparse(self._host_override)
        hostname = url.hostname
        client = FlightSQLClient(
            host=hostname,
            port=10025,
            token="DATABASE_TOKEN",  # Dummy auth, not plugged in yet
            metadata={"database": self.uri},  # Name of the project-id
            features={"metadata-reflection": "true"},
            insecure=True,  # or False, up to you
        )
        self._flight_client = client
        return client

    @cached_property
    def _client(self) -> RestfulLanceDBClient:
        if (self._api_key is None) or (self._region is None):
            raise ValueError("API Key and Region must be provided.")

        return RestfulLanceDBClient(
            db_name=self._uri.removeprefix("db://"),
            region=self._region,
            api_key=self._api_key,
            host_override=self._host_override,
        )

    @override
    def table_names(
        self,
        page_token: str | None = None,
        limit: int | None = None,
    ) -> Iterable[str]:
        """List all available tables and views."""
        return self._connect.table_names(page_token=page_token, limit=limit or 10)

    @override
    def open_table(
        self,
        name: str,
        *,
        storage_options: dict[str, str] | None = None,
        index_cache_size: int | None = None,
        version: int | None = None,
    ) -> "Table":
        """Open a Lance Table.

        Parameters
        ----------
        name: str
            Name of the table.
        storage_options: dict[str, str], optional
            Additional options for the storage backend.
            Options already set on the connection will be inherited by the table,
            but can be overridden here. See available options at
            [https://lancedb.github.io/lancedb/guides/storage/](https://lancedb.github.io/lancedb/guides/storage/)


        """
        from .table import Table

        storage_options = storage_options or self._storage_options

        return Table(
            self,
            name,
            index_cache_size=index_cache_size,
            storage_options=storage_options,
            version=version,
        )

    @override
    def create_table(  # type: ignore
        self,
        name: str,
        data: DATA | None = None,
        schema: pa.Schema | LanceModel | None = None,
        mode: str = "create",
        exist_ok: bool = False,
        on_bad_vectors: str = "error",
        fill_value: float = 0.0,
        *,
        storage_options: dict[str, str] | None = None,
        **kwargs,
    ) -> "Table":  # type: ignore
        """Create a Table in the lake

        Parameters
        ----------
        name: str
            The name of the table
        data: The data to initialize the table, *optional*
            User must provide at least one of `data` or `schema`.
            Acceptable types are:

            - list-of-dict
            - pandas.DataFrame
            - pyarrow.Table or pyarrow.RecordBatch
        schema: The schema of the table, *optional*
            Acceptable types are:

            - pyarrow.Schema
            - [LanceModel][lancedb.pydantic.LanceModel]
        mode: str; default "create"
            The mode to use when creating the table.
            Can be either "create" or "overwrite".
            By default, if the table already exists, an exception is raised.
            If you want to overwrite the table, use mode="overwrite".
        exist_ok: bool, default False
            If a table by the same name already exists, then raise an exception
            if exist_ok=False. If exist_ok=True, then open the existing table;
            it will not add the provided data but will validate against any
            schema that's specified.
        on_bad_vectors: str, default "error"
            What to do if any of the vectors are not the same size or contain NaNs.
            One of "error", "drop", "fill".
        """
        from .table import Table

        self._connect.create_table(
            name,
            data,
            schema,
            mode,
            exist_ok=exist_ok,
            on_bad_vectors=on_bad_vectors,
            fill_value=fill_value,
            storage_options=storage_options,
            **kwargs,
        )
        return Table(self, name, storage_options=storage_options)

    def create_view(
        self,
        name: str,
        query: str,
        materialized: bool = False,
    ) -> "Table":
        """Create a View from a Query.

        Parameters
        ----------
        name: str
            Name of the view.
        query: Query
            Query to create the view.
        materialized: bool, optional
            If True, the view is materialized.
        """
        self.sql("CREATE VIEW {name} AS ({query})")
        return self.open_table(name)

    def drop_view(self, name: str) -> pa.Table:
        """Drop a view."""
        return self.sql(f"DROP VIEW {name}")

    @cached_property
    def jobs(self) -> "JobClient":
        """Geneva Jobs API

        Example
        -------

            # List all jobs
            >>> conn = connect("db://mydb")
            >>> jobs = conn.jobs.list(table="mytable",
                limit=500,
                filter="created_at > '2021-01-01'")

            # Start a new job
            >>> conn.jobs.start(table="mytable", column="virtual_col")
        """
        from geneva.job.client import JobClient

        return JobClient(rest_client=self._client)

    def sql(self, query: str) -> pa.Table:
        """Execute a raw SQL query.

        It uses the Flight SQL engine to execute the query.

        Parameters
        ----------
        query: str
            SQL query to execute

        Returns
        -------
        pyarrow.Table
            Result of the query in a `pyarrow.Table`

        TODO
        ----
        - Support pagination
        - Support query parameters
        """
        info = self.flight_client.execute(query)
        return self.flight_client.do_get(info.endpoints[0].ticket).read_all()


@attrs.define
class _GenavaConnectionConfig(ConfigBase):
    region: str = attrs.field(default="us-east-1")
    api_key: str | None = attrs.field(default=None)
    host_override: str | None = attrs.field(default=None)
    checkpoint: str | None = attrs.field(default=None)

    @classmethod
    @override
    def name(cls) -> str:
        return "connection"


def connect(
    uri: str | Path,
    *,
    region: str | None = None,
    api_key: Credential | str | None = None,
    host_override: str | None = None,
    storage_options: dict[str, str] | None = None,
    checkpoint: str | CheckpointStore | None = None,
    dataflow_options: Optional["DataflowOptions"] = None,
    **kwargs,
) -> Connection:
    """Connect to Geneva.

    Examples
    --------
        >>> import geneva
        >>> conn = geneva.connect("db://my_dataset")
        >>> tbl = conn.open_table("youtube_dataset")

    Parameters
    ----------
    uri: geneva URI, or Path
        LanceDB Database URI, or a S3/GCS path
    region: str | None
        LanceDB cloud region. Set to `None` on LanceDB Enterprise
    api_key: str | None
        API key to connect to the DB instance.
    host_override: str | None
        Set to the host of the enterprise stack

    Returns
    -------
    Connection - A LanceDB connection

    """

    # load values from config if not provided via arguments
    config = CONFIG_LOADER.load(_GenavaConnectionConfig)
    region = region or config.region
    api_key = api_key or config.api_key
    api_key = Credential(api_key) if isinstance(api_key, str) else api_key
    host_override = host_override or config.host_override

    if checkpoint is None:
        checkpoint = os.getenv("LANCE_CHECKPOINT", "memory")
    if isinstance(checkpoint, str):
        checkpoint_store = CheckpointStore.from_uri(checkpoint)
    else:
        checkpoint_store = checkpoint
    return Connection(
        str(uri),
        region=region,
        api_key=api_key,
        host_override=host_override,
        storage_options=storage_options,
        checkpoint_store=checkpoint_store,
        dataflow_options=dataflow_options,
        **kwargs,
    )
