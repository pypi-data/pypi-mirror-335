from __future__ import annotations

import logging
from pathlib import Path

from dbox.ctx import set_context, use_type

log = logging.getLogger(__name__)
parent_dir = Path(__file__).parent


class SqlGenContext:
    """Global context for SQL generation."""

    def __init__(self):
        self._params = {}
        self._search_paths = (parent_dir / "templates",)

    @property
    def params(self):
        """Extra params for rendering templates."""
        return self._params

    def quote(self, identifier: str) -> str:
        # postgresql
        return f'"{identifier}"'

    def __enter__(self):
        self.__context_manager = set_context(SqlGenContext, self)
        self.__context_manager.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self.__context_manager.__exit__(exc_type, exc_value, traceback)


# re-export for type hinting
def use_sql_context():
    return use_type(SqlGenContext)
