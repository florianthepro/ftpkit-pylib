from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Mapping
from uuid import UUID

from .errors import IntegrityError, MigrationError, ValidationError
from .identifiers import parse_uuid
from .io import atomic_write_json, read_json
from .locking import FileLock
from .models import Capability, parse_datetime, utc_now
from .validators import validate_app_id, validate_http_url, validate_port, validate_url_path

CURRENT_REGISTRY_VERSION = 1


@dataclass(frozen=True, slots=True)
class RegistryEntry:
    app_id: str
    instance_id: UUID
    display_name: str
    version: str
    protocol_version: int
    install_path: str
    data_path: str
    frontend_path: str
    backend_path: str
    runtime_path: str
    backup_path: str
    service_name: str
    service_user: str
    bind_ip: str
    backend_port: int | None
    unix_socket: str | None
    public_port: int
    public_url: str
    url_path: str
    tls_mode: str
    capabilities: frozenset[Capability]
    installed_at: datetime
    updated_at: datetime
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        validate_app_id(self.app_id)
        parse_uuid(self.instance_id)
        if self.protocol_version < 1 or not self.display_name.strip() or not self.version.strip():
            raise ValidationError("invalid registry entry identity")
        if (self.backend_port is None) == (self.unix_socket is None):
            raise ValidationError("exactly one backend endpoint is required")
        if self.backend_port is not None:
            validate_port(self.backend_port)
        validate_port(self.public_port)
        validate_http_url(self.public_url)
        validate_url_path(self.url_path)
        if self.updated_at < self.installed_at:
            raise ValidationError("updated_at cannot precede installed_at")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "RegistryEntry":
        try:
            return cls(
                app_id=str(data["app_id"]), instance_id=parse_uuid(str(data["instance_id"])), display_name=str(data["display_name"]),
                version=str(data["version"]), protocol_version=int(data["protocol_version"]), install_path=str(data["install_path"]),
                data_path=str(data["data_path"]), frontend_path=str(data["frontend_path"]), backend_path=str(data["backend_path"]),
                runtime_path=str(data["runtime_path"]), backup_path=str(data["backup_path"]), service_name=str(data["service_name"]),
                service_user=str(data["service_user"]), bind_ip=str(data["bind_ip"]),
                backend_port=None if data.get("backend_port") is None else int(data["backend_port"]),
                unix_socket=None if data.get("unix_socket") is None else str(data["unix_socket"]), public_port=int(data["public_port"]),
                public_url=str(data["public_url"]), url_path=str(data["url_path"]), tls_mode=str(data["tls_mode"]),
                capabilities=frozenset(Capability(x) for x in data["capabilities"]), installed_at=parse_datetime(data["installed_at"]),
                updated_at=parse_datetime(data["updated_at"]), metadata=dict(data.get("metadata", {})))
        except (KeyError, TypeError, ValueError) as exc:
            raise ValidationError("invalid registry entry") from exc

    def to_dict(self) -> dict[str, Any]:
        return {**self.__dict__} if hasattr(self, "__dict__") else {
            "app_id": self.app_id, "instance_id": str(self.instance_id), "display_name": self.display_name, "version": self.version,
            "protocol_version": self.protocol_version, "install_path": self.install_path, "data_path": self.data_path,
            "frontend_path": self.frontend_path, "backend_path": self.backend_path, "runtime_path": self.runtime_path,
            "backup_path": self.backup_path, "service_name": self.service_name, "service_user": self.service_user,
            "bind_ip": self.bind_ip, "backend_port": self.backend_port, "unix_socket": self.unix_socket, "public_port": self.public_port,
            "public_url": self.public_url, "url_path": self.url_path, "tls_mode": self.tls_mode,
            "capabilities": sorted(x.value for x in self.capabilities), "installed_at": self.installed_at.isoformat(),
            "updated_at": self.updated_at.isoformat(), "metadata": dict(self.metadata)
        }


@dataclass(frozen=True, slots=True)
class Registry:
    schema_version: int
    revision: int
    updated_at: datetime
    instances: Mapping[UUID, RegistryEntry] = field(default_factory=dict)

    @classmethod
    def empty(cls) -> "Registry":
        return cls(CURRENT_REGISTRY_VERSION, 0, utc_now(), {})

    def __post_init__(self) -> None:
        if self.schema_version != CURRENT_REGISTRY_VERSION or self.revision < 0:
            raise ValidationError("unsupported registry schema or revision")
        if any(key != entry.instance_id for key, entry in self.instances.items()):
            raise IntegrityError("registry key differs from entry UUID")

    def with_entry(self, entry: RegistryEntry) -> "Registry":
        values = dict(self.instances)
        values[entry.instance_id] = entry
        return Registry(self.schema_version, self.revision + 1, utc_now(), values)

    def without_entry(self, instance_id: UUID | str) -> "Registry":
        uid = parse_uuid(instance_id)
        if uid not in self.instances:
            raise ValidationError("unknown instance UUID", field="instance_id")
        values = dict(self.instances)
        del values[uid]
        return Registry(self.schema_version, self.revision + 1, utc_now(), values)

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": self.schema_version, "revision": self.revision, "updated_at": self.updated_at.isoformat(),
                "instances": [entry.to_dict() for entry in sorted(self.instances.values(), key=lambda x: str(x.instance_id))]}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Registry":
        migrated = migrate_registry(dict(data))
        entries = [RegistryEntry.from_dict(x) for x in migrated.get("instances", [])]
        if len({x.instance_id for x in entries}) != len(entries):
            raise IntegrityError("duplicate instance UUID")
        return cls(int(migrated["schema_version"]), int(migrated["revision"]), parse_datetime(migrated["updated_at"]), {x.instance_id: x for x in entries})


Migration = Callable[[dict[str, Any]], dict[str, Any]]
_MIGRATIONS: dict[int, Migration] = {}


def register_registry_migration(source_version: int, migration: Migration) -> None:
    if source_version < 0 or source_version in _MIGRATIONS:
        raise ValueError("invalid or duplicate migration")
    _MIGRATIONS[source_version] = migration


def migrate_registry(data: dict[str, Any]) -> dict[str, Any]:
    try:
        version = int(data.get("schema_version", 1))
    except (TypeError, ValueError) as exc:
        raise MigrationError("invalid registry schema version") from exc
    if version > CURRENT_REGISTRY_VERSION:
        raise MigrationError("registry schema is newer than this library")
    while version < CURRENT_REGISTRY_VERSION:
        migration = _MIGRATIONS.get(version)
        if migration is None:
            raise MigrationError(f"missing registry migration from version {version}")
        data = migration(dict(data))
        new_version = int(data.get("schema_version", version))
        if new_version <= version:
            raise MigrationError("migration did not advance schema version")
        version = new_version
    return data


class RegistryStore:
    def __init__(self, path: str | Path, *, lock_timeout: float = 10.0):
        self.path = Path(path)
        self.lock_path = self.path.with_suffix(self.path.suffix + ".lock")
        self.lock_timeout = lock_timeout

    def load(self) -> Registry:
        with FileLock(self.lock_path, timeout=self.lock_timeout):
            return Registry.from_dict(read_json(self.path))

    def save(self, registry: Registry, *, expected_revision: int | None = None) -> None:
        with FileLock(self.lock_path, timeout=self.lock_timeout):
            if expected_revision is not None and self.path.exists():
                current = Registry.from_dict(read_json(self.path))
                if current.revision != expected_revision:
                    raise IntegrityError("registry revision conflict")
            atomic_write_json(self.path, registry.to_dict(), mode=0o600, backup=self.path.exists())
