from __future__ import annotations

from uuid import UUID, uuid4

from .errors import ValidationError


def new_instance_uuid() -> UUID:
    return uuid4()


def parse_uuid(value: str | UUID, *, require_v4: bool = True) -> UUID:
    try:
        parsed = value if isinstance(value, UUID) else UUID(str(value))
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValidationError("invalid UUID", field="instance_id") from exc
    if require_v4 and parsed.version != 4:
        raise ValidationError("UUID must be version 4", field="instance_id")
    return parsed


def validate_uuid(value: str | UUID, *, require_v4: bool = True) -> bool:
    try:
        parse_uuid(value, require_v4=require_v4)
    except ValidationError:
        return False
    return True
