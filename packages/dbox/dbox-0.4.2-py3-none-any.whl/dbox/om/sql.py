from pathlib import Path
from typing import ClassVar, List, Optional, Type

from pydantic import Field

from dbox.sql.base import AbstractSqlBlock, SqlField
from dbox.sql.blocks import (
    JoinBlock,
    JoinTarget,
    PredefinedTemplateSqlBlock,
    PredefinedTemplateSqlFunction,
    Select,
    Table,
)

from .model import DModel

template_dir = Path(__file__).parent / "templates"


class PagingBlock(PredefinedTemplateSqlFunction):
    template: ClassVar = template_dir / "paging.sql"

    order_by: List[str] = Field(default_factory=list)
    limit: Optional[int] = None
    offset: Optional[int] = None


class CountBlock(PredefinedTemplateSqlFunction):
    template: ClassVar = template_dir / "count.sql"


class InsertBlock(PredefinedTemplateSqlBlock):
    template: ClassVar = template_dir / "insert.sql"

    model: Type[DModel]
    columns: List[str]
    pk_col: str


class UpdateBlock(PredefinedTemplateSqlBlock):
    template: ClassVar = template_dir / "update.sql"

    model: Type[DModel]
    pk_col: str
    columns: List[str]


class SoftDelete(PredefinedTemplateSqlBlock):
    template: ClassVar = template_dir / "soft_delete.sql"

    model: Type[DModel]
    pk_col: str


class Delete(PredefinedTemplateSqlBlock):
    template: ClassVar = template_dir / "delete.sql"

    model: Type[DModel]


class Filter(PredefinedTemplateSqlFunction):
    template: ClassVar = template_dir / "filter.sql"

    conditions: List[str] = Field(default_factory=list)


class DModelRelation(AbstractSqlBlock):
    model: Type[DModel]

    def model_post_init(self, __context):
        self.name = self.model.__tablename__

    def to_sql(self):
        return Select(
            input_block=Table(table=self.model.get_fqtn()),
            selects=self.model.self_fields(),
        ).to_sql()

    def sql_target(self):
        return self.model.get_fqtn()

    def get_fields(self):
        return [SqlField(name=f) for f in self.model.self_fields()]


def join_models(base: Type[DModel], *args):
    targets = []
    for model, condition in args:
        targets.append(JoinTarget(target=DModelRelation(model=model), condition=condition))
    join = JoinBlock(base=DModelRelation(model=base), joins=targets)
    return join.to_sql()
