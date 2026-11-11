from smtplib import SMTPException

from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.utils import timezone

from backend.modules.notificaciones.models import Notificacion
from backend.modules.recomendaciones.models import Recomendacion
from backend.modules.usuarios.models import Usuario

MAX_DELIVERY_ATTEMPTS = 3


def schedule_notification(
    *,
    recommendation: Recomendacion | None,
    recipient: Usuario,
    notification_type: str,
    idempotency_key: str,
    canal_interno: bool | None = None,
    canal_email: bool | None = None,
) -> Notificacion | None:
    """Programa una notificación idempotente respetando los canales configurados."""
    if canal_interno is None or canal_email is None:
        from backend.modules.notificaciones.application.manage_notification_settings import (
            resolve_channels,
        )

        resolved_internal, resolved_email = resolve_channels(
            recipient=recipient,
            notification_type=notification_type,
        )
        canal_interno = resolved_internal if canal_interno is None else canal_interno
        canal_email = resolved_email if canal_email is None else canal_email

    if not canal_interno and not canal_email:
        return None

    # Una notificación solo interna queda visible de inmediato en la bandeja.
    internal_only = canal_interno and not canal_email
    try:
        with transaction.atomic():
            return Notificacion.objects.create(
                recomendacion=recommendation,
                destinatario=recipient,
                tipo=notification_type,
                clave_idempotencia=idempotency_key,
                programada_en=timezone.now(),
                canal_interno=canal_interno,
                canal_email=canal_email,
                estado=(
                    Notificacion.Estado.ENVIADA
                    if internal_only
                    else Notificacion.Estado.PENDIENTE
                ),
                enviada_en=timezone.now() if internal_only else None,
            )
    except IntegrityError:
        return Notificacion.objects.get(clave_idempotencia=idempotency_key)


def deliver_pending_notifications(*, limit: int = 50) -> int:
    """Entrega correos pendientes con reintentos acotados.

    Solo se reintentan las notificaciones PENDIENTES o FALLIDAS que aún no
    alcanzaron ``MAX_DELIVERY_ATTEMPTS``. La clave de idempotencia evita crear
    duplicados; un fallo SMTP no revierte la transacción de negocio.
    """
    delivered = 0
    for notification in Notificacion.objects.filter(
        estado__in=[Notificacion.Estado.PENDIENTE, Notificacion.Estado.FALLIDA],
        canal_email=True,
        intentos__lt=MAX_DELIVERY_ATTEMPTS,
    ).order_by("programada_en")[:limit]:
        notification.intentos += 1
        try:
            sent = send_mail(
                subject=f"SITRA-CGE: {notification.tipo}",
                message="Tiene una actualización pendiente en SITRA-CGE UNL.",
                from_email=None,
                recipient_list=[notification.destinatario.correo_institucional],
                fail_silently=False,
            )
        except (SMTPException, OSError):
            sent = False

        if sent:
            notification.estado = Notificacion.Estado.ENVIADA
            notification.enviada_en = timezone.now()
            delivered += 1
        else:
            notification.estado = Notificacion.Estado.FALLIDA
        notification.save(update_fields=["intentos", "estado", "enviada_en"])
    return delivered
