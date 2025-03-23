import logging

from IPython.display import Markdown, clear_output, display

log = logging.getLogger(__name__)


class IpythonPrinter:
    def __init__(self, buffer_size: int = 100):
        self.buffer_size = buffer_size
        # state
        self._buffer: str = ""
        self._acc = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.display(True)

    def append(self, content: str):
        self._acc += len(content)
        self._buffer += content

    def clear(self):
        self._buffer = ""
        self._acc = 0

    def make_content(self, content: str):
        raise NotImplementedError

    def print(self, content: str):
        self.append(content)
        self.display()

    def display(self, force=False):
        if self._acc >= self.buffer_size or force:
            clear_output(wait=True)
            content = self.make_content(self._buffer)
            display(content)
            self._acc = 0


class MarkdownPrinter(IpythonPrinter):
    def make_content(self, content: str):
        return Markdown(content)
