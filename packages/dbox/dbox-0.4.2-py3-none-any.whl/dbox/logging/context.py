from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Dict

_log_ctx_var: ContextVar[Dict[str, Any]] = ContextVar("LOG", default=None)


@contextmanager
def set_log_labels(**kwargs):
    current_labels = _log_ctx_var.get() or {}
    new_labels = {**current_labels, **kwargs}
    token = _log_ctx_var.set(new_labels)
    try:
        yield
    finally:
        _log_ctx_var.reset(token)


def current_log_labels():
    return _log_ctx_var.get() or {}
