"""Reglas de registro de recomendaciones (RF-006) en el caso de uso CreateRecomendacion."""

from datetime import date
from uuid import uuid4

import pytest
from django.core.exceptions import ValidationError as DjangoValidationError

from backend.core.audit.models import AuditLog
from backend.core.shared.domain_types import ConflictError, DomainError, ValidationError
from backend.modules.recomendaciones.application.create_recomendacion import CreateRecomendacion
from backend.modules.recomendaciones.models import InformeCGE, Recomendacion
from backend.modules.usuarios.models import Usuario
from tests import factories

pytestmark = pytest.mark.django_db


@pytest.fixture
def uai():
    return factories.usuario(Usuario.Rol.UAI, "uai-creacion", "UAI")


@pytest.fixture
def informe(uai):
    factories.unidad("DEP-A")
    return InformeCGE.objects.create(
        numero_informe="INF-CREA-01",
        periodo_auditado="2026",
        fecha_notificacion=date(2026, 1, 10),
        pdf_informe_url="https://example.test/inf.pdf",
        creado_por=uai,
    )


def _crear(uai, informe, **cambios):
    datos = {
        "report_id": informe.id,
        "number": "1",
        "description": "Actualizar el reglamento.",
        "unit_id": "DEP-A",
        "legal_days": 30,
        "due_date": date(2026, 2, 9),
        "priority": "ALTA",
    }
    datos.update(cambios)
    return CreateRecomendacion().execute(actor=uai, request_id=uuid4(), **datos)


def test_se_crea_pendiente_asignada_a_la_unidad_y_auditada(uai, informe):
    rec = _crear(uai, informe)

    assert rec.estado == Recomendacion.Estado.PENDIENTE
    assert rec.unidad_responsable.codigo == "DEP-A"
    assert rec.fecha_vencimiento_legal == date(2026, 2, 9)
    audit = AuditLog.objects.get(entidad_id=rec.id, accion="CREATE")
    assert audit.usuario_id == uai.id
    assert audit.estado_nuevo == "PENDIENTE"


@pytest.mark.parametrize("dias", [0, -5])
def test_plazo_legal_no_positivo_se_rechaza(uai, informe, dias):
    with pytest.raises(ValidationError):
        _crear(uai, informe, legal_days=dias)
    assert Recomendacion.objects.count() == 0


def test_el_modelo_tambien_rechaza_plazo_cero(informe):
    rec = Recomendacion(
        informe=informe,
        numero_recomendacion="2",
        descripcion="Test",
        prioridad="ALTA",
        unidad_responsable=factories.unidad("DEP-A"),
        plazo_legal_dias=0,
        fecha_vencimiento_legal=date(2026, 1, 10),
    )
    with pytest.raises(DjangoValidationError) as error:
        rec.full_clean()
    assert "plazo_legal_dias" in error.value.message_dict


def test_numero_repetido_en_el_mismo_informe_es_conflicto(uai, informe):
    _crear(uai, informe)

    with pytest.raises(ConflictError):
        _crear(uai, informe)
    assert Recomendacion.objects.count() == 1


def test_el_mismo_numero_en_otro_informe_se_permite(uai, informe):
    otro = InformeCGE.objects.create(
        numero_informe="INF-CREA-02",
        periodo_auditado="2026",
        fecha_notificacion=date(2026, 1, 10),
        pdf_informe_url="https://example.test/inf2.pdf",
        creado_por=uai,
    )
    _crear(uai, informe)
    _crear(uai, otro)

    assert Recomendacion.objects.filter(numero_recomendacion="1").count() == 2


def test_informe_o_unidad_inexistentes_se_rechazan_sin_crear_nada(uai, informe):
    with pytest.raises(DomainError):
        _crear(uai, informe, report_id=uuid4())
    with pytest.raises(DomainError):
        _crear(uai, informe, unit_id="NO-EXISTE")
    assert Recomendacion.objects.count() == 0
    assert not AuditLog.objects.filter(accion="CREATE", entidad="recomendacion").exists()
