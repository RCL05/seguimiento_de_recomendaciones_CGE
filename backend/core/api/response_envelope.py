from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Any


def build_envelope(
    *,
    success: bool,
    message: str,
    data: Any = None,
    errors: Any = None,
    request_id: UUID | None = None,
    pagination: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "success": success,
        "message": message,
        "data": data if success else None,
        "errors": errors if not success else None,
        "meta": {
            "request_id": str(request_id or uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "v1",
            "pagination": pagination,
        },
    }
