"""Reglas de carga de evidencias (RF-008): PDF, tamaño, hash y unidad del ejecutor."""

import hashlib
from uuid import uuid4

import pytest
from django.test import override_settings

from backend.core.audit.models import AuditLog
from backend.core.shared.domain_types import NotFoundError, PayloadTooLarge, ValidationError
from backend.modules.recomendaciones.application import upload_evidencia
from backend.modules.recomendaciones.application.upload_evidencia import UploadEvidencia
from backend.modules.recomendaciones.models import Evidencia, Recomendacion
from backend.modules.usuarios.models import Usuario
from tests import factories

pytestmark = pytest.mark.django_db

PDF = b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"


@pytest.fixture(autouse=True)
def media(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        yield tmp_path


@pytest.fixture
def rec():
    return factories.recomendacion()


@pytest.fixture
def ejecutor():
    return factories.usuario(Usuario.Rol.EJECUTOR, "ejecutor-upload", "DEP-A")


def _subir(actor, rec, filename="evidencia.pdf", content=PDF):
    return UploadEvidencia().execute(
        actor=actor,
        request_id=uuid4(),
        recommendation_id=rec.id,
        filename=filename,
        content=content,
        evidence_type=Evidencia.Tipo.FINAL,
    )


def _archivos(media):
    carpeta = media / "evidencias"
    return list(carpeta.iterdir()) if carpeta.exists() else []


def test_carga_valida_guarda_hash_sha256_y_pasa_a_validacion(rec, ejecutor, media):
    evidencia = _subir(ejecutor, rec)

    assert evidencia.hash_sha256 == hashlib.sha256(PDF).hexdigest()
    assert evidencia.tamano_bytes == len(PDF)
    assert evidencia.mime_type == "application/pdf"
    assert len(_archivos(media)) == 1
    rec.refresh_from_db()
    assert rec.estado == Recomendacion.Estado.EN_VALIDACION


@pytest.mark.parametrize("filename", ["evidencia.docx", "evidencia.pdf.exe", "evidencia"])
def test_rechaza_extension_distinta_de_pdf(rec, ejecutor, media, filename):
    with pytest.raises(ValidationError):
        _subir(ejecutor, rec, filename=filename)
    assert Evidencia.objects.count() == 0
    assert _archivos(media) == []


@pytest.mark.parametrize("content", [b"", b"PK\x03\x04 zip disfrazado de pdf"])
def test_rechaza_contenido_vacio_o_que_no_es_pdf_y_borra_el_archivo(rec, ejecutor, media, content):
    with pytest.raises(ValidationError):
        _subir(ejecutor, rec, content=content)
    assert Evidencia.objects.count() == 0
    assert _archivos(media) == []


def test_rechaza_pdf_que_supera_el_tamano_maximo(rec, ejecutor, media, monkeypatch):
    monkeypatch.setattr(upload_evidencia, "MAX_SIZE_BYTES", len(PDF) - 1)

    with pytest.raises(PayloadTooLarge):
        _subir(ejecutor, rec)
    assert Evidencia.objects.count() == 0
    assert _archivos(media) == []


def test_pdf_en_trozos_respeta_el_limite_acumulado(rec, ejecutor, monkeypatch):
    monkeypatch.setattr(upload_evidencia, "MAX_SIZE_BYTES", 20)

    with pytest.raises(PayloadTooLarge):
        _subir(ejecutor, rec, content=iter([PDF[:15], PDF[15:]]))


def test_ejecutor_de_otra_unidad_recibe_404_y_queda_auditado(rec, media):
    ajeno = factories.usuario(Usuario.Rol.EJECUTOR, "ejecutor-ajeno", "DEP-B")

    with pytest.raises(NotFoundError):
        _subir(ajeno, rec)

    assert Evidencia.objects.count() == 0
    assert _archivos(media) == []
    denegado = AuditLog.objects.get(accion="ACCESS_DENIED", entidad_id=rec.id)
    assert denegado.resultado == "DENIED"
    assert denegado.usuario_id == ajeno.id
