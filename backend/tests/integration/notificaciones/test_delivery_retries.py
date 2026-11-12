"""Reintentos SMTP acotados e idempotentes para notificaciones por correo."""

from smtplib import SMTPException

import pytest
from django.utils import timezone

from backend.modules.notificaciones.application import service
from backend.modules.notificaciones.models import Notificacion
from backend.modules.usuarios.models import Usuario

pytestmark = pytest.mark.django_db


@pytest.fixture
def recipient():
    return Usuario.objects.create(
        correo_institucional="reintentos@unl.edu.ec",
        nombres="Destino Reintentos",
        rol=Usuario.Rol.UAI,
    )


def _notificacion(recipient, clave="RETRY:1"):
    return Notificacion.objects.create(
        destinatario=recipient,
        tipo="EN_MORA",
        clave_idempotencia=clave,
        programada_en=timezone.now(),
        canal_email=True,
    )


def test_reintenta_hasta_entregar_y_marca_enviada(monkeypatch, recipient):
    attempts = {"count": 0}

    def fake_send_mail(**kwargs):
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise SMTPException("fallo temporal")
        return 1

    monkeypatch.setattr(service, "send_mail", fake_send_mail)
    notification = _notificacion(recipient)

    assert service.deliver_pending_notifications() == 0
    notification.refresh_from_db()
    assert (notification.intentos, notification.estado) == (1, Notificacion.Estado.FALLIDA)

    assert service.deliver_pending_notifications() == 0
    notification.refresh_from_db()
    assert (notification.intentos, notification.estado) == (2, Notificacion.Estado.FALLIDA)

    assert service.deliver_pending_notifications() == 1
    notification.refresh_from_db()
    assert (notification.intentos, notification.estado) == (3, Notificacion.Estado.ENVIADA)
    assert notification.enviada_en is not None


def test_deja_de_reintentar_tras_tres_fallos(monkeypatch, recipient):
    calls = {"count": 0}

    def always_fail(**kwargs):
        calls["count"] += 1
        raise OSError("sin conexión SMTP")

    monkeypatch.setattr(service, "send_mail", always_fail)
    notification = _notificacion(recipient, clave="RETRY:2")

    for _ in range(service.MAX_DELIVERY_ATTEMPTS):
        assert service.deliver_pending_notifications() == 0

    notification.refresh_from_db()
    assert notification.intentos == service.MAX_DELIVERY_ATTEMPTS
    assert notification.estado == Notificacion.Estado.FALLIDA

    assert service.deliver_pending_notifications() == 0
    assert calls["count"] == service.MAX_DELIVERY_ATTEMPTS


def test_no_reenvia_una_notificacion_ya_enviada(monkeypatch, recipient):
    calls = {"count": 0}

    def fake_send_mail(**kwargs):
        calls["count"] += 1
        return 1

    monkeypatch.setattr(service, "send_mail", fake_send_mail)
    _notificacion(recipient, clave="RETRY:3")

    assert service.deliver_pending_notifications() == 1
    assert service.deliver_pending_notifications() == 0
    assert calls["count"] == 1
