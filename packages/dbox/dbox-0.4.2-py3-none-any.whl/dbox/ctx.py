from contextlib import contextmanager
from contextvars import ContextVar, copy_context
from typing import Any, Dict, TypeVar

_CTX_KEY: ContextVar[Dict[Any, Any]] = ContextVar("ctx", default=None)
_NOT_PROVIDED = object()
_T = TypeVar("T")


@contextmanager
def set_context(*args, **kwargs):
    try:
        reset = ctx_set(*args, **kwargs)
        yield
    finally:
        reset()


def ctx_set(*args, **kwargs):
    """Imperative version of set_context that can be used in ipython etc.
    Since set_context is a context manager, it automatically resets the context after the block.
    """
    ctx = _CTX_KEY.get() or {}
    new_ctx = {**ctx, **kwargs}
    if args:
        key, value = args
        new_ctx[key] = value
    token = _CTX_KEY.set(new_ctx)

    def reset():
        _CTX_KEY.reset(token)

    return reset


def _use(key, default=_NOT_PROVIDED):
    """Low-level method to get a value from the context."""
    curr = _CTX_KEY.get() or {}
    if key not in curr and default is _NOT_PROVIDED:
        raise RuntimeError("no such context key %s provided" % key)
    return curr.get(key, default)


def use_type(key: type[_T], default=_NOT_PROVIDED) -> _T:
    """Sugar for type checking."""
    return _use(key, default)


def use_key(key, default=_NOT_PROVIDED, tpe: type[_T] = _NOT_PROVIDED):
    """Sugar for type checking."""
    value = _use(key, default)
    if tpe is not _NOT_PROVIDED:
        value: _T  # = value
        return value
    return value


def use_factory(tpe: type[_T], key: str = _NOT_PROVIDED):
    if key is _NOT_PROVIDED:
        key = tpe

    def use_context(default=_NOT_PROVIDED) -> _T:
        return use_key(key, default, tpe=tpe)

    return use_context


if __name__ == "__main__":

    class MyAwesomeClass:
        pass

    awesome = MyAwesomeClass()
    with set_context(MyAwesomeClass, awesome) as ctx:
        use_awesome = use_factory(MyAwesomeClass)
        awesome2 = use_type(MyAwesomeClass)
        assert use_awesome() is awesome
        assert awesome2 is awesome

    with set_context(
        username="duanlv",
        session="awesome",
    ):
        ctx_set("username", "0")
        username = use_key("username")
        print(_use("username"))
        with set_context(
            username="admin",
        ):
            print(_use("username"))

        print(_use("username"))
