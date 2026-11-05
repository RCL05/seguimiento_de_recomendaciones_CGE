from datetime import date

import pytest

from backend.modules.recomendaciones.models import InformeCGE, Recomendacion
from backend.modules.usuarios.models import UnidadOrganica, Usuario


@pytest.mark.django_db
def test_registro_asignacion_duplicados_y_estado_inicial():
    unit_a = UnidadOrganica.objects.create(codigo="DTI", nombre="DTI")
    unit_b = UnidadOrganica.objects.create(codigo="FIN", nombre="Financiero")
    user = Usuario.objects.create(
        correo_institucional="uai@unl.edu.ec",
        nombres="Auditoría Interna",
        rol=Usuario.Rol.UAI,
        unidad_org=unit_a,
    )
    informe = InformeCGE.objects.create(
        numero_informe="INF-INT-001",
        periodo_auditado="2025",
        fecha_notificacion=date(2026, 1, 10),
        pdf_informe_url="https://example.test/informe.pdf",
        creado_por=user,
    )

    rec1 = Recomendacion.objects.create(
        informe=informe,
        numero_recomendacion="1",
        descripcion="Control interno",
        prioridad="ALTA",
        unidad_responsable=unit_a,
        plazo_legal_dias=30,
        fecha_vencimiento_legal=date(2026, 2, 9),
    )
    assert rec1.estado == Recomendacion.Estado.PENDIENTE

    # Asignación explícita a unidad responsable
    rec2 = Recomendacion.objects.create(
        informe=informe,
        numero_recomendacion="2",
        descripcion="Rendición de cuentas",
        prioridad="MEDIA",
        unidad_responsable=unit_b,
        plazo_legal_dias=45,
        fecha_vencimiento_legal=date(2026, 2, 24),
    )
    assert rec2.unidad_responsable_id == unit_b.id

    # Duplicado por (informe, numero_recomendacion)
    with pytest.raises(Exception):
        Recomendacion.objects.create(
            informe=informe,
            numero_recomendacion="1",
            descripcion="Duplicada",
            prioridad="BAJA",
            unidad_responsable=unit_b,
            plazo_legal_dias=30,
            fecha_vencimiento_legal=date(2026, 2, 9),
        )
