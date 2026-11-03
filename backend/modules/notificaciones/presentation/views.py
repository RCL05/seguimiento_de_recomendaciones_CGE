from __future__ import annotations

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from backend.core.api.exception_handler import handle_exception
from backend.core.api.response_envelope import success_response
from backend.core.shared.domain_types import PermissionDenied, Role, User
from backend.modules.notificaciones.models import Notificacion


def _get_actor(request):
    role = request.headers.get("X-Role") or request.headers.get("HTTP_X_ROLE")
    if not role:
        raise PermissionDenied("Rol requerido en encabezados.")
    try:
        user_role = Role(role)
    except Exception:
        raise PermissionDenied("Rol inválido.")
    return User(id="sys", role=user_role, unit_id=None)


@csrf_exempt
@require_http_methods(["GET"])
def bandeja_notificaciones(request):
    try:
        actor = _get_actor(request)
        qs = Notificacion.objects.filter(destinatario_id=actor.id).order_by("-programada_en")
        data = [
            {
                "id": str(n.id),
                "tipo": n.tipo,
                "estado": n.estado,
                "programada_en": n.programada_en.isoformat(),
                "enviada_en": n.enviada_en.isoformat() if n.enviada_en else None,
                "intentos": n.intentos,
            }
            for n in qs
        ]
        return success_response(data={"items": data, "count": len(data)}, message="Bandeja consultada")
    except Exception as exc:
        return handle_exception(exc)
