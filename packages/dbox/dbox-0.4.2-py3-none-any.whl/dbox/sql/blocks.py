from functools import cached_property
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional

import jinja2
from pydantic import BaseModel, Field, computed_field, model_validator

from dbox.templater import to_template

from .base import AbstractSqlBlock, AbstractSqlFunction, SqlField

template_dir = Path(__file__).parent / "templates"


class RawSqlBlock(AbstractSqlBlock):
    raw: str

    def sql(self) -> str:
        return self.raw


class TemplateMixin(BaseModel):
    def get_template(self) -> jinja2.Template:
        raise NotImplementedError

    def to_template(self, template) -> jinja2.Template:
        return to_template(template)

    def get_render_params(self) -> Dict[str, Any]:
        params = {"this": self}
        # put in class variables first
        for name in self.__class__.__class_vars__:
            params[name] = getattr(self.__class__, name)
        # put in instance variables
        params.update(dict(self))
        # put in computed fields
        for name, _ in self.model_computed_fields.items():
            params[name] = getattr(self, name)
        return params

    def sql(self) -> str:
        render_params = self.get_render_params()
        return self.get_template().render(**render_params)


class TemplateSqlBlock(TemplateMixin, AbstractSqlBlock):
    template: Any

    def get_template(self) -> jinja2.Template:
        return self.to_template(self.template)


class TemplateSqlFunction(TemplateMixin, AbstractSqlFunction):
    template: Any

    def get_template(self) -> jinja2.Template:
        return self.to_template(self.template)


class PredefinedTemplateSqlBlock(TemplateMixin, AbstractSqlBlock):
    template: ClassVar[Any]

    def get_template(self) -> jinja2.Template:
        return self.to_template(Path(self.template))


class PredefinedTemplateSqlFunction(TemplateMixin, AbstractSqlFunction):
    template: ClassVar[Any]

    def get_template(self) -> jinja2.Template:
        return self.to_template(Path(self.template))


class StackingSqlFunction(PredefinedTemplateSqlFunction):
    template: ClassVar = template_dir / "stacking.j2"

    blocks: List[AbstractSqlFunction]
    auto_name: bool = False

    def decompose(self) -> List[AbstractSqlFunction]:
        return self.blocks

    def sql(self) -> str:
        blocks = self.blocks  # [e.model_copy() for e in self.blocks]
        if len(blocks) == 1:
            return blocks[0].sql()
        last_block_name = "input_source"
        for idx, block in enumerate(blocks):
            if self.auto_name:
                block.name = f"block_{idx}"
            block.input_block = Table(table=last_block_name)
            last_block_name = block.name
        return super().sql()


class Table(AbstractSqlBlock):
    table: str
    fields: List[SqlField] = Field(default_factory=list)

    def sql(self) -> str:
        return "select * from " + self.sql_target()

    def sql_target(self) -> str:
        return self.table

    def get_fields(self):
        return self.fields


class Select(PredefinedTemplateSqlFunction):
    template: ClassVar = template_dir / "select.j2"

    selects: Optional[List[str]] = None
    excepts: Optional[List[str]] = None
    filters: Optional[List[str]] = None


class TableDiff(PredefinedTemplateSqlFunction):
    template: ClassVar = template_dir / "table_diff.j2"

    source: AbstractSqlBlock
    target: AbstractSqlBlock
    key_columns: List[str]


class Diff0(PredefinedTemplateSqlBlock):
    template: ClassVar = template_dir / "diff0.j2"

    source: AbstractSqlBlock
    target: AbstractSqlBlock
    key_columns: List[str]


class CteBlock(PredefinedTemplateSqlFunction):
    template: ClassVar = template_dir / "cte.j2"

    blocks: List[AbstractSqlBlock]


class StackBlock(PredefinedTemplateSqlBlock):
    template: ClassVar = template_dir / "stack.j2"

    blocks: List[AbstractSqlBlock]

    # validate that the blocks are all stackable
    @model_validator(mode="after")
    def validate_blocks(self):
        names = [e.name for e in self.blocks if e.name]
        assert len(names) == len(set(names)), "Blocks must have unique names."
        for block in self.blocks[1:]:
            if not isinstance(block, AbstractSqlFunction):
                raise ValueError(f"Block {block} is not stackable")
        return self

    @cached_property
    def cloned_blocks(self):
        cloned = [block.model_copy() for block in self.blocks]
        for idx, block in enumerate(cloned):
            block.name = block.name or f"block_{idx}"
        return cloned

    def sql(self):
        if len(self.blocks) == 1:
            return self.blocks[0].sql()
        else:
            # do a copy of the blocks since we might assign names to them
            for idx, block in enumerate(self.cloned_blocks):
                if idx == 0:
                    continue
                else:
                    last_block = self.cloned_blocks[idx - 1]
                    target_block = Table(table=last_block.name)
                    self.cloned_blocks[idx] = block(target_block)
            return super().sql()


class UnionAll(PredefinedTemplateSqlBlock):
    template: ClassVar = template_dir / "union_all.j2"

    blocks: List[AbstractSqlBlock]


class Hash(PredefinedTemplateSqlFunction):
    template: ClassVar = template_dir / "hash_data.j2"


class JoinTarget(BaseModel):
    target: AbstractSqlBlock
    condition: str
    alias: Optional[str] = None


class JoinBlock(PredefinedTemplateSqlBlock):
    template: ClassVar = template_dir / "join.j2"

    base: AbstractSqlBlock
    joins: List[JoinTarget]

    def quote(self, expr):
        # TODo: make use of SqlGenContext
        return f'"{expr}"'

    def get_fields(self) -> List[SqlField]:
        fields = []
        for f in self.base.get_fields():
            fields.append(f.name)
        for block in [j.target for j in self.joins]:
            alias = block.name
            assert alias
            for f in block.get_fields():
                fields.append(f"{alias}.{f.name}")
        return [SqlField(name=f) for f in fields]

    @computed_field()
    def select_expressions(self) -> List[Any]:
        selects = []
        for fname in self.base.get_field_names():
            alias = self.base.name
            select = [f"{alias}.{fname}", f"{fname}"]
            selects.append(select)
        for block in [j.target for j in self.joins]:
            alias = block.name
            assert alias
            for fname in block.get_field_names():
                select = [f"{alias}.{fname}", f"{alias}.{fname}"]
                selects.append(select)
        return selects


class Stat(PredefinedTemplateSqlFunction):
    template: ClassVar = template_dir / "stat.j2"

    key_columns: List[str] = Field(default_factory=list)


class SortArray(PredefinedTemplateSqlFunction):
    template: ClassVar = template_dir / "sort_array.j2"

    column: str
    order_column: str
