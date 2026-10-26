from __future__ import annotations

from typing import Any

REDACTED = "[REDACTED]"

SENSITIVE_FRAGMENTS = (
    "authorization",
    "cookie",
    "credential",
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "smtp",
    "private_key",
)


def _is_sensitive(key: str) -> bool:
    lowered = key.lower()
    return any(fragment in lowered for fragment in SENSITIVE_FRAGMENTS)


def redact_sensitive(value: Any) -> Any:
    """Devuelve una copia segura para logs, ocultando secretos y credenciales.

    Conserva identificadores, roles, estados y hashes, que son necesarios para
    correlacionar eventos sin exponer datos sensibles.
    """
    if isinstance(value, dict):
        return {
            key: REDACTED if _is_sensitive(str(key)) else redact_sensitive(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact_sensitive(item) for item in value]
    return value


def safe_log_context(**fields: Any) -> dict[str, Any]:
    return redact_sensitive(fields)
