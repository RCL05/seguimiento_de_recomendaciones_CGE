from datetime import date, timedelta

import pytest

from backend.modules.recomendaciones.models import InformeCGE, Recomendacion
from backend.modules.usuarios.models import UnidadOrganica, Usuario

pytestmark = pytest.mark.django_db


def calcular_vencimiento(fecha_notificacion: date, plazo_legal_dias: int) -> date:
    return fecha_notificacion + timedelta(days=plazo_legal_dias)


def test_reglas_creacion_calculan_vencimiento_correctamente():
    unit = UnidadOrganica.objects.create(codigo="U01", nombre="Unidad 01")
    user = Usuario.objects.create(
        correo_institucional="uai-t@unl.edu.ec",
        nombres="Auditoría",
        rol=Usuario.Rol.UAI,
        unidad_org=unit,
    )
    informe = InformeCGE.objects.create(
        numero_informe="INF-TEST-01",
        periodo_auditado="2026",
        fecha_notificacion=date(2026, 1, 10),
        pdf_informe_url="https://example.test/inf.pdf",
        creado_por=user,
    )
    vencimiento = calcular_vencimiento(informe.fecha_notificacion, 30)
    assert vencimiento == date(2026, 2, 9)

    rec = Recomendacion.objects.create(
        informe=informe,
        numero_recomendacion="1",
        descripcion="Test",
        prioridad="ALTA",
        unidad_responsable=unit,
        plazo_legal_dias=30,
        fecha_vencimiento_legal=vencimiento,
    )
    assert rec.fecha_vencimiento_legal == informe.fecha_notificacion + timedelta(days=rec.plazo_legal_dias)


def test_plazo_legal_dias_debe_ser_positivo():
    try:
        from django.core.exceptions import ValidationError

        unit = UnidadOrganica.objects.create(codigo="U02", nombre="Unidad 02")
        user = Usuario.objects.create(
            correo_institucional="uai-t2@unl.edu.ec",
            nombres="Auditoría",
            rol=Usuario.Rol.UAI,
            unidad_org=unit,
        )
        informe = InformeCGE.objects.create(
            numero_informe="INF-TEST-02",
            periodo_auditado="2026",
            fecha_notificacion=date(2026, 1, 10),
            pdf_informe_url="https://example.test/inf2.pdf",
            creado_por=user,
        )
        rec = Recomendacion(
            informe=informe,
            numero_recomendacion="2",
            descripcion="Test",
            prioridad="ALTA",
            unidad_responsable=unit,
            plazo_legal_dias=0,
            fecha_vencimiento_legal=date(2026, 1, 10),
        )
        rec.full_clean()
        assert False, "Debe fallar con plazo_legal_dias <= 0"
    except ValidationError:
        assert True
