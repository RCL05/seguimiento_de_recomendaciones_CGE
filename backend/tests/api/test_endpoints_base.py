"""Endpoints base de la Semana 3 (APE 3): recursos REST, códigos HTTP y validaciones."""

import json
from datetime import timedelta

import pytest
from django.test import Client, override_settings
from django.utils import timezone

from backend.modules.recomendaciones.models import Recomendacion
from tests.auth_helpers import authenticated_headers

pytestmark = pytest.mark.django_db

PDF = b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"


def _json(client, method, path, payload, headers):
    return getattr(client, method)(path, data=json.dumps(payload), content_type="application/json", **headers)


@pytest.fixture
def uai():
    return authenticated_headers("UAI", "uai-base", "UAI")


@pytest.fixture
def ejecutor():
    return authenticated_headers("EJECUTOR", "ejecutor-base", "DEP-A")


@pytest.fixture
def informe(uai):
    response = _json(
        Client(),
        "post",
        "/api/v1/informes",
        {
            "numero_informe": "INF-BASE-001",
            "periodo_auditado": "2025",
            "fecha_notificacion": "2026-01-10",
            "pdf_informe_url": "https://example.test/inf.pdf",
        },
        uai,
    )
    assert response.status_code == 201, response.content
    return response


@pytest.fixture
def recomendacion_en_validacion(tmp_path, uai, ejecutor, informe):
    """Recomendación con un hito y una evidencia cargada (estado EN_VALIDACION)."""
    client = Client()
    with override_settings(MEDIA_ROOT=tmp_path):
        rec = _json(
            client,
            "post",
            "/api/v1/recomendaciones",
            {
                "report_id": informe.json()["data"]["id"],
                "number": "R-BASE-1",
                "description": "Actualizar el reglamento interno.",
                "unit_id": "DEP-A",
                "legal_days": 60,
                "due_date": "2027-06-30",
                "priority": "ALTA",
            },
            uai,
        ).json()["data"]
        hito = _json(
            client,
            "post",
            f"/api/v1/recomendaciones/{rec['id']}/hitos",
            {"descripcion_hito": "Redactar propuesta", "fecha_compromiso": "2027-03-01"},
            ejecutor,
        )
        assert hito.status_code == 201, hito.content
        evidencia = client.post(
            f"/api/v1/recomendaciones/{rec['id']}/evidencias",
            data=PDF,
            content_type="application/pdf",
            HTTP_X_FILENAME="propuesta.pdf",
            HTTP_X_EVIDENCE_TYPE="FINAL",
            **ejecutor,
        )
        assert evidencia.status_code == 201, evidencia.content
        yield rec["id"], evidencia.json()["data"], tmp_path


def test_informe_201_con_location_y_consulta_por_id(informe, uai):
    location = informe["Location"]
    assert location == f"/api/v1/informes/{informe.json()['data']['id']}"
    detalle = Client().get(location, **uai)
    assert detalle.status_code == 200
    assert detalle.json()["data"]["numero_informe"] == "INF-BASE-001"


def test_listado_de_informes_paginado(informe, uai):
    response = Client().get("/api/v1/informes?page_size=10", **uai)
    assert response.status_code == 200
    assert response.json()["meta"]["pagination"]["total"] == 1


def test_informe_duplicado_responde_409(informe, uai):
    duplicado = _json(
        Client(),
        "post",
        "/api/v1/informes",
        {
            "numero_informe": "INF-BASE-001",
            "periodo_auditado": "2025",
            "fecha_notificacion": "2026-01-10",
            "pdf_informe_url": "https://example.test/otro.pdf",
        },
        uai,
    )
    assert duplicado.status_code == 409
    assert duplicado.json()["errors"]["code"] == "CONFLICT"


def test_validacion_400_detalla_campos(uai, informe):
    response = _json(
        Client(),
        "post",
        "/api/v1/recomendaciones",
        {"report_id": informe.json()["data"]["id"], "legal_days": 0},
        uai,
    )
    assert response.status_code == 400
    errors = response.json()["errors"]
    assert errors["code"] == "VALIDATION_ERROR"
    assert {"number", "description", "unit_id", "due_date", "legal_days"} <= set(errors["fields"])


def test_401_incluye_www_authenticate():
    response = Client().get("/api/v1/recomendaciones")
    assert response.status_code == 401
    assert response["WWW-Authenticate"].startswith("Bearer")


def test_rechazo_sin_observaciones_responde_400(recomendacion_en_validacion, uai):
    rec_id, evidencia, _ = recomendacion_en_validacion
    response = _json(
        Client(),
        "post",
        f"/api/v1/recomendaciones/{rec_id}/dictamenes",
        {"evidence_id": evidencia["id"], "approved": False},
        uai,
    )
    assert response.status_code == 400
    assert "observaciones" in response.json()["errors"]["fields"]


