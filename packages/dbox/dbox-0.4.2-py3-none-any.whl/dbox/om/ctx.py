import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from psycopg import AsyncConnection, AsyncCursor
from psycopg.rows import DictRow, dict_row
from psycopg.types.json import Json
from psycopg_pool import AsyncConnectionPool

from dbox.ctx import set_context, use_factory

from .meta import Omt

parent_dir = Path(__file__).parent
log = logging.getLogger(__name__)


def default_json(v: Any) -> Any:
    if isinstance(v, Decimal):
        return str(v)
    if isinstance(v, datetime):
        return v.isoformat()
    raise TypeError(f"Unsupported type: {type(v)}")


def dump_json(v: Any) -> str:
    return json.dumps(v, default=default_json)


class SqlContext:
    def __init__(self, pool: AsyncConnectionPool = None, schema: str = "public", **kwargs):
        super().__init__(**kwargs)
        # self.add_template_path(parent_dir / "templates")
        self.schema = schema
        self._pool = pool
        self._cursor: AsyncCursor[DictRow] = None
        self._conn: AsyncConnection[DictRow] = None

    def __enter__(self):
        self.__context_manager = set_context(SqlContext, self)
        self.__context_manager.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self.__context_manager.__exit__(exc_type, exc_value, traceback)

    def get_fqtn(self, table_name: str) -> str:
        return '"{}"."{}"'.format(self.schema, table_name)
        # return self.quote(self.schema) + "." + self.quote(table_name)

    @property
    def cursor(self):
        assert self._cursor is not None, "Cursor not available"
        return self._cursor

    @property
    def connection(self):
        assert self._conn is not None, "Connection not available"
        return self._conn

    @asynccontextmanager
    async def use_db(self, start_transaction: bool = False):
        """Prepare the connections and cursor for a transaction"""
        pool = self._pool
        await pool.open()
        async with pool.connection() as conn:
            self._conn = conn
            conn.row_factory = dict_row
            cursor = conn.cursor()
            async with cursor:
                self._cursor = cursor
                if start_transaction:
                    await cursor.execute("begin transaction")
                try:
                    yield cursor
                    await conn.commit()
                except Exception:
                    await conn.rollback()
                    raise

    async def run_query(self, query: str, *, many=False, params=None, exec: bool = False, **kwargs):
        log.debug("Query: %s", query)
        await self.cursor.execute(query, params)
        if exec:
            return
        result = list(await self.cursor.fetchall())
        if many:
            return result
        else:
            assert len(result) < 2
            if len(result) == 0:
                return None
            return result[0]

    async def start_transaction(self):
        await self.cursor.execute("begin transaction")

    async def commit(self):
        await self.connection.commit()

    def serialize(self, om: Omt, value: Any):
        om: Omt
        if value is None:
            return None
        if om.info.annotation is None:
            return value
        if om.info.annotation in (int, float, bool, str):
            return value
        elif om.info.annotation == Decimal:
            return Decimal(value) if not isinstance(value, Decimal) else value
        elif om.info.annotation == datetime:
            return value
        elif om.to_db_value is not None:
            return om.to_db_value(value)
        elif om.is_json:
            return Json(value, dumps=dump_json)
        return value
        # Optional[datetime] ???
        # should return something before this
        raise NotImplementedError(f"Unsupported type: {om.info}")


use_sql_context = use_factory(SqlContext)
