import asyncio
import logging
from io import IOBase
from typing import AsyncIterable, Optional

log = logging.getLogger(__name__)


class TrackProgress:
    def __init__(self, marker, step_mb: int = 1):
        self.marker = marker
        self.total = 0
        self.step_mb = step_mb
        self.logged = set()

    def log(self, n):
        mb = n // (self.step_mb * 1024 * 1024)
        if mb and mb not in self.logged:
            log.debug("%s - Progress %s MB.", self.marker, mb * self.step_mb)
            self.logged.add(mb)


class AsyncIterableBinaryIO(IOBase):
    def __init__(self, aiterable: AsyncIterable[bytes]):
        self.aiterable = aiterable
        self.buffer = bytearray()

        self.__closed = False
        self.__done = False
        self.__started = False
        self.__offset = 0

    async def _start(self):
        if self.__started:
            return
        self.__started = True
        n = 0
        pg = TrackProgress("Download", step_mb=10)
        while not self.__closed:
            try:
                buf = await anext(self.aiterable)
                n += len(buf)
                pg.log(n)
                self.buffer.extend(buf)
            except (StopIteration, StopAsyncIteration):
                log.debug("Done reading. Total %s bytes.", n)
                break
        self.__done = True

    async def read(self, size: Optional[int] = -1) -> bytes:
        if self.__closed:
            raise ValueError("I/O operation on closed file.")

        while size > 0 and not self.__done:
            await asyncio.sleep(0.1)
            if self.__offset + size <= len(self.buffer):
                break
        while size < 0 and not self.__done:
            await asyncio.sleep(0.1)

        if size < 0:
            result = self.buffer
        else:
            result = self.buffer[self.__offset : self.__offset + size]
            self.__offset += len(result)
        return bytes(result)

    def close(self) -> None:
        self.__closed = True

    async def readable(self) -> bool:
        return True

    async def writable(self) -> bool:
        return False

    async def seekable(self) -> bool:
        return False

    async def readinto(self, b: bytearray) -> int:
        data = await self.read(len(b))
        n = len(data)
        b[:n] = data
        return n

    async def __aenter__(self) -> "AsyncIterableBinaryIO":
        # log.debug("Entering context")
        self.__task = asyncio.create_task(self._start())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        # log.debug("Exiting context")
        self.close()


# Example usage


async def async_data_chunks():
    yield b"Hello, "
    yield b"world!"
    yield b" This is "
    yield b"a test."


async def main():
    stream = AsyncIterableBinaryIO(async_data_chunks())

    # Read in chunks
    print(await stream.read(7))  # Output: b'Hello, '
    print(await stream.read(6))  # Output: b'world!'
    print(await stream.read())  # Output: b' This is a test.'

    # Ensure to close the stream
    await stream.close()
