from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class ErrorDetail:
    code: str
    message: str
    field: str | None = None
    context: Mapping[str, Any] = dc_field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.field is not None:
            value["field"] = self.field
        if self.context:
            value["context"] = dict(self.context)
        return value


class FtpkitError(Exception):
    code = "ftpkit_error"

    def __init__(self, message: str, *, field: str | None = None, context: Mapping[str, Any] | None = None):
        super().__init__(message)
        self.detail = ErrorDetail(self.code, message, field, context or {})


class ValidationError(FtpkitError):
    code = "validation_error"


class SerializationError(FtpkitError):
    code = "serialization_error"


class LockTimeoutError(FtpkitError):
    code = "lock_timeout"


class MigrationError(FtpkitError):
    code = "migration_error"


class IntegrityError(FtpkitError):
    code = "integrity_error"
