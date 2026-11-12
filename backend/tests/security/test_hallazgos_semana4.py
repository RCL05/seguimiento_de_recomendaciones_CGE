"""Regresiones de los hallazgos de seguridad de la Semana 4 (SEC-01 a SEC-04 y KPIs)."""

import json

import pytest
from django.core.cache import cache
from django.test import Client, override_settings

from backend.core.audit.models import AuditLog
from backend.modules.recomendaciones.models import Evidencia, Recomendacion
from tests.api.test_endpoints_base import PDF, _json, ejecutor, informe, recomendacion_en_validacion, uai  # noqa: F401
from tests.auth_helpers import authenticated_headers

pytestmark = pytest.mark.django_db


def _estado(rec_id):
    return Recomendacion.objects.get(pk=rec_id).estado


def _cargar(rec_id, ejecutor_headers, media_root, tipo="FINAL"):
    with override_settings(MEDIA_ROOT=media_root):
        response = Client().post(
            f"/api/v1/recomendaciones/{rec_id}/evidencias",
            data=PDF,
            content_type="application/pdf",
            HTTP_X_FILENAME="nueva.pdf",
            HTTP_X_EVIDENCE_TYPE=tipo,
            **ejecutor_headers,
        )
    assert response.status_code == 201, response.content
    return response.json()["data"]


def _dictamen(rec_id, evidence_id, headers, approved, observaciones=""):
    payload = {"evidence_id": evidence_id, "approved": approved}
    if observaciones:
        payload["observaciones"] = observaciones
    return _json(Client(), "post", f"/api/v1/recomendaciones/{rec_id}/dictamenes", payload, headers)


def _anular(evidence_id, headers):
    return _json(
        Client(), "patch", f"/api/v1/evidencias/{evidence_id}",
        {"estado": "ANULADA", "motivo": "Archivo equivocado."}, headers,
    )


# SEC-01 ----------------------------------------------------------------------

def test_anular_la_unica_evidencia_devuelve_la_recomendacion_a_en_proceso(recomendacion_en_validacion, uai, ejecutor):
    rec_id, evidencia, media_root = recomendacion_en_validacion
    assert _anular(evidencia["id"], uai).status_code == 200

    assert _estado(rec_id) == Recomendacion.Estado.EN_PROCESO
    assert AuditLog.objects.filter(accion="DEVOLVER_A_PROCESO", entidad_id=rec_id).exists()
    # El ejecutor puede volver a cargar evidencia.
    _cargar(rec_id, ejecutor, media_root)
    assert _estado(rec_id) == Recomendacion.Estado.EN_VALIDACION


def test_no_se_anula_la_evidencia_que_sustenta_una_recomendacion_cumplida(recomendacion_en_validacion, uai):
    rec_id, evidencia, _ = recomendacion_en_validacion
    assert _dictamen(rec_id, evidencia["id"], uai, approved=True).status_code == 201

    response = _anular(evidencia["id"], uai)
    assert response.status_code == 409
    assert _estado(rec_id) == Recomendacion.Estado.CUMPLIDA
    assert Evidencia.objects.get(pk=evidencia["id"]).estado == Evidencia.Estado.VIGENTE


# SEC-02 y SEC-03 ---------------------------------------------------------------

def test_evidencia_rechazada_no_puede_aprobarse_despues(recomendacion_en_validacion, uai, ejecutor):
    rec_id, rechazada, media_root = recomendacion_en_validacion
    assert _dictamen(rec_id, rechazada["id"], uai, approved=False, observaciones="Falta la firma.").status_code == 201
    _cargar(rec_id, ejecutor, media_root)

    response = _dictamen(rec_id, rechazada["id"], uai, approved=True)
    assert response.status_code == 409
    assert _estado(rec_id) == Recomendacion.Estado.EN_VALIDACION


def test_un_borrador_no_puede_aprobarse_como_cumplimiento(recomendacion_en_validacion, uai, ejecutor):
    rec_id, final, media_root = recomendacion_en_validacion
    assert _dictamen(rec_id, final["id"], uai, approved=False, observaciones="Incompleta.").status_code == 201
    borrador = _cargar(rec_id, ejecutor, media_root, tipo="BORRADOR")

    aprobado = _dictamen(rec_id, borrador["id"], uai, approved=True)
    assert aprobado.status_code == 409
    assert _estado(rec_id) == Recomendacion.Estado.EN_VALIDACION
    # El borrador sí puede devolverse con observaciones.
    assert _dictamen(rec_id, borrador["id"], uai, approved=False, observaciones="Es un avance.").status_code == 201


# SEC-04 ----------------------------------------------------------------------

def _login(client, credential):
    return client.post(
        "/api/v1/sesiones",
        data=json.dumps({"credential": credential}),
        content_type="application/json",
    )


def test_login_fallido_se_audita_y_responde_con_www_authenticate(monkeypatch):
    monkeypatch.setattr(
        "backend.modules.usuarios.infrastructure.sso_adapter.SsoAdapter.authenticate",
        lambda _adapter, *, token: {},
    )
    response = _login(Client(), "credencial-secreta-invalida")

    assert response.status_code == 401
    assert response["WWW-Authenticate"].startswith("Bearer")
    registro = AuditLog.objects.get(accion="LOGIN_SSO_FALLIDO")
    assert "credencial-secreta-invalida" not in json.dumps(registro.detalles_json)


def test_login_limita_intentos_por_ip(monkeypatch):
    monkeypatch.setattr(
        "backend.modules.usuarios.infrastructure.sso_adapter.SsoAdapter.authenticate",
        lambda _adapter, *, token: {},
    )
    cache.clear()
    client = Client()
    with override_settings(LOGIN_THROTTLE_RATE="3/min"):
        estados = [_login(client, f"intento-{n}").status_code for n in range(4)]
    cache.clear()

    assert estados == [401, 401, 401, 429]


# KPIs ------------------------------------------------------------------------

def test_kpis_del_ejecutor_solo_cuentan_su_unidad(recomendacion_en_validacion, uai, ejecutor, informe):
    authenticated_headers("EJECUTOR", "ejecutor-b", "DEP-B")  # crea la unidad DEP-B
    otra = _json(
        Client(), "post", "/api/v1/recomendaciones",
        {
            "report_id": informe.json()["data"]["id"], "number": "R-OTRA", "description": "Otra unidad.",
            "unit_id": "DEP-B", "legal_days": 30, "due_date": "2027-06-30", "priority": "MEDIA",
        },
        uai,
    )
    assert otra.status_code == 201, otra.content

    sin_recomendaciones = authenticated_headers("EJECUTOR", "ejecutor-sin-recs", "DEP-C")
    propio = Client().get("/api/v1/dashboard/kpis", **ejecutor)
    ajeno = Client().get("/api/v1/dashboard/kpis", **sin_recomendaciones)
    institucional = Client().get("/api/v1/dashboard/kpis", **uai)

    assert propio.json()["data"]["total_recomendaciones"] == 1
    assert ajeno.json()["data"]["total_recomendaciones"] == 0
    assert ajeno.json()["data"]["total_informes_cge"] == 0
    assert institucional.json()["data"]["total_recomendaciones"] == 2
