from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Any

from django.http import JsonResponse


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


def success_response(
    *,
    data=None,
    message: str,
    request_id: UUID | None = None,
    status: int = 200,
    pagination: dict | None = None,
) -> JsonResponse:
    return JsonResponse(
        build_envelope(
            success=True,
            message=message,
            data=data,
            request_id=request_id,
            pagination=pagination,
        ),
        status=status,
        safe=False,
    )


def error_response(
    *,
    code: str,
    message: str,
    status: int = 400,
    request_id: UUID | None = None,
    details=None,
) -> JsonResponse:
    errors = {"code": code, "detail": message}
    if details is not None:
        errors["details"] = details
    return JsonResponse(
        build_envelope(
            success=False,
            message=message,
            errors=errors,
            request_id=request_id,
        ),
        status=status,
        safe=False,
    )
