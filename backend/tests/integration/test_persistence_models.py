from datetime import date

import pytest

from backend.modules.recomendaciones.models import InformeCGE, Recomendacion
from backend.modules.usuarios.models import UnidadOrganica, Usuario


@pytest.mark.django_db
def test_recommendation_persistence_enforces_unique_report_number():
    unit = UnidadOrganica.objects.create(codigo="DTI", nombre="Tecnologías")
    user = Usuario.objects.create(
        correo_institucional="uai@unl.edu.ec",
        nombres="Auditoría Interna",
        rol=Usuario.Rol.UAI,
        unidad_org=unit,
    )
    report = InformeCGE.objects.create(
        numero_informe="INF-001",
        periodo_auditado="2025",
        fecha_notificacion=date(2026, 1, 10),
        pdf_informe_url="https://example.test/informe.pdf",
        creado_por=user,
    )
    Recomendacion.objects.create(
        informe=report,
        numero_recomendacion="1",
        descripcion="Controlar el seguimiento",
        prioridad="ALTA",
        unidad_responsable=unit,
        plazo_legal_dias=30,
        fecha_vencimiento_legal=date(2026, 2, 9),
    )
    with pytest.raises(Exception):
        Recomendacion.objects.create(
            informe=report,
            numero_recomendacion="1",
            descripcion="Duplicada",
            prioridad="BAJA",
            unidad_responsable=unit,
            plazo_legal_dias=30,
            fecha_vencimiento_legal=date(2026, 2, 9),
        )
