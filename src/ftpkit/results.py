from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from .errors import ErrorDetail

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Result(Generic[T]):
    value: T | None = None
    error: ErrorDetail | None = None

    def __post_init__(self) -> None:
        if (self.value is None) == (self.error is None):
            raise ValueError("exactly one of value or error is required")

    @property
    def ok(self) -> bool:
        return self.error is None

    def unwrap(self) -> T:
        if self.error is not None:
            raise RuntimeError(f"{self.error.code}: {self.error.message}")
        return self.value  # type: ignore[return-value]

    @classmethod
    def success(cls, value: T) -> "Result[T]":
        return cls(value=value)

    @classmethod
    def failure(cls, error: ErrorDetail) -> "Result[T]":
        return cls(error=error)
