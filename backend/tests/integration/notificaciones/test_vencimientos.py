"""Vencimiento como indicador (opción 2): job de plazos, reanudación y dictamen tardío."""

import json
from datetime import timedelta

import pytest
from django.test import Client, override_settings
from django.utils import timezone

from backend.core.audit.models import AuditLog
from backend.modules.notificaciones.application.mark_overdue import mark_overdue_recommendations
from backend.modules.notificaciones.models import Notificacion
from backend.modules.recomendaciones.infrastructure.repositories import RecommendationRepository
from backend.modules.recomendaciones.models import Evidencia, Recomendacion
from backend.modules.usuarios.models import UnidadOrganica
from tests.auth_helpers import authenticated_headers

pytestmark = pytest.mark.django_db

PDF = b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"
HOY = timezone.localdate


@pytest.fixture
def uai():
    return authenticated_headers("UAI", "uai-venc", "UAI")


@pytest.fixture
def ejecutor():
    UnidadOrganica.objects.get_or_create(codigo="DEP-A", defaults={"nombre": "Departamento A"})
    return authenticated_headers("EJECUTOR", "ejecutor-venc", "DEP-A")


def _post(path, payload, headers):
    return Client().post(path, data=json.dumps(payload), content_type="application/json", **headers)


def _recomendacion(uai, ejecutor, numero="R-V1"):
    """Recomendación con un hito (EN_PROCESO) y plazo aún vigente."""
    informe = _post(
        "/api/v1/informes",
        {
            "numero_informe": f"INF-{numero}",
            "periodo_auditado": "2025",
            "fecha_notificacion": HOY().isoformat(),
            "pdf_informe_url": "https://example.test/inf.pdf",
        },
        uai,
    ).json()["data"]
    rec = _post(
        "/api/v1/recomendaciones",
        {
            "report_id": informe["id"],
            "number": numero,
            "description": "Implementar control.",
            "unit_id": "DEP-A",
            "legal_days": 30,
            "due_date": (HOY() + timedelta(days=30)).isoformat(),
        },
        uai,
    ).json()["data"]
    hito = _post(
        f"/api/v1/recomendaciones/{rec['id']}/hitos",
        {"descripcion_hito": "Primer hito", "fecha_compromiso": (HOY() + timedelta(days=10)).isoformat()},
        ejecutor,
    )
    assert hito.status_code == 201, hito.content
    return rec["id"]


def _vencer(rec_id, dias=3):
    Recomendacion.objects.filter(pk=rec_id).update(fecha_vencimiento_legal=HOY() - timedelta(days=dias))


def _subir(rec_id, ejecutor):
    return Client().post(
        f"/api/v1/recomendaciones/{rec_id}/evidencias",
        data=PDF,
        content_type="application/pdf",
        HTTP_X_FILENAME="evidencia.pdf",
        HTTP_X_EVIDENCE_TYPE="FINAL",
        **ejecutor,
    )


def test_job_registra_y_notifica_sin_cambiar_estado_y_es_idempotente(uai, ejecutor):
    rec_id = _recomendacion(uai, ejecutor)
    _vencer(rec_id)

    primera = mark_overdue_recommendations()
    rec = Recomendacion.objects.get(pk=rec_id)
    assert primera["marked"] == 1
    assert rec.estado == Recomendacion.Estado.EN_PROCESO
    assert rec.vencimiento_registrado_en is not None
    assert RecommendationRepository.esta_vencida(rec_id) is True
    audit = AuditLog.objects.get(entidad_id=rec_id, accion="MARK_OVERDUE")
    assert audit.estado_anterior == audit.estado_nuevo == "EN_PROCESO"
    notificaciones = Notificacion.objects.filter(recomendacion_id=rec_id, tipo="EN_MORA").count()
    assert notificaciones >= 1

    segunda = mark_overdue_recommendations()
    assert segunda["marked"] == 0
    assert AuditLog.objects.filter(entidad_id=rec_id, accion="MARK_OVERDUE").count() == 1
    assert Notificacion.objects.filter(recomendacion_id=rec_id, tipo="EN_MORA").count() == notificaciones


def test_vencida_sigue_en_proceso_y_acepta_hitos_futuros(uai, ejecutor):
    rec_id = _recomendacion(uai, ejecutor)
    _vencer(rec_id)
    mark_overdue_recommendations()

    pasado = _post(
        f"/api/v1/recomendaciones/{rec_id}/hitos",
        {"descripcion_hito": "Fecha pasada", "fecha_compromiso": (HOY() - timedelta(days=1)).isoformat()},
        ejecutor,
    )
    assert pasado.status_code == 400

    futuro = _post(
        f"/api/v1/recomendaciones/{rec_id}/hitos",
        {"descripcion_hito": "Corrección tardía", "fecha_compromiso": (HOY() + timedelta(days=15)).isoformat()},
        ejecutor,
    )
    assert futuro.status_code == 201, futuro.content

    detalle = Client().get(f"/api/v1/recomendaciones/{rec_id}", **ejecutor).json()["data"]
    assert detalle["state"] == "EN_PROCESO"
    assert detalle["vencida"] is True
    assert detalle["overdue_registered_at"] is not None


