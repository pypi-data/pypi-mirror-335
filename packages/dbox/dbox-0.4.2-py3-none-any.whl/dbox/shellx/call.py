import io
import logging
import shlex
import subprocess
from subprocess import PIPE
from typing import Any, BinaryIO, Dict, List, Optional

from attrs import define, field

from .ctx import current_shell_context

log = logging.getLogger(__name__)


@define(kw_only=True, slots=False)
class Call:
    finalized: bool = False

    # build
    def set_stdout(self, value):
        raise NotImplementedError

    def set_stderr(self, value):
        raise NotImplementedError

    # execution
    def __call__(self, stdin: Optional[bytes | str | BinaryIO] = None):
        assert not self.finalized, "Cannot call a process twice"
        self.finalized = True
        # once this is called, no mutation should be allowed

    def wait(self, timeout: float = None):
        raise NotImplementedError

    def ok(self, stdin=None, timeout: float = None):
        """Invoke the command and wait for successful completion.
        Returns the stdout as bytes.
        """
        self.__call__(stdin=stdin)
        self.wait(timeout=timeout)
        if self.returncode != 0:
            raise RuntimeError(f"return code: {self.returncode}")
        return self.out

    # results
    process_stdout: Optional[BinaryIO] = None
    process_stderr: Optional[BinaryIO] = None

    @property
    def out(self) -> Optional[bytes]:
        self.wait()
        if hasattr(self, "_out"):
            return self._out
        if self.process_stdout is None:
            return None
        self._out = self.process_stdout.read()
        return self._out

    @property
    def err(self) -> Optional[bytes]:
        if hasattr(self, "_err"):
            return self._err
        if self.process_stderr is None:
            return None
        self._err = self.process_stderr.read()
        return self._err

    @property
    def returncode(self) -> Optional[int]:
        raise NotImplementedError


@define(kw_only=True)
class PipeCall(Call):
    calls: List["Call"]

    def __getitem__(self, index):
        return self.calls[index]

    def __iter__(self):
        return iter(self.calls)

    def set_stdout(self, value):
        self.calls[-1].set_stdout(value)

    def set_stderr(self, value):
        self.calls[-1].set_stderr(value)

    def __call__(self, stdin=None):
        super().__call__(stdin)
        prev_stdout = None
        for i, call in enumerate(self.calls):
            if i > 0:
                call(stdin=prev_stdout)
            else:
                call(stdin=stdin)
            prev_stdout = call.process_stdout

        self.process_stdout = self.calls[-1].process_stdout
        self.process_stderr = self.calls[-1].process_stderr

        for call in self.calls[:-1]:
            call.process_stdout.close()

    def wait(self, timeout: float = None):
        for call in self.calls:
            call.wait(timeout=timeout)

    @property
    def returncode(self):
        # until all calls are done
        for call in self.calls:
            if call.returncode is None:
                return None
        # the first non-zero return code
        for call in self.calls:
            if call.returncode != 0:
                log.debug("Pipe return code: %s from %s", call.returncode, call)
                return call.returncode
        return 0


@define(kw_only=True, slots=False)
class SingleCall(Call):
    # mutable, and will be set if the call is used in a pipe
    stdout: Optional[int] = PIPE
    # normally set to None if we are not interested in the stderr
    stderr: Optional[int] = None

    executable: Optional[str] = None
    args: List[str] = field(factory=list)
    popen_kwargs: Dict[str, Any] = field(factory=dict)

    completed: bool = field(init=False, default=False, repr=False)

    def set_stdout(self, value):
        self.stdout = value

    def set_stderr(self, value):
        self.stderr = value

    def __call__(self, stdin: Optional[bytes | str | BinaryIO] = None):
        # should be called last
        # once this is called, no mutation should be allowed
        super().__call__(stdin)
        # if stdin is not None:
        if stdin is None:
            _stdin = None
        elif isinstance(stdin, io.BufferedReader):
            # pipe objects are instances of BufferedReader
            _stdin = stdin
        else:
            _stdin = PIPE
        self.process = subprocess.Popen(
            args=self.args,
            executable=self.executable,
            stdin=_stdin,
            stdout=self.stdout,
            stderr=self.stderr,
            # bufsize=819200,
            **self.popen_kwargs,
        )
        log.debug("Started process %s", self)
        self.shell_context = current_shell_context()
        self.shell_context.add(self.process.pid)
        self.process_stdout = self.process.stdout
        self.process_stderr = self.process.stderr
        if isinstance(stdin, (str, bytes)):
            # might block
            stdin = stdin.encode("utf-8") if isinstance(stdin, str) else stdin
            self.process.stdin.write(stdin)
            self.process.stdin.close()

    def wait(self, timeout: float = None):
        if self.completed:
            return
        self.process.wait(timeout=timeout)
        self.shell_context.complete(self.process.pid)
        self.completed = True

    @property
    def returncode(self) -> Optional[int]:
        return self.process.poll()


def cmd(*args, **kwargs):
    """Create a command object. For advanced usage, such as allow running in backgroud, pipe, etc."""
    if len(args) == 1 and not kwargs:
        args = shlex.split(args[0])
    return SingleCall(args=args, **kwargs)


def pipe(*calls):
    return PipeCall(calls=calls)


def fire(*args, **kwargs) -> None:
    """Create a command object, execute it, ensure it completed successfully.
    No PIPE will be created.
    """
    cl = cmd(*args, stdout=None, **kwargs)
    return cl.ok()


def invoke(*args, **kwargs) -> bytes:
    """Create a command object, execute it, ensure it completed successfully.
    The stdout will be captured and returned as bytes. No other PIPE will be created."""
    cl = cmd(*args, **kwargs)
    return cl.ok()
