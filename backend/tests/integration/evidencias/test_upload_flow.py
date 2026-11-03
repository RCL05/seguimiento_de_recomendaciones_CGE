from datetime import date

import pytest

from backend.modules.recomendaciones.models import Evidencia, InformeCGE, PlanAccion, Recomendacion
from backend.modules.usuarios.models import UnidadOrganica, Usuario


@pytest.mark.django_db
def test_carga_valida_invalida_y_transicion_a_revision():
    unit = UnidadOrganica.objects.create(codigo="EVID", nombre="Evidencias")
    user = Usuario.objects.create(
        correo_institucional="ejecutor@unl.edu.ec",
        nombres="Ejecutor",
        rol=Usuario.Rol.EJECUTOR,
        unidad_org=unit,
    )
    informe = InformeCGE.objects.create(
        numero_informe="INF-EV-001",
        periodo_auditado="2026",
        fecha_notificacion=date(2026, 1, 10),
        pdf_informe_url="https://example.test/inf-ev.pdf",
        creado_por=user,
    )
    rec = Recomendacion.objects.create(
        informe=informe,
        numero_recomendacion="10",
        descripcion="Cargar evidencia",
        prioridad="ALTA",
        unidad_responsable=unit,
        plazo_legal_dias=30,
        fecha_vencimiento_legal=date(2026, 2, 9),
        estado=Recomendacion.Estado.EN_EJECUCION,
    )
    plan = PlanAccion.objects.create(
        recomendacion=rec,
        descripcion_hito="Hito 1",
        fecha_compromiso=date(2026, 1, 25),
        creado_por=user,
    )

    # Carga válida
    ev = Evidencia.objects.create(
        recomendacion=rec,
        plan_accion=plan,
        nombre_archivo="soporte.pdf",
        mime_type="application/pdf",
        tamano_bytes=1024,
        url_almacenamiento="/media/evidencias/test.pdf",
        hash_sha256="b" * 64,
        subido_por=user,
        validada=False,
    )
    assert ev.mime_type == "application/pdf"
    assert len(ev.hash_sha256) == 64
    assert ev.inmutable is True

    # Transición a revisión interna (simulada)
    rec.estado = Recomendacion.Estado.EN_REVISION_INTERNA
    rec.save(update_fields=["estado"])
    rec.refresh_from_db()
    assert rec.estado == Recomendacion.Estado.EN_REVISION_INTERNA

    # Carga inválida (tamaño > 30MB simulado por validación lógica)
    from django.core.exceptions import ValidationError

    ev_bad = Evidencia(
        recomendacion=rec,
        plan_accion=plan,
        nombre_archivo="grande.pdf",
        mime_type="application/pdf",
        tamano_bytes=30 * 1024 * 1024 + 1,
        url_almacenamiento="/media/evidencias/grande.pdf",
        hash_sha256="c" * 64,
        subido_por=user,
    )
    with pytest.raises(ValidationError):
        ev_bad.full_clean()
