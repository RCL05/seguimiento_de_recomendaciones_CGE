from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from backend.core.api.request_context import request_id_from
from backend.core.api.response_envelope import build_envelope
from backend.core.api.views import _persistent_user
from backend.core.shared.domain_types import Role
from backend.modules.notificaciones.models import Notificacion


def notification_inbox(request):
    """Bandeja de notificaciones del usuario autenticado."""
    _, actor = _persistent_user(request)
    notifications = Notificacion.objects.filter(
        destinatario=actor
    ).order_by("-programada_en")[:100]
    data = [
        {
            "id": str(item.id),
            "type": item.tipo,
            "status": item.estado,
            "scheduled_at": item.programada_en.isoformat(),
            "attempts": item.intentos,
            "recommendation_id": str(item.recomendacion_id) if item.recomendacion_id else None,
        }
        for item in notifications
    ]
    return JsonResponse(build_envelope(
        success=True,
        message="Bandeja de notificaciones consultada",
        data=data,
        request_id=request_id_from(request),
    ))


@csrf_exempt
def run_jobs(request):
    """Endpoint interno para evaluar plazos, mora y entregar notificaciones pendientes.

    Solo el rol DTI puede ejecutar este endpoint manualmente.
    En producción se llama desde un cron / tarea programada.
    """
    if request.method != "POST":
        return JsonResponse(
            build_envelope(
                success=False,
                message="Método no permitido.",
                errors={"code": "METHOD_NOT_ALLOWED"},
                request_id=request_id_from(request),
            ),
            status=405,
        )

    user, _ = _persistent_user(request, Role.DTI)
    if user.role is not Role.DTI:
        return JsonResponse(
            build_envelope(
                success=False,
                message="Solo el rol DTI puede ejecutar los jobs.",
                errors={"code": "PERMISSION_DENIED"},
                request_id=request_id_from(request),
            ),
            status=403,
        )

    from backend.modules.notificaciones.application.send_deadline_alerts import send_deadline_alerts
    from backend.modules.notificaciones.application.mark_overdue import mark_overdue_recommendations

    alerts_result = send_deadline_alerts()
    mora_result = mark_overdue_recommendations()

    return JsonResponse(build_envelope(
        success=True,
        message="Jobs ejecutados correctamente",
        data={
            "alertas_vencimiento": alerts_result,
            "mora": mora_result,
        },
        request_id=request_id_from(request),
    ))
