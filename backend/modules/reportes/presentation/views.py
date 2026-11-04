from __future__ import annotations

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from backend.core.api.exception_handler import ErrorCodes, handle_exception
from backend.core.api.response_envelope import error_response, success_response
from backend.core.shared.domain_types import PermissionDenied, Role, User
from backend.modules.reportes.application.export_matriz import export_matriz_cge_csv
from backend.modules.reportes.application.get_dashboard import get_dashboard


def _get_actor(request):
    role = request.headers.get("X-Role") or request.headers.get("HTTP_X_ROLE")
    unit_id = request.headers.get("X-Unit-Id") or request.headers.get("HTTP_X_UNIT_ID")
    if not role:
        raise PermissionDenied("Rol requerido en encabezados.")
    try:
        user_role = Role(role)
    except Exception:
        raise PermissionDenied("Rol inválido.")
    return User(id="sys", role=user_role, unit_id=unit_id)


@csrf_exempt
@require_http_methods(["GET"])
def tablero_view(request):
    try:
        actor = _get_actor(request)
        if actor.role not in (Role.RECTORADO, Role.DTI, Role.UAI, Role.CGE_AUDITOR):
            return error_response(
                code=ErrorCodes.FORBIDDEN,
                message="Acceso exclusivo a RECTORADO y roles autorizados.",
                status=403,
            )
        data = get_dashboard()
        return success_response(data=data, message="Tablero consultado")
    except Exception as exc:
        return handle_exception(exc)


@csrf_exempt
@require_http_methods(["POST"])
def matriz_cge_view(request):
    try:
        actor = _get_actor(request)
        if actor.role not in (Role.UAI, Role.CGE_AUDITOR, Role.RECTORADO):
            return error_response(
                code=ErrorCodes.FORBIDDEN,
                message="No tiene permisos para exportar la matriz CGE.",
                status=403,
            )
        csv_bytes = export_matriz_cge_csv()
        response = HttpResponse(csv_bytes, content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="matriz_cge.csv"'
        return response
    except Exception as exc:
        return handle_exception(exc)
