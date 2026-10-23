from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .errors import SerializationError


def atomic_write_bytes(path: str | os.PathLike[str], data: bytes, *, mode: int = 0o600, backup: bool = False) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    temp_path = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_path, mode)
        if backup and target.exists():
            backup_path = target.with_suffix(target.suffix + ".bak")
            atomic_write_bytes(backup_path, target.read_bytes(), mode=mode, backup=False)
        os.replace(temp_path, target)
        directory_fd = os.open(target.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass


def atomic_write_text(path: str | os.PathLike[str], data: str, *, encoding: str = "utf-8", mode: int = 0o600, backup: bool = False) -> None:
    atomic_write_bytes(path, data.encode(encoding), mode=mode, backup=backup)


def atomic_write_json(path: str | os.PathLike[str], value: Any, *, mode: int = 0o600, backup: bool = False, indent: int = 2) -> None:
    try:
        payload = json.dumps(value, ensure_ascii=False, indent=indent, sort_keys=True, allow_nan=False) + "\n"
    except (TypeError, ValueError) as exc:
        raise SerializationError("value is not valid JSON") from exc
    atomic_write_text(path, payload, mode=mode, backup=backup)


def read_json(path: str | os.PathLike[str]) -> Any:
    try:
        with Path(path).open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise SerializationError(f"cannot read JSON: {path}") from exc
