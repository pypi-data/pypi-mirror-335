import atexit
import logging
import sys
from contextlib import contextmanager
from contextvars import ContextVar

import psutil

log = logging.getLogger(__name__)


class ShellContext:
    def __init__(self, name: str = None, parent: "ShellContext" = None) -> None:
        self.name = name
        self.parent = parent
        self.started_pids = []
        self.running_pids = []

    def add(self, pid: int):
        self.running_pids.append(pid)
        self.started_pids.append(pid)

    def complete(self, pid: int):
        self.running_pids.remove(pid)

    def _terminate(self, pid: int):
        if psutil.pid_exists(pid):
            try:
                p = psutil.Process(pid)
                cmdline = p.cmdline()
                p.terminate()
                return cmdline
            except psutil.NoSuchProcess:
                return None
        else:
            return None

    def terminate_runnings(self) -> int:
        cnt = 0
        for pid in list(self.running_pids):
            try:
                if cmdline := self._terminate(pid):
                    log.warning("Terminate preemptively: %d %s", pid, cmdline)
                cnt += 1
                self.running_pids.remove(pid)
            except Exception:
                log.warning("Failed terminating process %s", pid, exc_info=True)
                continue
        return cnt


GLOBAL_SHELL_CTX = ShellContext(name="global")
_CTX_VAR = ContextVar("current_shell_context", default=GLOBAL_SHELL_CTX)


def current_shell_context() -> ShellContext:
    return _CTX_VAR.get()


@contextmanager
def shell_context(stop_at_exit=True):
    current_ctx = current_shell_context()
    new_ctx = ShellContext(parent=current_ctx)
    try:
        token = _CTX_VAR.set(new_ctx)
        yield new_ctx
    finally:
        if stop_at_exit:
            new_ctx.terminate_runnings()
        _CTX_VAR.reset(token)


# def ctx_clean_up():
#     might_runnings = GLOBAL_SHELL_CTX.running_pids

#     for pid in might_runnings:
#         if cmdline := GLOBAL_SHELL_CTX.terminate(pid):
#             print(f"AT_EXIT: killed preemptively {pid:>7} {cmdline}", file=sys.stderr)


# atexit.register(ctx_clean_up)
