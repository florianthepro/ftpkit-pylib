from __future__ import annotations

import os
from pathlib import Path

from .errors import ValidationError


def safe_path(path: str | os.PathLike[str], *, roots: list[str | os.PathLike[str]] | tuple[str | os.PathLike[str], ...], must_exist: bool = False, allow_root: bool = False) -> Path:
    candidate = Path(path).expanduser().resolve(strict=must_exist)
    allowed = [Path(root).expanduser().resolve(strict=False) for root in roots]
    if not allowed:
        raise ValidationError("at least one allowed root is required", field="roots")
    for root in allowed:
        try:
            relative = candidate.relative_to(root)
        except ValueError:
            continue
        if not allow_root and relative == Path("."):
            raise ValidationError("the allowed root itself is not permitted", field="path")
        return candidate
    raise ValidationError("path is outside allowed roots", field="path", context={"path": str(candidate)})


def instance_path(base: str | os.PathLike[str], app_id: str, instance_id: object) -> Path:
    from .identifiers import parse_uuid
    from .validators import validate_app_id
    app = validate_app_id(app_id)
    uid = parse_uuid(str(instance_id))
    return Path(base) / f"{app}-{uid}"
