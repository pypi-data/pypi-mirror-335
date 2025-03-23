import pytest


@pytest.fixture(scope="session", autouse=True)
def ctx():
    from psycopg_pool import AsyncConnectionPool

    from .ctx import SqlContext

    # conn = psycopg.connect("dbname=sgx_dev user=sgx_login")
    conn_info = "dbname=sgx_dev user=sgx_login"
    pool = AsyncConnectionPool(conn_info, open=False)

    # async def getconn():
    #     aconn = await psycopg.AsyncConnection.connect(conninfo=conn_info)
    #     aconn.row_factory = dict_row
    #     return aconn

    # conn.row_factory = dict_row
    with SqlContext(pool=pool) as sql:
        yield sql
        if pool is not None:
            co = pool.close()
            # co.close()
