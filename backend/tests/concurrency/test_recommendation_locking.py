from datetime import date

import pytest
from django.db import transaction

from backend.modules.recomendaciones.models import Evidencia, InformeCGE, Recomendacion
from backend.modules.usuarios.models import UnidadOrganica, Usuario


@pytest.mark.django_db
def test_concurrencia_dictamen_con_select_for_update():
    unit = UnidadOrganica.objects.create(codigo="C01", nombre="C01")
    user = Usuario.objects.create(
        correo_institucional="uai-c@unl.edu.ec",
        nombres="UAI",
        rol=Usuario.Rol.UAI,
        unidad_org=unit,
    )
    informe = InformeCGE.objects.create(
        numero_informe="INF-C-001",
        periodo_auditado="2026",
        fecha_notificacion=date(2026, 1, 1),
        pdf_informe_url="https://example.test/inf.pdf",
        creado_por=user,
    )
    rec = Recomendacion.objects.create(
        informe=informe,
        numero_recomendacion="99",
        descripcion="Test",
        prioridad="ALTA",
        unidad_responsable=unit,
        plazo_legal_dias=30,
        fecha_vencimiento_legal=date(2026, 1, 31),
        estado=Recomendacion.Estado.EN_REVISION_INTERNA,
    )
    Evidencia.objects.create(
        recomendacion=rec,
        nombre_archivo="ev.pdf",
        mime_type="application/pdf",
        tamano_bytes=100,
        url_almacenamiento="/media/ev.pdf",
        hash_sha256="e" * 64,
        subido_por=user,
        validada=False,
    )

    with transaction.atomic():
        locked = Recomendacion.objects.select_for_update().get(pk=rec.pk)
        assert locked.estado == Recomendacion.Estado.EN_REVISION_INTERNA
