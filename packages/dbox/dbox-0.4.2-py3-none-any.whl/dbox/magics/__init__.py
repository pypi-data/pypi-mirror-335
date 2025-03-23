from typing import TYPE_CHECKING

import IPython

from .bqx import bqx_magic
from .jinja import jinja_magic

if TYPE_CHECKING:
    from IPython.core.interactiveshell import InteractiveShell


def duckdb_magic(line, content: str):
    ipy: InteractiveShell = IPython.get_ipython()
    duckdb_conn = ipy.ns_table["user_global"].get("duckdb_conn")
    if duckdb_conn is None:
        raise ValueError("duckdb_conn not found in user_global")
    return duckdb_conn.sql(content)


def load_ipython_extension(ipython: "InteractiveShell"):
    """Called by IPython when this module is loaded as an IPython extension."""

    ipython.register_magic_function(bqx_magic, magic_kind="cell", magic_name="bqx")
    # ipython.register_magic_function(sqlx_magic, magic_kind="cell", magic_name="sqlx")
    ipython.register_magic_function(jinja_magic, magic_kind="cell", magic_name="j2")
    # ipython.register_magic_function(duckdb_magic, magic_kind="cell", magic_name="duck")
