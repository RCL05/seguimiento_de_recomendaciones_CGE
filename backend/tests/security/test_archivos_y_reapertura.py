"""Archivos sin acceso público y reapertura controlada de recomendaciones."""

import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings

from backend.core.audit.models import AuditLog
from backend.modules.recomendaciones.models import Recomendacion
from backend.modules.usuarios.models import UnidadOrganica
from tests.auth_helpers import authenticated_headers

pytestmark = pytest.mark.django_db

PDF = b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"


@pytest.fixture
def uai():
    return authenticated_headers("UAI", "uai-archivos", "UAI")


@pytest.fixture
def informe_con_pdf(tmp_path, uai):
    with override_settings(MEDIA_ROOT=tmp_path, DEBUG=True):
        response = Client().post(
            "/api/v1/informes",
            data={
                "numero_informe": "INF-PDF-001",
                "periodo_auditado": "2025",
                "fecha_notificacion": "2026-02-01",
                "pdf_informe": SimpleUploadedFile("informe.pdf", PDF, content_type="application/pdf"),
            },
            **uai,
        )
        assert response.status_code == 201, response.content
        yield response.json()["data"], tmp_path


def test_media_no_se_publica_ni_con_debug(informe_con_pdf):
    _, media_root = informe_con_pdf
    stored = next(media_root.rglob("*.pdf"))
    relative = stored.relative_to(media_root).as_posix()
    with override_settings(MEDIA_ROOT=media_root, DEBUG=True):
        response = Client().get(f"/media/{relative}")
    assert response.status_code == 404


def test_documento_del_informe_requiere_token_y_rol(informe_con_pdf, uai):
    informe, media_root = informe_con_pdf
    assert informe["pdf_informe_url"] == f"/api/v1/informes/{informe['id']}/documento"
    with override_settings(MEDIA_ROOT=media_root):
        assert Client().get(informe["pdf_informe_url"]).status_code == 401

        ejecutor = authenticated_headers("EJECUTOR", "ejecutor-archivos", "DEP-A")
        assert Client().get(informe["pdf_informe_url"], **ejecutor).status_code == 403

        response = Client().get(informe["pdf_informe_url"], **uai)
        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"
        assert b"".join(response.streaming_content) == PDF


def test_informe_con_url_externa_no_tiene_documento_adjunto(uai):
    created = Client().post(
        "/api/v1/informes",
        data=json.dumps(
            {
                "numero_informe": "INF-URL-001",
                "periodo_auditado": "2025",
                "fecha_notificacion": "2026-02-01",
                "pdf_informe_url": "https://example.test/inf.pdf",
            }
        ),
        content_type="application/json",
        **uai,
    ).json()["data"]
    assert created["pdf_informe_url"] == "https://example.test/inf.pdf"
    response = Client().get(f"/api/v1/informes/{created['id']}/documento", **uai)
    assert response.status_code == 404


def _crear_recomendacion(uai, estado):
    UnidadOrganica.objects.get_or_create(codigo="DEP-A", defaults={"nombre": "Departamento A"})
    client = Client()
    informe = client.post(
        "/api/v1/informes",
        data=json.dumps(
            {
                "numero_informe": f"INF-REAB-{estado}",
                "periodo_auditado": "2025",
                "fecha_notificacion": "2026-02-01",
                "pdf_informe_url": "https://example.test/inf.pdf",
            }
        ),
        content_type="application/json",
        **uai,
    ).json()["data"]
    rec = client.post(
        "/api/v1/recomendaciones",
        data=json.dumps(
            {
                "report_id": informe["id"],
                "number": "R-REAB",
                "description": "Control de inventarios.",
                "unit_id": "DEP-A",
                "legal_days": 30,
                "due_date": "2027-12-31",
            }
        ),
        content_type="application/json",
        **uai,
    ).json()["data"]
    Recomendacion.objects.filter(pk=rec["id"]).update(estado=estado)
    return rec["id"]


def _reabrir(rec_id, headers, motivo="Hallazgo de seguimiento posterior."):
    return Client().patch(
        f"/api/v1/recomendaciones/{rec_id}",
        data=json.dumps({"estado": "REABIERTA", "motivo": motivo}),
        content_type="application/json",
        **headers,
    )


def test_uai_reabre_cumplida_y_ejecutor_la_reanuda(uai):
    rec_id = _crear_recomendacion(uai, Recomendacion.Estado.CUMPLIDA)

    response = _reabrir(rec_id, uai)
    assert response.status_code == 200, response.content
    assert response.json()["data"]["state"] == "REABIERTA"
    assert AuditLog.objects.filter(entidad_id=rec_id, accion="REOPEN", estado_nuevo="REABIERTA").exists()

    ejecutor = authenticated_headers("EJECUTOR", "ejecutor-reab", "DEP-A")
    hito = Client().post(
        f"/api/v1/recomendaciones/{rec_id}/hitos",
        data=json.dumps({"descripcion_hito": "Corregir hallazgo", "fecha_compromiso": "2027-06-30"}),
        content_type="application/json",
        **ejecutor,
    )
    assert hito.status_code == 201, hito.content
    assert Recomendacion.objects.get(pk=rec_id).estado == Recomendacion.Estado.EN_PROCESO


def test_solo_se_reabre_una_cumplida(uai):
    rec_id = _crear_recomendacion(uai, Recomendacion.Estado.EN_PROCESO)
    response = _reabrir(rec_id, uai)
    assert response.status_code == 409


def test_reapertura_exige_motivo_y_rol_uai(uai):
    rec_id = _crear_recomendacion(uai, Recomendacion.Estado.CUMPLIDA)
    assert _reabrir(rec_id, uai, motivo="").status_code == 400

    rectorado = authenticated_headers("RECTORADO", "rectorado-reab", "RECTORADO")
    assert _reabrir(rec_id, rectorado).status_code == 403
    assert Recomendacion.objects.get(pk=rec_id).estado == Recomendacion.Estado.CUMPLIDA
