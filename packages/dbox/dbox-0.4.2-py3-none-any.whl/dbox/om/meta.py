import logging
from pathlib import Path
from typing import Any, Callable, Optional

from attrs import define
from pydantic.fields import FieldInfo

parent_dir = Path(__file__).parent
log = logging.getLogger(__name__)


@define(kw_only=True, slots=True)
class Omt:
    pk: bool = False
    foreign_key: bool = False
    reference_data: bool = False
    server_generated: bool = False
    system_column: bool = False

    is_json: bool = False
    to_db_value: Optional[Callable[[Any], Any]] = None

    # should not be set when init
    info: Optional[FieldInfo] = None