def test_entrega_a_tiempo_no_queda_vencida_y_la_uai_puede_dictaminar(tmp_path, uai, ejecutor):
    rec_id = _recomendacion(uai, ejecutor, "R-V2")
    with override_settings(MEDIA_ROOT=tmp_path):
        evidencia = _subir(rec_id, ejecutor).json()["data"]
        # La UAI no revisa a tiempo: el plazo vence con la evidencia en revisión.
        _vencer(rec_id)
        Evidencia.objects.filter(pk=evidencia["id"]).update(fecha_carga=timezone.now() - timedelta(days=5))

        assert mark_overdue_recommendations()["marked"] == 0
        assert RecommendationRepository.esta_vencida(rec_id) is False

        dictamen = _post(
            f"/api/v1/recomendaciones/{rec_id}/dictamenes",
            {"evidence_id": evidencia["id"], "approved": True, "observaciones": "Conforme."},
            uai,
        )
    assert dictamen.status_code == 201, dictamen.content
    assert dictamen.json()["data"]["recomendacion"]["state"] == "CUMPLIDA"
    assert dictamen.json()["data"]["recomendacion"]["vencida"] is False


def test_entrega_tardia_sigue_vencida_pero_se_puede_cumplir(tmp_path, uai, ejecutor):
    rec_id = _recomendacion(uai, ejecutor, "R-V3")
    _vencer(rec_id)
    with override_settings(MEDIA_ROOT=tmp_path):
        evidencia = _subir(rec_id, ejecutor)
        assert evidencia.status_code == 201, evidencia.content
        assert RecommendationRepository.esta_vencida(rec_id) is True

        dictamen = _post(
            f"/api/v1/recomendaciones/{rec_id}/dictamenes",
            {"evidence_id": evidencia.json()["data"]["id"], "approved": True, "observaciones": "Cumplida tarde."},
            uai,
        )
    assert dictamen.status_code == 201
    assert RecommendationRepository.esta_vencida(rec_id) is False


def test_filtro_vencida_y_columna_en_matriz(uai, ejecutor):
    vencida = _recomendacion(uai, ejecutor, "R-V4")
    en_plazo = _recomendacion(uai, ejecutor, "R-V5")
    _vencer(vencida)

    solo_vencidas = Client().get("/api/v1/recomendaciones?vencida=true", **uai).json()["data"]
    assert [r["id"] for r in solo_vencidas] == [vencida]
    en_plazo_ids = [r["id"] for r in Client().get("/api/v1/recomendaciones?vencida=false", **uai).json()["data"]]
    assert en_plazo in en_plazo_ids and vencida not in en_plazo_ids

    csv = Client().get("/api/v1/reportes/matriz-cge", **uai).content.decode("utf-8-sig").splitlines()
    header = csv[0].split(",")
    assert header[-2:] == ["vencida", "vencimiento_registrado_en"]
    filas = {line.split(",")[1]: line.split(",")[header.index("vencida")] for line in csv[1:]}
    assert filas == {"R-V4": "SI", "R-V5": "NO"}


def test_migracion_devuelve_cada_vencida_a_su_estado_real(uai, ejecutor):
    import importlib
    from uuid import uuid4

    from django.apps import apps

    from backend.core.audit.repository import record_audit

    migracion = importlib.import_module(
        "backend.modules.recomendaciones.migrations.0007_vencimiento_como_indicador"
    )
    con_historial = _recomendacion(uai, ejecutor, "R-M1")
    sin_historial = _recomendacion(uai, ejecutor, "R-M2")
    Recomendacion.objects.filter(pk__in=[con_historial, sin_historial]).update(estado="VENCIDA")
    record_audit(
        request_id=uuid4(),
        user=None,
        action="MARK_OVERDUE",
        entity="recommendation",
        entity_id=con_historial,
        previous_state="EN_VALIDACION",
        new_state="VENCIDA",
    )

    migracion.restaurar_estado_real(apps, None)

    restaurada = Recomendacion.objects.get(pk=con_historial)
    assert restaurada.estado == Recomendacion.Estado.EN_VALIDACION
    assert restaurada.vencimiento_registrado_en is not None
    # Sin evento en la bitácora: tiene hitos, así que vuelve a EN_PROCESO.
    assert Recomendacion.objects.get(pk=sin_historial).estado == Recomendacion.Estado.EN_PROCESO


def test_reapertura_reinicia_el_ciclo_de_vencimiento(uai, ejecutor):
    rec_id = _recomendacion(uai, ejecutor, "R-V6")
    _vencer(rec_id)
    mark_overdue_recommendations()
    Recomendacion.objects.filter(pk=rec_id).update(estado=Recomendacion.Estado.CUMPLIDA)

    reabierta = Client().patch(
        f"/api/v1/recomendaciones/{rec_id}",
        data=json.dumps({"estado": "REABIERTA", "motivo": "Hallazgo posterior."}),
        content_type="application/json",
        **uai,
    )
    assert reabierta.status_code == 200
    assert Recomendacion.objects.get(pk=rec_id).vencimiento_registrado_en is None
    assert mark_overdue_recommendations()["marked"] == 1
