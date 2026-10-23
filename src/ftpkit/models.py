from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Mapping
from uuid import UUID

from .errors import ValidationError
from .identifiers import parse_uuid
from .validators import validate_app_id, validate_http_url, validate_port, validate_url_path


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_datetime(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        result = value
    else:
        try:
            result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError) as exc:
            raise ValidationError("invalid ISO datetime", field="datetime") from exc
    if result.tzinfo is None:
        raise ValidationError("datetime must include timezone", field="datetime")
    return result.astimezone(timezone.utc)


class Capability(str, Enum):
    STATUS = "status"
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    HEALTH = "health"
    LOGS = "logs"
    BACKUP = "backup"
    RESTORE = "restore"
    UPGRADE = "upgrade"
    CONFIGURE = "configure"
    REMOVE = "remove"
    IMPORT = "import"
    EXPORT = "export"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ChangeAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    INSTALL = "install"
    REMOVE = "remove"
    START = "start"
    STOP = "stop"
    RESTART = "restart"


@dataclass(frozen=True, slots=True)
class CertificateMetadata:
    subject: str
    issuer: str
    serial_number: str
    not_before: datetime
    not_after: datetime
    sha256_fingerprint: str
    san: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.not_after <= self.not_before:
            raise ValidationError("certificate expiry must follow start")
        normalized = self.sha256_fingerprint.replace(":", "").lower()
        if len(normalized) != 64 or any(c not in "0123456789abcdef" for c in normalized):
            raise ValidationError("invalid SHA-256 fingerprint", field="sha256_fingerprint")


@dataclass(frozen=True, slots=True)
class BackupMetadata:
    backup_id: UUID
    instance_id: UUID
    created_at: datetime
    path: str
    sha256: str
    size: int
    app_version: str

    def __post_init__(self) -> None:
        parse_uuid(self.backup_id)
        parse_uuid(self.instance_id)
        if self.size < 0:
            raise ValidationError("backup size cannot be negative", field="size")
        if len(self.sha256) != 64 or any(c not in "0123456789abcdef" for c in self.sha256.lower()):
            raise ValidationError("invalid backup digest", field="sha256")


@dataclass(frozen=True, slots=True)
class ChangeItem:
    action: ChangeAction
    resource_type: str
    resource: str
    description: str
    requires_confirmation: bool = False


@dataclass(frozen=True, slots=True)
class ChangePlan:
    plan_id: UUID
    app_id: str
    instance_id: UUID | None
    action: str
    risk: RiskLevel
    changes: tuple[ChangeItem, ...]
    downtime_seconds: int = 0
    backup_required: bool = False
    rollback_strategy: str = ""
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        parse_uuid(self.plan_id)
        validate_app_id(self.app_id)
        if self.instance_id is not None:
            parse_uuid(self.instance_id)
        if self.downtime_seconds < 0:
            raise ValidationError("downtime cannot be negative")

    @property
    def confirmation_required(self) -> bool:
        return any(item.requires_confirmation for item in self.changes)


@dataclass(frozen=True, slots=True)
class ConfirmationEvidence:
    plan_id: UUID
    confirmed_at: datetime
    actor: str
    plan_digest: str

    def __post_init__(self) -> None:
        parse_uuid(self.plan_id)
        if not self.actor.strip():
            raise ValidationError("confirmation actor is required")
        if len(self.plan_digest) != 64 or any(c not in "0123456789abcdef" for c in self.plan_digest.lower()):
            raise ValidationError("invalid plan digest")


@dataclass(frozen=True, slots=True)
class AppManifest:
    app_id: str
    display_name: str
    app_version: str
    manifest_version: int
    protocol_version: int
    backend_type: str
    start_command: tuple[str, ...]
    health_path: str
    required_directories: tuple[str, ...]
    persistent_directories: tuple[str, ...]
    capabilities: frozenset[Capability]
    supports_url_paths: bool = True
    tls_modes: tuple[str, ...] = ("proxy",)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        validate_app_id(self.app_id)
        if not self.display_name.strip() or not self.app_version.strip() or self.manifest_version < 1 or self.protocol_version < 1:
            raise ValidationError("invalid manifest identity or version")
        if not self.start_command or any(not part for part in self.start_command):
            raise ValidationError("start command must be a non-empty argv sequence")
        validate_url_path(self.health_path)
        for path in self.required_directories + self.persistent_directories:
            if Path(path).is_absolute() or ".." in Path(path).parts:
                raise ValidationError("manifest directories must be safe relative paths", field="directories")
        if not self.capabilities:
            raise ValidationError("at least one capability is required")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "AppManifest":
        required = {"app_id", "display_name", "app_version", "manifest_version", "protocol_version", "backend_type", "start_command", "health_path", "required_directories", "persistent_directories", "capabilities"}
        missing = required - data.keys()
        if missing:
            raise ValidationError("manifest fields missing", context={"missing": sorted(missing)})
        try:
            capabilities = frozenset(Capability(value) for value in data["capabilities"])
            return cls(
                app_id=str(data["app_id"]), display_name=str(data["display_name"]), app_version=str(data["app_version"]),
                manifest_version=int(data["manifest_version"]), protocol_version=int(data["protocol_version"]), backend_type=str(data["backend_type"]),
                start_command=tuple(str(x) for x in data["start_command"]), health_path=str(data["health_path"]),
                required_directories=tuple(str(x) for x in data["required_directories"]), persistent_directories=tuple(str(x) for x in data["persistent_directories"]),
                capabilities=capabilities, supports_url_paths=bool(data.get("supports_url_paths", True)),
                tls_modes=tuple(str(x) for x in data.get("tls_modes", ["proxy"])), metadata=dict(data.get("metadata", {})))
        except (TypeError, ValueError, KeyError) as exc:
            raise ValidationError("invalid manifest") from exc

    def to_dict(self) -> dict[str, Any]:
        return {
            "app_id": self.app_id, "display_name": self.display_name, "app_version": self.app_version,
            "manifest_version": self.manifest_version, "protocol_version": self.protocol_version, "backend_type": self.backend_type,
            "start_command": list(self.start_command), "health_path": self.health_path,
            "required_directories": list(self.required_directories), "persistent_directories": list(self.persistent_directories),
            "capabilities": sorted(x.value for x in self.capabilities), "supports_url_paths": self.supports_url_paths,
            "tls_modes": list(self.tls_modes), "metadata": dict(self.metadata)
        }


@dataclass(frozen=True, slots=True)
class ManagementRequest:
    protocol_version: int
    operation: Capability
    instance_id: UUID
    request_id: UUID
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.protocol_version < 1:
            raise ValidationError("invalid protocol version")
        parse_uuid(self.instance_id)
        parse_uuid(self.request_id)


@dataclass(frozen=True, slots=True)
class ManagementResponse:
    protocol_version: int
    request_id: UUID
    success: bool
    data: Mapping[str, Any] = field(default_factory=dict)
    error: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.protocol_version < 1:
            raise ValidationError("invalid protocol version")
        parse_uuid(self.request_id)
        if self.success == (self.error is not None):
            raise ValidationError("successful responses cannot have errors and failed responses must have errors")
