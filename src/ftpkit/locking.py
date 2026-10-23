from __future__ import annotations

import os
import time
from pathlib import Path
from types import TracebackType

from .errors import LockTimeoutError

try:
    import fcntl
except ImportError as exc:
    raise RuntimeError("ftpkit locking requires a POSIX platform") from exc


class FileLock:
    def __init__(self, path: str | os.PathLike[str], *, timeout: float = 10.0, poll_interval: float = 0.05):
        if timeout < 0 or poll_interval <= 0:
            raise ValueError("invalid lock timing")
        self.path = Path(path)
        self.timeout = timeout
        self.poll_interval = poll_interval
        self._handle = None

    def acquire(self) -> "FileLock":
        if self._handle is not None:
            return self
        self.path.parent.mkdir(parents=True, exist_ok=True)
        handle = self.path.open("a+", encoding="utf-8")
        deadline = time.monotonic() + self.timeout
        while True:
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                handle.seek(0)
                handle.truncate()
                handle.write(str(os.getpid()))
                handle.flush()
                self._handle = handle
                return self
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    handle.close()
                    raise LockTimeoutError(f"timed out acquiring lock: {self.path}")
                time.sleep(self.poll_interval)

    def release(self) -> None:
        if self._handle is None:
            return
        fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN)
        self._handle.close()
        self._handle = None

    def __enter__(self) -> "FileLock":
        return self.acquire()

    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, traceback: TracebackType | None) -> None:
        self.release()
