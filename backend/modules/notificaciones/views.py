from django.http import JsonResponse

from backend.core.api.request_context import request_id_from
from backend.core.api.response_envelope import build_envelope
from backend.core.api.views import _persistent_user
from backend.modules.notificaciones.models import Notificacion


def notification_inbox(request):
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
        }
        for item in notifications
    ]
    return JsonResponse(build_envelope(
        success=True,
        message="Bandeja de notificaciones consultada",
        data=data,
        request_id=request_id_from(request),
    ))
