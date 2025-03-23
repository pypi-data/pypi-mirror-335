from subprocess import PIPE

import pytest

from . import cmd, fire, invoke, pipe
from .call import PipeCall, SingleCall


def test_run_basic_cmd():
    call1 = SingleCall(executable="/bin/echo", args=["prog", "hello"])
    call1()
    call1.wait()
    assert call1.out == b"hello\n"
    assert call1.err is None
    assert call1.returncode == 0

    call2 = SingleCall(args=["echo", "hello"])
    call2()
    call2.wait()
    assert call2.out == b"hello\n"
    assert call2.err is None


def test_chain_output():
    c1 = SingleCall(args=["echo", "-n", "hello"])
    c1()
    c2 = SingleCall(args=["wc", "-c"])
    c2(c1.out)
    assert c2.out.strip() == b"5"


def test_chain_stdout():
    c1 = cmd("echo", "-n", "hello")
    c1()
    c2 = cmd("wc", "-c")
    c2(c1.process_stdout)
    c1.process_stdout.close()
    c2.wait(1000)
    print("ok")
    assert c2.out.strip() == b"5"


def test_run_with_cwd():
    call = cmd("pwd", popen_kwargs={"cwd": "/"})
    call()
    call.wait()
    assert call.out == b"/\n"
    assert call.err is None
    assert call.returncode == 0


def test_run_with_env():
    call = cmd("env", popen_kwargs={"env": {"PATH": "/usr/bin"}})
    call()
    call.wait()
    assert call.out.strip() == b"PATH=/usr/bin"
    assert call.err is None
    assert call.returncode == 0


@pytest.mark.timeout(5)
def test_chain():
    p = pipe(cmd("cat", "conftest.py"), cmd("grep", "-i", "def"), cmd("tee"))

    p()
    print(p.out.decode())
    print(p.err, p.returncode)
    assert p.returncode == 0


@pytest.mark.timeout(5)
def test_pipefail():
    p = pipe(cmd("false"), cmd("true"))
    p()
    print(p.out, p.err, p.returncode)
    assert p.returncode == 1


@pytest.mark.timeout(5)
def test_pipefail_no_wait():
    p = pipe(cmd("false"), cmd("cat"))
    p()
    print(p.out, p.err, p.returncode)
    assert p.returncode == 1


@pytest.mark.timeout(5)
def test_pipe_correct():
    p = pipe(cmd("echo", "-n", "3"), cmd("tee"))
    p()
    print(p.out, p.err, p.returncode)
    assert p.out == b"3"
    assert p.err is None
    assert p.returncode == 0


@pytest.mark.timeout(5)
def test_pipe_combination():
    c1 = cmd("echo", "-n", "hello world")
    c2 = cmd("false")
    c3 = cmd("true")
    c4 = cmd("tee", "/dev/stderr")

    p = pipe(pipe(pipe(c1, c2), c3), c4)
    p()
    p.wait()
    assert p[0].returncode == 1
    assert p[1].returncode == 0
    assert p.returncode == 1

    assert p[0][0].returncode == 1
    assert p[0][0][0].returncode == 0


@pytest.mark.timeout(5)
def test_pipe_behavior():
    c1 = cmd("echo", "-n", "hello world")
    c2 = cmd("tee", "/dev/stderr")
    c3 = cmd("false")
    c4 = cmd("echo", "-n", "hello moon")
    c5 = cmd("tee")

    p = pipe(c1, c2, c3, c4, c5)

    p()
    p.wait()

    assert p[0].returncode == 0
    assert p[1].returncode == 0
    assert p[2].returncode == 1
    assert p[3].returncode == 0
    assert p[4].returncode == 0

    assert p.returncode == 1

    assert p.out == b"hello moon"


@pytest.mark.timeout(5)
def test_pipe_with_false():
    p1 = pipe(cmd("bash", "-c", "sleep 0.1; echo 3"), cmd("tee"), cmd("false"))
    p1()
    p1.wait()
    assert p1.returncode == -13  # SIGPIPE

    p2 = pipe(cmd("echo", "-n", "3"), cmd("tee"), cmd("false"))
    p2()
    p2.wait()
    assert p2.returncode == 1  # no SIGPIPE since tee is fast enough


def test_fire_invoke():
    fire("echo", "hello")
    # out = invoke("python", "-c", "print('hello')")
    # assert out == b"hello\n"
