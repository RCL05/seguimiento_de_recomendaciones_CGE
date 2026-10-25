from smtplib import SMTPException

from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.utils import timezone

from backend.modules.notificaciones.models import Notificacion
from backend.modules.recomendaciones.models import Recomendacion
from backend.modules.usuarios.models import Usuario


def schedule_notification(
    *,
    recommendation: Recomendacion | None,
    recipient: Usuario,
    notification_type: str,
    idempotency_key: str,
) -> Notificacion:
    try:
        with transaction.atomic():
            return Notificacion.objects.create(
                recomendacion=recommendation,
                destinatario=recipient,
                tipo=notification_type,
                clave_idempotencia=idempotency_key,
                programada_en=timezone.now(),
            )
    except IntegrityError:
        return Notificacion.objects.get(clave_idempotencia=idempotency_key)


def deliver_pending_notifications(*, limit: int = 50) -> int:
    delivered = 0
    for notification in Notificacion.objects.filter(
        estado=Notificacion.Estado.PENDIENTE
    ).order_by("programada_en")[:limit]:
        try:
            sent = send_mail(
                subject=f"SITRA-CGE: {notification.tipo}",
                message="Tiene una actualización pendiente en SITRA-CGE UNL.",
                from_email=None,
                recipient_list=[notification.destinatario.correo_institucional],
                fail_silently=False,
            )
            notification.intentos += 1
            if sent:
                notification.estado = Notificacion.Estado.ENVIADA
                notification.enviada_en = timezone.now()
                delivered += 1
            notification.save(update_fields=["intentos", "estado", "enviada_en"])
        except (SMTPException, OSError):
            notification.intentos += 1
            notification.estado = Notificacion.Estado.FALLIDA
            notification.save(update_fields=["intentos", "estado"])
    return delivered
