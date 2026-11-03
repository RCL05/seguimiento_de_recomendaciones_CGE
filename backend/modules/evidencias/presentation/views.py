from __future__ import annotations

import json
import uuid

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from backend.core.api.exception_handler import ErrorCodes, handle_exception
from backend.core.api.request_context import get_or_create_request_id
from backend.core.api.response_envelope import error_response, success_response
from backend.core.shared.domain_types import PermissionDenied, Role, User
from backend.modules.evidencias.application.issue_dictamen import IssueDictamen
from backend.modules.usuarios.models import Usuario


def _get_actor_from_headers(request):
    role = request.headers.get("X-Role") or request.headers.get("HTTP_X_ROLE")
    unit_id = request.headers.get("X-Unit-Id") or request.headers.get("HTTP_X_UNIT_ID")
    if not role:
        raise PermissionDenied("Rol requerido en encabezados.")
    try:
        user_role = Role(role)
    except Exception:
        raise PermissionDenied("Rol inválido.")
    return User(id=str(uuid.uuid4()), role=user_role, unit_id=unit_id)


@csrf_exempt
@require_http_methods(["PATCH"])
def dictamen_view(request, recommendation_id):
    try:
        request_id = get_or_create_request_id(request)
        actor_header = _get_actor_from_headers(request)
        if actor_header.role != Role.UAI:
            return error_response(
                code=ErrorCodes.FORBIDDEN,
                message="Solo UAI puede emitir dictámenes.",
                status=403,
            )

        payload = json.loads(request.body or "{}")
        evidence_id = payload.get("evidence_id")
        approved = bool(payload.get("approved", False))
        observations = payload.get("observations", "") or ""

        if not evidence_id:
            return error_response(
                code=ErrorCodes.VALIDATION_ERROR,
                message="evidence_id es obligatorio.",
                status=400,
            )

        actor = Usuario.objects.filter(rol=Usuario.Rol.UAI).first()
        if actor is None:
            actor = Usuario.objects.first()

        use_case = IssueDictamen()
        dictamen = use_case.execute(
            actor=actor,
            request_id=request_id,
            recommendation_id=uuid.UUID(str(recommendation_id)),
            evidence_id=uuid.UUID(str(evidence_id)),
            approved=approved,
            observations=observations,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return success_response(
            data={
                "dictamen_id": str(dictamen.id),
                "recomendacion_id": str(dictamen.recomendacion_id),
                "resultado": dictamen.resultado,
                "estado_recomendacion": dictamen.recomendacion.estado,
            },
            message="Dictamen emitido correctamente",
            status=201,
        )
    except Exception as exc:
        return handle_exception(exc)