def test_dictamen_aprobado_201_y_doble_dictamen_409(recomendacion_en_validacion, uai):
    rec_id, evidencia, _ = recomendacion_en_validacion
    payload = {"evidence_id": evidencia["id"], "approved": True, "observaciones": "Conforme."}
    first = _json(Client(), "post", f"/api/v1/recomendaciones/{rec_id}/dictamenes", payload, uai)
    assert first.status_code == 201, first.content
    assert first.json()["data"]["recomendacion"]["state"] == "CUMPLIDA"

    second = _json(Client(), "post", f"/api/v1/recomendaciones/{rec_id}/dictamenes", payload, uai)
    assert second.status_code == 409


def test_plan_de_accion_lista_hitos(recomendacion_en_validacion, ejecutor):
    rec_id, _, _ = recomendacion_en_validacion
    response = Client().get(f"/api/v1/recomendaciones/{rec_id}/hitos", **ejecutor)
    assert response.status_code == 200
    assert [h["descripcion_hito"] for h in response.json()["data"]] == ["Redactar propuesta"]


def test_anulacion_logica_por_patch_conserva_la_evidencia(recomendacion_en_validacion, uai):
    _, evidencia, _ = recomendacion_en_validacion
    path = f"/api/v1/evidencias/{evidencia['id']}"
    response = _json(Client(), "patch", path, {"estado": "ANULADA", "motivo": "Archivo equivocado."}, uai)
    assert response.status_code == 200, response.content
    assert response.json()["data"]["status"] == "ANULADA"

    again = _json(Client(), "patch", path, {"estado": "ANULADA", "motivo": "Otra vez."}, uai)
    assert again.status_code == 409


def test_integridad_detecta_archivo_alterado(recomendacion_en_validacion, uai):
    _, evidencia, media_root = recomendacion_en_validacion
    path = f"/api/v1/evidencias/{evidencia['id']}/integridad"
    with override_settings(MEDIA_ROOT=media_root):
        intacta = Client().get(path, **uai)
        assert intacta.status_code == 200
        assert intacta.json()["data"]["integra"] is True

        (media_root / "evidencias" / f"{evidencia['id']}.pdf").write_bytes(PDF + b"% alterado\n")
        alterada = Client().get(path, **uai)
        assert alterada.json()["data"]["integra"] is False


def test_integridad_no_disponible_para_ejecutor(recomendacion_en_validacion, ejecutor):
    _, evidencia, _ = recomendacion_en_validacion
    response = Client().get(f"/api/v1/evidencias/{evidencia['id']}/integridad", **ejecutor)
    assert response.status_code == 403


def test_tablero_lista_unidades_en_mora(recomendacion_en_validacion):
    rec_id, _, _ = recomendacion_en_validacion
    # Plazo vencido y la evidencia en revisión se entregó después del vencimiento.
    Recomendacion.objects.filter(pk=rec_id).update(
        estado=Recomendacion.Estado.EN_PROCESO,
        fecha_vencimiento_legal=timezone.localdate() - timedelta(days=5),
    )
    rectorado = authenticated_headers("RECTORADO", "rectorado-base", "RECTORADO")
    data = Client().get("/api/v1/reportes/tablero", **rectorado).json()["data"]
    assert data["en_mora"] == 1
    assert data["unidades_en_mora"][0]["unidad_codigo"] == "DEP-A"
    assert "VENCIDA" not in data["por_estado"]


def test_matriz_es_get_y_csv(recomendacion_en_validacion, uai):
    response = Client().get("/api/v1/reportes/matriz-cge", **uai)
    assert response.status_code == 200
    header = response.content.decode("utf-8-sig").splitlines()[0]
    assert header.startswith("numero_informe,numero_recomendacion,descripcion")


def test_dti_asigna_rol_y_unidad(uai):
    dti = authenticated_headers("DTI", "dti-base", "DTI")
    client = Client()
    usuarios = client.get("/api/v1/usuarios", **dti).json()["data"]
    target = next(u for u in usuarios if u["correo_institucional"] == "uai-base@unl.edu.ec")

    response = _json(client, "patch", f"/api/v1/usuarios/{target['id']}", {"rol": "CGE_AUDITOR"}, dti)
    assert response.status_code == 200, response.content
    assert response.json()["data"]["rol"] == "CGE_AUDITOR"

    forbidden = _json(client, "patch", f"/api/v1/usuarios/{target['id']}", {"rol": "DTI"}, uai)
    assert forbidden.status_code in {401, 403}


def test_swagger_ui_y_esquema_publicos():
    client = Client()
    assert client.get("/api/docs/").status_code == 200
    schema = client.get("/api/schema/")
    assert schema.status_code == 200
    assert b"SITRA-CGE UNL API" in schema.content
