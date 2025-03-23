import pytest

from dbox.sql.ctx import SqlGenContext


@pytest.fixture(scope="package")
def ctx():
    with SqlGenContext() as sql_ctx:
        yield sql_ctx
