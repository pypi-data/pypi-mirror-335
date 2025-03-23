import logging
from collections import defaultdict
from typing import Any, ClassVar, Dict, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel

from dbox.sql.blocks import RawSqlBlock, Select

from .ctx import SqlContext, use_sql_context
from .model import DModel
from .sql import CountBlock, PagingBlock

DataT = TypeVar("DataT")

log = logging.getLogger(__name__)


def to_nested(data: Dict[str, Any]):
    ret = defaultdict(dict)
    nested = set()
    for k, v in data.items():
        if "." in k:
            prefix, rest = k.split(".", 1)
            ret[prefix][rest] = v
            nested.add(prefix)
        else:
            ret[k] = v
    for k in nested:
        ret[k] = to_nested(ret[k])
    if all(v is None for v in ret.values()):
        # left join data null
        # return dict(ret)
        return None
    return dict(ret)


DataT = TypeVar("DataT")
FilterT = TypeVar("FilterT")


class CollectionPage(BaseModel, Generic[DataT]):
    data: List[DataT]
    total_count: Optional[int] = None
    current_page: Optional[int] = None  # current page


async def get_one(
    ModelT: Type["DModel"],  # noqa: N803
    *,
    ctx: SqlContext = None,
    pk=None,
):
    ctx = ctx or use_sql_context()
    query = Select(
        input_block=RawSqlBlock(raw=ModelT.select(ctx)),
        filters=[f"{ModelT.pk_col()} = %(pk)s"],
    ).to_sql()
    await ctx.cursor.execute(query, {"pk": pk})
    row = await ctx.cursor.fetchone()
    if row is None:
        return None
    return ModelT.bind(row)


async def paginate(
    ModelT: Type["DModel"],  # noqa: N803
    *,
    ctx: SqlContext = None,
    conditions: List[str] = None,
    order_by: List[str] = None,
    limit: int = 0,
    offset: int = 0,
    page: int = None,
    include_total: bool = False,
    params=None,
) -> CollectionPage[DModel]:  # noqa
    ctx = ctx or use_sql_context()
    source = RawSqlBlock(raw=ModelT.select(ctx))
    if conditions:
        source = Select(input_block=source, filters=conditions)
    if page is not None:
        assert page >= 1
        assert limit > 0
        offset = (page - 1) * limit
    paging = PagingBlock(input_block=source, order_by=order_by or [], limit=limit, offset=offset)
    paging_query = paging.to_sql()
    log.debug("Query: %s", paging_query)
    log.debug("Params: %s", params)

    await ctx.cursor.execute(paging_query, params)
    rows = await ctx.cursor.fetchall()
    rows = [ModelT.bind(row) for row in rows]
    res = CollectionPage(data=rows)
    if include_total:
        cnt_query = CountBlock(input_block=source).to_sql()
        await ctx.cursor.execute(cnt_query, params)
        res.total_count = (await ctx.cursor.fetchone())["count"]
    if page is not None:
        res.current_page = page
    return res


async def fetch_all(
    ModelT: Type["DModel"],  # noqa: N803
    *,
    ctx: SqlContext = None,
    conditions: List[str] = None,
    order_by: List[str] = None,
    params=None,
) -> CollectionPage[DModel]:
    ctx = ctx or use_sql_context()
    res = await paginate(
        ModelT,
        ctx=ctx,
        conditions=conditions,
        order_by=order_by,
        limit=None,
        offset=None,
        params=params,
    )
    res.total_count = len(res.data)
    return res


class QueryFilter(BaseModel):
    def sql_params(self, ctx) -> dict:
        return self.model_dump()

    def sql_conditions(self, ctx) -> List[str]:
        raise NotImplementedError


QueryFilterT = TypeVar("QueryFilterT", bound=QueryFilter)


class PaginateRequest(BaseModel, Generic[QueryFilterT]):
    limit: ClassVar[int] = 20

    page: Optional[int] = 1
    order_by: Optional[List[str]] = None
    query_filter: Optional[QueryFilterT] = None
    include_total: Optional[bool] = False

    def sql_params(self, ctx) -> dict:
        if self.query_filter is None:
            return {}
        return self.query_filter.sql_params(ctx=ctx)

    def conditions(self, ctx: SqlContext) -> List[str]:
        if self.query_filter is None:
            return []
        return self.query_filter.sql_conditions(ctx=ctx)


async def handle_paginate(
    ModelT: Type["DModel"],  # noqa: N803
    *,
    paginate_request: PaginateRequest,
    ctx: SqlContext = None,
) -> CollectionPage[DModel]:  # noqa
    ctx = ctx or use_sql_context()
    return await paginate(
        ModelT,
        ctx=ctx,
        conditions=paginate_request.conditions(ctx=ctx),
        order_by=paginate_request.order_by,
        limit=paginate_request.limit,
        page=paginate_request.page,
        include_total=paginate_request.include_total or paginate_request.page == 1,
        params=paginate_request.sql_params(ctx=ctx),
    )
