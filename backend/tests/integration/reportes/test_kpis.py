from datetime import date, timedelta

import pytest

from backend.modules.recomendaciones.models import InformeCGE, Recomendacion
from backend.modules.reportes.application.get_kpis import get_kpis
from backend.modules.usuarios.models import UnidadOrganica, Usuario

pytestmark = pytest.mark.django_db


def test_get_kpis_agrega_estados_cumplimiento_y_mora():
    unit = UnidadOrganica.objects.create(codigo="DEP-K", nombre="Unidad KPI")
    user = Usuario.objects.create(
        correo_institucional="kpi@unl.edu.ec",
        nombres="Usuario KPI",
        rol=Usuario.Rol.UAI,
        unidad_org=unit,
    )
    informe = InformeCGE.objects.create(
        numero_informe="INF-KPI-1",
        periodo_auditado="2025",
        fecha_notificacion=date(2026, 1, 1),
        creado_por=user,
    )
    base = {
        "informe": informe,
        "descripcion": "Hallazgo de prueba",
        "prioridad": "ALTA",
        "unidad_responsable": unit,
        "plazo_legal_dias": 30,
    }
    Recomendacion.objects.create(
        **base,
        numero_recomendacion="REC-KPI-1",
        fecha_vencimiento_legal=date.today() - timedelta(days=5),
        estado=Recomendacion.Estado.EN_PROCESO,
    )
    Recomendacion.objects.create(
        **base,
        numero_recomendacion="REC-KPI-2",
        fecha_vencimiento_legal=date.today() + timedelta(days=30),
        estado=Recomendacion.Estado.CUMPLIDA,
    )

    kpis = get_kpis()

    assert kpis["total_recomendaciones"] == 2
    assert kpis["recomendaciones_por_estado"] == {
        "PENDIENTE": 0,
        "EN_PROCESO": 1,
        "EN_VALIDACION": 0,
        "CUMPLIDA": 1,
    }
    assert kpis["tasa_cumplimiento_porcentaje"] == 50.0
    assert kpis["recomendaciones_vencidas_o_en_mora"] == 1
    assert kpis["total_informes_cge"] == 1
