"""Alertas de vencimiento próximo (RF-011) y regla de vencimiento (opción 2)."""

from datetime import date

import pytest

from backend.modules.notificaciones.application.send_deadline_alerts import send_deadline_alerts
from backend.modules.notificaciones.infrastructure.preferences_models import ConfiguracionNotificacion
from backend.modules.notificaciones.models import Notificacion
from backend.modules.recomendaciones.domain.vencimiento import esta_vencida
from backend.modules.recomendaciones.models import Recomendacion
from backend.modules.usuarios.models import Usuario
from tests import factories


@pytest.fixture
def destinatarios(db):
    return {
        "ejecutor": factories.usuario(Usuario.Rol.EJECUTOR, "ejecutor-alerta", "DEP-A"),
        "uai": factories.usuario(Usuario.Rol.UAI, "uai-alerta", "UAI"),
    }


def _alertas(rec):
    return Notificacion.objects.filter(recomendacion=rec, tipo="ALERTA_VENCIMIENTO")


def _esperados(rec):
    """Ejecutores activos de la unidad responsable y roles configurados (UAI por defecto)."""
    ejecutores = Usuario.objects.filter(
        unidad_org=rec.unidad_responsable, rol=Usuario.Rol.EJECUTOR, activo=True
    )
    uai = Usuario.objects.filter(rol=Usuario.Rol.UAI, activo=True)
    return set(ejecutores.values_list("id", flat=True)) | set(uai.values_list("id", flat=True))


@pytest.mark.parametrize("dias", [15, 10, 1, 0])
def test_alerta_cuando_faltan_15_dias_o_menos(destinatarios, dias):
    rec = factories.recomendacion(dias_para_vencer=dias)
    ajeno = factories.usuario(Usuario.Rol.EJECUTOR, "ejecutor-ajeno", "DEP-B")

    resultado = send_deadline_alerts()

    destinos = set(_alertas(rec).values_list("destinatario_id", flat=True))
    assert destinos == _esperados(rec)
    assert {destinatarios["ejecutor"].id, destinatarios["uai"].id} <= destinos
    assert ajeno.id not in destinos  # un ejecutor de otra unidad no recibe la alerta
    assert resultado["scheduled"] == len(destinos)


def test_sin_alerta_con_16_dias_o_con_el_plazo_ya_vencido(destinatarios):
    lejana = factories.recomendacion(dias_para_vencer=16)
    vencida = factories.recomendacion(dias_para_vencer=-1)

    assert send_deadline_alerts()["scheduled"] == 0
    assert not _alertas(lejana).exists()
    assert not _alertas(vencida).exists()


def test_sin_alerta_si_ya_tiene_evidencia_validada_o_esta_en_validacion(destinatarios):
    con_validada = factories.recomendacion(dias_para_vencer=5)
    factories.evidencia(con_validada, validada=True)
    en_validacion = factories.recomendacion(dias_para_vencer=5, estado=Recomendacion.Estado.EN_VALIDACION)
    cumplida = factories.recomendacion(dias_para_vencer=5, estado=Recomendacion.Estado.CUMPLIDA)

    assert send_deadline_alerts()["scheduled"] == 0
    for rec in (con_validada, en_validacion, cumplida):
        assert not _alertas(rec).exists()


def test_evidencia_presentada_sin_validar_no_detiene_la_alerta(destinatarios):
    rec = factories.recomendacion(dias_para_vencer=5)
    factories.evidencia(rec, validada=False)

    assert send_deadline_alerts()["scheduled"] == len(_esperados(rec))


def test_segunda_ejecucion_es_idempotente(destinatarios):
    rec = factories.recomendacion(dias_para_vencer=7)

    esperados = len(_esperados(rec))

    primera = send_deadline_alerts()
    segunda = send_deadline_alerts()

    assert primera["scheduled"] == esperados
    assert segunda == {"scheduled": 0, "skipped": esperados, "delivered": 0}
    assert _alertas(rec).count() == esperados


def test_notificaciones_desactivadas_no_programan_nada(destinatarios):
    factories.recomendacion(dias_para_vencer=3)
    config = ConfiguracionNotificacion.load()
    config.notificaciones_activas = False
    config.save()

    assert send_deadline_alerts() == {"scheduled": 0, "skipped": 0, "delivered": 0}
    assert Notificacion.objects.count() == 0


def test_umbral_configurado_reemplaza_los_15_dias(destinatarios):
    config = ConfiguracionNotificacion.load()
    config.umbral_dias = 5
    config.save()
    dentro = factories.recomendacion(dias_para_vencer=5)
    fuera = factories.recomendacion(dias_para_vencer=6)

    send_deadline_alerts()

    assert _alertas(dentro).exists()
    assert not _alertas(fuera).exists()


HOY = date(2026, 10, 25)
AYER = date(2026, 10, 24)


@pytest.mark.parametrize(
    ("estado", "vence", "entrega_oportuna", "esperado"),
    [
        ("EN_PROCESO", HOY, False, False),  # vence hoy: aún dentro del plazo
        ("EN_PROCESO", AYER, False, True),
        ("PENDIENTE", AYER, False, True),
        ("REABIERTA", AYER, False, True),
        ("EN_VALIDACION", AYER, True, False),  # entregó a tiempo; la demora es de la UAI
        ("EN_VALIDACION", AYER, False, True),  # entregó tarde
        ("CUMPLIDA", AYER, False, False),
    ],
)
def test_regla_de_vencimiento(estado, vence, entrega_oportuna, esperado):
    resultado = esta_vencida(
        estado=estado,
        fecha_vencimiento=vence,
        hoy=HOY,
        entrega_oportuna_en_revision=entrega_oportuna,
    )
    assert resultado is esperado
