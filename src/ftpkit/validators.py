from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlsplit

from .errors import ValidationError

_DOMAIN_LABEL = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")
_APP_ID = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")


def validate_app_id(value: str) -> str:
    text = str(value)
    if len(text) > 63 or not _APP_ID.fullmatch(text):
        raise ValidationError("app id must be lowercase kebab-case", field="app_id")
    return text


def validate_ip(value: str, *, allow_unspecified: bool = False, allow_loopback: bool = True) -> str:
    try:
        address = ipaddress.ip_address(value)
    except ValueError as exc:
        raise ValidationError("invalid IP address", field="ip") from exc
    if address.is_unspecified and not allow_unspecified:
        raise ValidationError("unspecified IP address is not allowed", field="ip")
    if address.is_loopback and not allow_loopback:
        raise ValidationError("loopback IP address is not allowed", field="ip")
    return address.compressed


def validate_domain(value: str, *, allow_localhost: bool = False) -> str:
    domain = value.strip().rstrip(".").lower()
    if domain == "localhost" and allow_localhost:
        return domain
    if len(domain) > 253 or not domain or ipaddress_like(domain):
        raise ValidationError("invalid domain", field="domain")
    labels = domain.split(".")
    if len(labels) < 2 or any(not _DOMAIN_LABEL.fullmatch(label) for label in labels):
        raise ValidationError("invalid domain", field="domain")
    return domain


def ipaddress_like(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def validate_port(value: int | str, *, allow_privileged: bool = True) -> int:
    if isinstance(value, bool):
        raise ValidationError("invalid port", field="port")
    try:
        port = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError("invalid port", field="port") from exc
    if not 1 <= port <= 65535:
        raise ValidationError("port must be between 1 and 65535", field="port")
    if not allow_privileged and port < 1024:
        raise ValidationError("privileged port is not allowed", field="port")
    return port


def validate_url_path(value: str, *, allow_root: bool = True) -> str:
    if not isinstance(value, str) or not value.startswith("/"):
        raise ValidationError("URL path must start with /", field="url_path")
    if value == "/":
        if allow_root:
            return value
        raise ValidationError("root URL path is not allowed", field="url_path")
    if len(value) > 2048 or "?" in value or "#" in value or "\\" in value or "//" in value:
        raise ValidationError("invalid URL path", field="url_path")
    normalized = value.rstrip("/")
    parts = normalized.split("/")[1:]
    if any(part in {"", ".", ".."} for part in parts):
        raise ValidationError("invalid URL path segment", field="url_path")
    return normalized or "/"


def validate_http_url(value: str, *, https_only: bool = False) -> str:
    parsed = urlsplit(value)
    allowed = {"https"} if https_only else {"http", "https"}
    if parsed.scheme not in allowed or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise ValidationError("invalid HTTP URL", field="url")
    if parsed.port is not None:
        validate_port(parsed.port)
    return value
