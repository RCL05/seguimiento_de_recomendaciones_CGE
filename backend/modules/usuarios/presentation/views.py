from __future__ import annotations

import json
import uuid

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from backend.core.api.exception_handler import ErrorCodes, handle_exception
from backend.core.api.request_context import get_or_create_request_id
from backend.core.api.response_envelope import error_response, success_response
from backend.core.shared.domain_types import PermissionDenied, Role, User
from backend.modules.usuarios.application.login_sso import LoginSsoUseCase
from backend.modules.usuarios.application.manage_roles import ManageRolesUseCase
from backend.modules.usuarios.models import Usuario


def _get_actor(request):
    role = request.headers.get("X-Role") or request.headers.get("HTTP_X_ROLE")
    if not role:
        raise PermissionDenied("Rol requerido en encabezados.")
    try:
        user_role = Role(role)
    except Exception:
        raise PermissionDenied("Rol inválido.")
    return User(id=str(uuid.uuid4()), role=user_role, unit_id=None)


@csrf_exempt
@require_http_methods(["POST"])
def login_sso_view(request):
    try:
        request_id = get_or_create_request_id(request)
        payload = json.loads(request.body or "{}")
        token = payload.get("token", "")
        use_case = LoginSsoUseCase()
        result = use_case.execute(token=token, request_id=request_id, ip_address=request.META.get("REMOTE_ADDR"))
        return success_response(data=result, message="Sesión iniciada")
    except Exception as exc:
        return handle_exception(exc)


@csrf_exempt
@require_http_methods(["POST"])
def admin_assign_role(request):
    try:
        request_id = get_or_create_request_id(request)
        actor_header = _get_actor(request)
        if actor_header.role != Role.DTI:
            return error_response(code=ErrorCodes.FORBIDDEN, message="Solo DTI puede asignar roles.", status=403)
        payload = json.loads(request.body or "{}")
        actor = Usuario.objects.filter(rol=Usuario.Rol.DTI).first()
        target = Usuario.objects.filter(id=payload.get("user_id")).first()
        if not actor or not target:
            return error_response(code=ErrorCodes.NOT_FOUND, message="Usuario no encontrado.", status=404)
        use_case = ManageRolesUseCase()
        use_case.assign_role(actor=actor, target=target, new_role=payload.get("role"), request_id=request_id)
        return success_response(data={"user_id": str(target.id), "role": target.rol}, message="Rol asignado")
    except Exception as exc:
        return handle_exception(exc)
