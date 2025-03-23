import duckdb


class DataAssertion:
    def __init__(self, conn):
        self.conn = duckdb.connect(":memory:")
        self.rel = self.conn.execute("select 100 as col1, 200 as col2")

    def assert_empty(self):
        assert self.rel.fetchone() is None

    def assert_value(self, expected_value):
        assert self.rel.fetchall() == expected_value


def bigquery_assert(
    query,
    materialize: bool = False,
):
    pass


def assert_zero_rows(query, materialize: bool = False):
    paaa
