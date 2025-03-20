from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING, Any, overload

import clickhouse_driver as chdr
import clickhouse_driver.dbapi.connection as chdrconn
import polars as pl
from clickhouse_driver.dbapi import DatabaseError, InterfaceError
from clickhouse_driver.dbapi.extras import Cursor, DictCursor, NamedTupleCursor
from clickhouse_driver.errors import Error as DriverError
from typing_extensions import Literal

from tesseract_olap.backend import (
    Backend,
    CacheConnection,
    CacheProvider,
    DummyProvider,
    ParamManager,
    Result,
    Session,
    chunk_queries,
    growth_calculation,
    rename_columns,
)
from tesseract_olap.common import AnyDict, AnyTuple, hide_dsn_password
from tesseract_olap.exceptions.backend import (
    BackendLimitsException,
    UpstreamInternalError,
    UpstreamNotPrepared,
)
from tesseract_olap.query import AnyQuery, DataQuery, MembersQuery

from .cursor import inyect_members_count, validate_schema_tables
from .dialect import TypedCursor, TypedDictCursor
from .sql_data import sql_dataquery
from .sqlbuild import (
    count_membersquery_sql,
    membersquery_sql,
)

if TYPE_CHECKING:
    from types import TracebackType

    from pypika.queries import Term

    from tesseract_olap.schema import SchemaTraverser

logger = logging.getLogger(__name__)


class ClickhouseBackend(Backend):
    """Clickhouse Backend class.

    This is the main implementation for Clickhouse of the core :class:`Backend`
    class.

    Must be initialized with a connection string with the parameters for the
    Clickhouse database. Then must be connected before used to execute queries,
    and must be closed after finishing use.
    """

    dsn: str

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    def new_session(self, cache: CacheProvider | None = None, **kwargs) -> ClickhouseSession:
        if cache is None:
            cache = DummyProvider()
        return ClickhouseSession(self.dsn, cache=cache, **kwargs)

    def ping(self) -> bool:
        """Check if the current connection is working correctly."""
        with self.new_session() as session, session.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        return result == (1,)

    def debug_query(self, query: AnyQuery, **kwargs) -> AnyDict:
        """Return the generated queries/metadata used in the process of fetching data."""
        count_qb, count_meta = _query_to_builder(query, count=True)
        data_qb, data_meta = _query_to_builder(query)
        return {
            "count": self._debug_single_query(count_qb.get_sql(), count_meta),
            "data": self._debug_single_query(data_qb.get_sql(), data_meta),
        }

    def validate_schema(self, schema: SchemaTraverser) -> None:
        """Check all the tables and columns referenced in the schema exist in the backend."""
        logger.debug("Validating schema '%r' against ClickhouseBackend", schema)

        with self.new_session() as session:
            # all cursors are closed when exiting the context
            with session.cursor("Tuple") as cursor:
                validate_schema_tables(schema, cursor)

            inyect_members_count(schema, [session.cursor("Dict") for _ in range(4)])


