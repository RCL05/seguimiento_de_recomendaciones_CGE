from datetime import date

import pytest

from backend.core.shared.domain_types import ConflictError, RecommendationState
from backend.modules.recomendaciones.domain.state_machine import transition
from backend.modules.recomendaciones.models import Evidencia, InformeCGE, Recomendacion
from backend.modules.usuarios.models import UnidadOrganica, Usuario


@pytest.mark.django_db
def test_cumplida_requiere_revision_interna_y_evidencia_validada():
    unit = UnidadOrganica.objects.create(codigo="UAI", nombre="UAI")
    user = Usuario.objects.create(
        correo_institucional="uai@unl.edu.ec",
        nombres="UAI",
        rol=Usuario.Rol.UAI,
        unidad_org=unit,
    )
    informe = InformeCGE.objects.create(
        numero_informe="INF-MVP-001",
        periodo_auditado="2026",
        fecha_notificacion=date(2026, 1, 1),
        pdf_informe_url="https://example.test/inf.pdf",
        creado_por=user,
    )
    rec = Recomendacion.objects.create(
        informe=informe,
        numero_recomendacion="1",
        descripcion="Test",
        prioridad="ALTA",
        unidad_responsable=unit,
        plazo_legal_dias=30,
        fecha_vencimiento_legal=date(2026, 1, 31),
        estado=Recomendacion.Estado.EN_REVISION_INTERNA,
    )
    ev = Evidencia.objects.create(
        recomendacion=rec,
        nombre_archivo="ev.pdf",
        mime_type="application/pdf",
        tamano_bytes=100,
        url_almacenamiento="/media/ev.pdf",
        hash_sha256="d" * 64,
        subido_por=user,
        validada=False,
    )
    from backend.core.shared.domain_types import Recommendation

    r = Recommendation(
        id=str(rec.id),
        report_id=str(rec.informe_id),
        number=rec.numero_recomendacion,
        description=rec.descripcion,
        unit_id=str(rec.unidad_responsable_id),
        legal_days=rec.plazo_legal_dias,
        due_date=str(rec.fecha_vencimiento_legal),
        state=RecommendationState.EN_REVISION_INTERNA,
        had_internal_review=True,
    )
    with pytest.raises(ConflictError):
        transition(r, RecommendationState.CUMPLIDA, has_validated_evidence=False)
    transition(r, RecommendationState.CUMPLIDA, has_validated_evidence=True)
    ev.validada = True
    ev.save(update_fields=["validada"])
    rec.estado = Recomendacion.Estado.CUMPLIDA
    rec.save(update_fields=["estado"])
    rec.refresh_from_db()
    assert rec.estado == Recomendacion.Estado.CUMPLIDA
