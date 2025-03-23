from pathlib import Path
from typing import ClassVar

import pytest
from pydantic import computed_field

from .base import AbstractSqlBlock
from .blocks import *
from .ctx import SqlGenContext

template_dir = Path(__file__).parent / "templates"


def test_jinja2_block(ctx: SqlGenContext):
    class TestBlock0(PredefinedTemplateSqlFunction):
        template: ClassVar[Path] = template_dir / "tests" / "test0.j2"

        a: int = 1

        @computed_field
        def b(self) -> int:
            return self.a + 1

    block = TestBlock0(a=1)
    assert block.sql() == "select 1 as a, 2 as b"


@pytest.mark.parametrize(
    "input_block",
    [TemplateSqlBlock(template="select 1 as a, 2 as b"), Table(table="`project.dataset.table`")],
)
def test_hash_data(input_block: AbstractSqlBlock):
    block = Hash(input_block=input_block)
    query = block.sql()
    print(query)


def test_select_block(ctx: SqlGenContext):
    source = TemplateSqlBlock(template="select 1 as a, 2 as b")
    # source.sql()
    apply1 = Select(
        selects=[
            "a",
            "b",
        ],
        filters=["b > 1"],
    )
    query = source | apply1 | apply1
    print(query.sql())


def test_stack_block(ctx: SqlGenContext):
    blocks = [
        TemplateSqlBlock(template="select 1 as a, 2 as b"),
        Select(
            selects=[
                "a",
                "b",
            ],
            filters=["b > 1"],
        ),
        Hash(),
    ]
    block = StackBlock(blocks=blocks)
    query = block.sql()
    print(query)


def test_joins(ctx):
    person = Table(
        name="person",
        table="person",
        fields=[{"name": "id"}, {"name": "name"}, {"name": "age"}, {"name": "department_id"}, {"name": "school_id"}],
    )
    department = Table(
        name="department", table="department", fields=[{"name": "id"}, {"name": "name"}, {"name": "company_id"}]
    )
    company = Table(name="company", table="company", fields=[{"name": "id"}, {"name": "name"}])
    school = Table(name="school", table="school", fields=[{"name": "id"}, {"name": "name"}])

    join = JoinBlock(
        base=person,
        joins=[
            JoinTarget(target=department, condition="person.department_id = department.id", alias="department"),
            JoinTarget(target=company, condition="department.company_id = company.id", alias="company"),
            JoinTarget(target=school, condition="person.school_id = school.id", alias="school"),
        ],
    )
    sql = join.sql()
    print(sql)


def test_diff0():
    source = TemplateSqlBlock(template="select i-1 as a, 2 as b from unnest([1,2,3]) i")
    target = TemplateSqlBlock(template="select i as a, 2 as b from unnest([1,2,3]) i")
    diff = Diff0(source=source, target=target, key_columns=["a"])
    print(diff.sql())


def test_stacking():
    stack = StackingSqlFunction(
        blocks=[
            Select(name="select", selects=["a", "b"]),
            Select(filters=["c > 1"], name="filter"),
            Hash(name="hash"),
        ],
        input_block=Table(table="project.dataset.table"),
    )
    print(stack.sql())
    stack.auto_name = True
    print(stack.sql())