class ClickhouseSession(Session):
    """Session class for Clickhouse connections."""

    _cache: CacheConnection
    _connection: chdrconn.Connection
    _count_cache: dict[str, int]

    cache: CacheProvider
    chunk_limit: int
    dsn: str
    query_limit: int

    def __init__(
        self,
        dsn: str,
        *,
        cache: CacheProvider,
        chunk_limit: int = 100000,
        query_limit: int = 1000000,
    ) -> None:
        self.cache = cache
        self.dsn = dsn
        self.chunk_limit = chunk_limit
        self.query_limit = query_limit

        self._count_cache = {}

    def __repr__(self) -> str:
        return f"{type(self).__name__}(dsn='{hide_dsn_password(self.dsn)}')"

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        super().__exit__(exc_type, exc_val, exc_tb)
        try:
            args: tuple[Any, ...] = getattr(exc_val, "args")  # noqa: B009
        except AttributeError:
            args = ("",)

        if args and isinstance(args[0], DriverError):
            exc = args[0]
            message, *_ = str(exc.message).split("Stack trace:", 1)
            msg = f"{type(exc).__name__}({exc.code}): {message}"
            raise UpstreamInternalError(msg) from exc

        try:
            exc_message = getattr(exc_val, "message")  # noqa: B009
            message = f"Clickhouse{type(exc_val).__name__}: {exc_message}"
        except AttributeError:
            message = f"Clickhouse{type(exc_val).__name__}"

        if isinstance(exc_val, InterfaceError):
            msg = f"{message}: {args[0]}"
            raise UpstreamNotPrepared(msg) from exc_val
        if isinstance(exc_val, DatabaseError):
            raise UpstreamInternalError(message, *args) from exc_val

    def connect(self):
        self._cache = self.cache.connect()
        self._connection = chdr.connect(dsn=self.dsn, compression="lz4")

    def close(self):
        self._cache.close()
        self._connection.close()
        delattr(self, "_cache")
        delattr(self, "_connection")

    @overload
    def cursor(self) -> TypedCursor: ...
    @overload
    def cursor(self, format_: Literal["Tuple"]) -> TypedCursor: ...
    @overload
    def cursor(self, format_: Literal["Dict"]) -> TypedDictCursor: ...
    @overload
    def cursor(self, format_: Literal["NamedTuple"]) -> NamedTupleCursor: ...

    def cursor(
        self,
        format_: Literal["Dict", "Tuple", "NamedTuple"] = "Tuple",
    ) -> Cursor | DictCursor | NamedTupleCursor:
        if format_ == "Dict":
            cls = TypedDictCursor
        elif format_ == "Tuple":
            cls = TypedCursor
        elif format_ == "NamedTuple":
            cls = NamedTupleCursor
        else:
            msg = f"Invalid cursor result format: '{format_}'"
            raise ValueError(msg)

        return self._connection.cursor(cls)

    def fetch(self, query: AnyQuery, **kwargs) -> Result[list[AnyTuple]]:
        """Execute the query and return the data as a list of tuples."""
        qbuilder, meta = _query_to_builder(query)

        with self.cursor() as cursor:
            for table in meta.tables:
                cursor.set_inline_table(table)
            cursor.execute(qbuilder.get_sql(), parameters=meta.params)
            data = cursor.fetchall() or []

        limit, offset = query.pagination.as_tuple()

        return Result(
            data=data,
            columns=query.columns,
            cache={"key": query.key, "status": "MISS"},
            page={"limit": limit, "offset": offset, "total": len(data)},
        )

    def fetch_dataframe(self, query: AnyQuery, **kwargs) -> Result[pl.DataFrame]:
        """Execute the query and returns the data as a polars DataFrame."""
        cursor = self.cursor()
        cursor.set_query_id(f"{query.key}_{random.randrange(4294967296):08x}")  # noqa: S311
        cursor.execute("SET use_query_cache = true")

        df_list: list[pl.DataFrame] = []
        pagi = query.pagination

        count = self._fetch_row_count(cursor, query)
        if 0 < self.query_limit < count and (pagi.limit == 0 or pagi.limit > self.query_limit):
            total = count if pagi.limit == 0 else pagi.limit
            msg = (
                f"This request intends to retrieve {total} rows of data, "
                "which is too large for the OLAP server to handle. "
                "Please reformulate the request with more limitations and try again."
            )
            raise BackendLimitsException(msg)

        logger.debug(
            "Query %s is %d rows; %r",
            query.key,
            count,
            pagi,
            extra={"query": repr(query)},
        )

        cache_status = "HIT"
        for chunk_query in chunk_queries(query, limit=self.chunk_limit):
            chunk_data = self._cache.retrieve(chunk_query)

            if chunk_data is None:
                qbuilder, meta = _query_to_builder(chunk_query)

                cursor.reset_cursor()
                for table in meta.tables:
                    cursor.set_inline_table(table)

                chunk_data = pl.read_database(
                    query=qbuilder.get_sql(),
                    connection=cursor,
                    execute_options={"parameters": meta.params},
                )
                self._cache.store(chunk_query, chunk_data)

                if chunk_data.height > 0:
                    cache_status = "MISS"

            logger.debug(
                "%s for chunk %r: %s (%.3fmb)",
                type(self.cache).__name__,
                chunk_query.key,
                cache_status,
                chunk_data.estimated_size("mb"),
                extra={"query": repr(chunk_query)},
            )

            if chunk_data.height > 0 or not df_list:
                df_list.append(chunk_data)
                if chunk_data.height < self.chunk_limit:
                    break
            else:
                break

        cursor.close()

        data = pl.concat(df_list) if len(df_list) > 1 else df_list[0]
        if isinstance(query, DataQuery):
            # Do growth calculation if query.growth exists
            data = growth_calculation(query, data)
            # Rename the columns according to the aliases
            data = rename_columns(query, data)

        result = Result(
            data=data.slice(pagi.offset % self.chunk_limit, pagi.limit or None),
            columns=query.columns,
            cache={"key": query.key, "status": cache_status},
            page={
                "limit": pagi.limit,
                "offset": pagi.offset,
                "total": count or data.height,
            },
        )

        return result

    def fetch_records(self, query: AnyQuery, **kwargs) -> Result[list[AnyDict]]:
        """Execute the query and return the data as a list of dictionaries."""
        qbuilder, meta = _query_to_builder(query)

        with self.cursor("Dict") as cursor:
            for table in meta.tables:
                cursor.set_inline_table(table)
            cursor.execute(qbuilder.get_sql(), parameters=meta.params)
            data: list[AnyDict] = cursor.fetchall()

        limit, offset = query.pagination.as_tuple()

        return Result(
            data=data,
            columns=query.columns,
            cache={"key": query.key, "status": "MISS"},
            page={"limit": limit, "offset": offset, "total": len(data)},
        )

    def _fetch_row_count(self, cursor: TypedCursor, query: AnyQuery) -> int:
        count = self._count_cache.get(query.count_key)

        if count is None:
            qbuilder, meta = _query_to_builder(query, count=True)
            for table in meta.tables:
                cursor.set_inline_table(table)
            cursor.execute(qbuilder.get_sql())
            row = cursor.fetchone()
            count = 0 if row is None else row[0]
            self._count_cache[query.count_key] = count

        return count


def _query_to_builder(query: AnyQuery, *, count: bool = False) -> tuple[Term, ParamManager]:
    """Translate any kind of query into an SQL builder object and its extra parameters."""
    if isinstance(query, DataQuery):
        return sql_dataquery(query, count=count)

    if isinstance(query, MembersQuery):
        return count_membersquery_sql(query) if count else membersquery_sql(query)

    raise ValueError("unreachable")  # noqa: EM101
