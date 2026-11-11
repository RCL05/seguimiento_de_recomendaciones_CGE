"""Reasignación de recomendaciones entre unidades con historial (RF-003)."""

import json
from uuid import uuid4

import pytest
from django.test import Client

from backend.core.audit.models import AuditLog
from backend.modules.recomendaciones.models import Recomendacion
from backend.modules.usuarios.models import UnidadOrganica
from tests.auth_helpers import authenticated_headers

pytestmark = pytest.mark.django_db


@pytest.fixture
def uai():
    UnidadOrganica.objects.get_or_create(codigo="DEP-A", defaults={"nombre": "Departamento A"})
    UnidadOrganica.objects.get_or_create(codigo="DEP-B", defaults={"nombre": "Departamento B"})
    return authenticated_headers("UAI", "uai-reasig", "UAI")


def _post(path, payload, headers):
    return Client().post(
        path,
        data=json.dumps(payload),
        content_type="application/json",
        **headers,
    )


def _crear_recomendacion(uai, numero="R-REASIG"):
    informe = _post(
        "/api/v1/informes",
        {
            "numero_informe": f"INF-{numero}",
            "periodo_auditado": "2026",
            "fecha_notificacion": "2026-02-01",
            "pdf_informe_url": "https://example.test/inf.pdf",
        },
        uai,
    ).json()["data"]
    return _post(
        "/api/v1/recomendaciones",
        {
            "report_id": informe["id"],
            "number": numero,
            "description": "Implementar control interno.",
            "unit_id": "DEP-A",
            "legal_days": 30,
            "due_date": "2027-12-31",
        },
        uai,
    ).json()["data"]["id"]


def _patch(path, payload, headers):
    return Client().patch(
        path,
        data=json.dumps(payload),
        content_type="application/json",
        **headers,
    )


def _reasignar(rec_id, headers, unit_id="DEP-B", motivo="Cambio de estructura orgánica."):
    return _patch(
        f"/api/v1/recomendaciones/{rec_id}",
        {"unit_id": unit_id, "motivo": motivo},
        headers,
    )


def test_uai_reasigna_y_conserva_historial(uai):
    rec_id = _crear_recomendacion(uai)

    response = _reasignar(rec_id, uai)

    assert response.status_code == 200, response.content
    assert response.json()["data"]["unit_id"] == "DEP-B"
    rec = Recomendacion.objects.select_related("unidad_responsable").get(pk=rec_id)
    assert rec.unidad_responsable.codigo == "DEP-B"
    assert rec.estado == Recomendacion.Estado.PENDIENTE

    audit = AuditLog.objects.get(entidad_id=rec_id, accion="REASSIGN")
    assert audit.detalles_json["unidad_anterior"] == "DEP-A"
    assert audit.detalles_json["unidad_nueva"] == "DEP-B"
    assert audit.detalles_json["motivo"] == "Cambio de estructura orgánica."
    assert AuditLog.objects.filter(entidad_id=rec_id, accion="CREATE").exists()


def test_reasignacion_exige_rol_uai(uai):
    rec_id = _crear_recomendacion(uai)
    ejecutor = authenticated_headers("EJECUTOR", "ejecutor-reasig", "DEP-A")

    response = _reasignar(rec_id, ejecutor)

    assert response.status_code == 403
    rec = Recomendacion.objects.select_related("unidad_responsable").get(pk=rec_id)
    assert rec.unidad_responsable.codigo == "DEP-A"
    assert not AuditLog.objects.filter(entidad_id=rec_id, accion="REASSIGN").exists()


def test_reasignacion_valida_motivo_unidad_y_misma_unidad(uai):
    rec_id = _crear_recomendacion(uai)

    assert _reasignar(rec_id, uai, motivo="").status_code == 400
    assert _reasignar(rec_id, uai, unit_id="NO-EXISTE").status_code == 400
    assert _reasignar(rec_id, uai, unit_id="DEP-A").status_code == 400

    rec = Recomendacion.objects.select_related("unidad_responsable").get(pk=rec_id)
    assert rec.unidad_responsable.codigo == "DEP-A"
    assert not AuditLog.objects.filter(entidad_id=rec_id, accion="REASSIGN").exists()


def test_reasignacion_de_recomendacion_inexistente_responde_404(uai):
    response = _reasignar(uuid4(), uai)
    assert response.status_code == 404


def test_reasignacion_y_reapertura_no_se_combinan_en_un_mismo_patch(uai):
    rec_id = _crear_recomendacion(uai)

    ambos = _patch(
        f"/api/v1/recomendaciones/{rec_id}",
        {"estado": "REABIERTA", "unit_id": "DEP-B", "motivo": "Mezcla."},
        uai,
    )
    ninguno = _patch(f"/api/v1/recomendaciones/{rec_id}", {"motivo": "Sin cambio."}, uai)

    assert ambos.status_code == 400
    assert ninguno.status_code == 400
    assert not AuditLog.objects.filter(entidad_id=rec_id, accion="REASSIGN").exists()


def test_la_ruta_con_accion_reasignacion_ya_no_existe(uai):
    rec_id = _crear_recomendacion(uai)
    response = _post(
        f"/api/v1/recomendaciones/{rec_id}/reasignacion",
        {"unit_id": "DEP-B", "motivo": "Ruta anterior."},
        uai,
    )
    assert response.status_code == 404
