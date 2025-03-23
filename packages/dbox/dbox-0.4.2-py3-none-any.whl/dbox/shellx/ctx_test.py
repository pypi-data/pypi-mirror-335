from subprocess import Popen

from .call import cmd
from .ctx import GLOBAL_SHELL_CTX, ShellContext, current_shell_context, shell_context


def test_stop_runnings():
    ctx = ShellContext()
    p = Popen(["sh", "-c", "echo 10; sleep 5"])
    ctx.add(p.pid)
    assert len(ctx.running_pids) == 1
    assert ctx.terminate_runnings() == 1
    assert len(ctx.running_pids) == 0


def test_global_context():
    call1 = cmd("sleep", "0.2")
    call2 = cmd("sleep", "5")
    call1()
    call2()
    global_ctx = current_shell_context()
    assert global_ctx is GLOBAL_SHELL_CTX

    assert call1.process.pid in global_ctx.running_pids
    assert call2.process.pid in global_ctx.running_pids

    call1.wait()
    assert call1.process.pid not in global_ctx.running_pids


def test_local_context():
    with shell_context() as ctx:
        call1 = cmd("sleep", "0.2")
        call2 = cmd("sleep", "5")
        call3 = cmd("bash", "-c", "sleep 5")

        call3()
        call1()
        call2()

        assert len(ctx.started_pids) == 3
        assert len(ctx.running_pids) == 3

        call1.wait()
        assert len(ctx.running_pids) == 2

    assert len(ctx.running_pids) == 0, "Should have killed all running processes"
