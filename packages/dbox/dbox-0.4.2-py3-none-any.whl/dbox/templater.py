import os
from pathlib import Path, PurePath

import jinja2
from jinja2 import FunctionLoader, TemplateNotFound

parent_dir = Path(__file__).parent


def _load_source_from_path(template: str):
    assert isinstance(template, str)  # this must be the case for jinja2
    path = Path(template)
    if not path.exists():
        raise TemplateNotFound(template)

    with open(path) as f:
        contents = f.read()

    mtime = os.path.getmtime(path)

    def uptodate() -> bool:
        try:
            return os.path.getmtime(path) == mtime
        except OSError:
            return False

    # Use normpath to convert Windows altsep to sep.
    return contents, path.as_posix(), uptodate


jinja = jinja2.Environment(
    trim_blocks=True,
    lstrip_blocks=True,
    loader=FunctionLoader(_load_source_from_path),
    undefined=jinja2.StrictUndefined,
)


# register useful filters
def must_there(value):
    if not value:
        raise ValueError(f"Value is not true: {value}")
    return value


jinja.filters["must_there"] = must_there


def to_template(template) -> jinja2.Template:
    """Convert to a template object using a resonable environment settings.
    If it is string, it is considered as a template string.
    If it is a path, then we load the template from the path.
    """
    if isinstance(template, jinja2.Template):
        return template
    if isinstance(template, PurePath):
        return jinja.get_template(template.as_posix())
    assert isinstance(template, str)
    return jinja.from_string(template)
