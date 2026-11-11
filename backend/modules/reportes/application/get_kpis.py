"""Caso de uso: indicadores clave del dashboard operativo.

Alcance por rol (mismo criterio que RF-019):
- Ejecutor: solo las recomendaciones de su unidad; sin unidad, indicadores en cero.
- UAI, Rectorado, Auditor CGE y DTI: indicadores institucionales agregados.
"""
from __future__ import annotations

from django.db.models import Count
from django.utils import timezone

from backend.modules.recomendaciones.infrastructure.repositories import anotar_vencimiento
from backend.modules.recomendaciones.models import InformeCGE, Recomendacion
from backend.modules.usuarios.models import Usuario

ESTADOS_REQUERIDOS = (
    Recomendacion.Estado.PENDIENTE,
    Recomendacion.Estado.EN_PROCESO,
    Recomendacion.Estado.EN_VALIDACION,
    Recomendacion.Estado.CUMPLIDA,
)


def _scope(actor: Usuario | None):
    recomendaciones = Recomendacion.objects.all()
    informes = InformeCGE.objects.all()
    if actor is not None and actor.rol == Usuario.Rol.EJECUTOR:
        recomendaciones = recomendaciones.filter(unidad_responsable_id=actor.unidad_org_id)
        if actor.unidad_org_id is None:
            recomendaciones = recomendaciones.none()
        informes = informes.filter(pk__in=recomendaciones.values("informe_id"))
    return recomendaciones, informes


def get_kpis(actor: Usuario | None = None) -> dict:
    recomendaciones, informes = _scope(actor)
    counts = dict(recomendaciones.values_list("estado").annotate(total=Count("id")))
    total = sum(counts.values())
    cumplidas = counts.get(Recomendacion.Estado.CUMPLIDA, 0)
    return {
        "total_recomendaciones": total,
        "recomendaciones_por_estado": {
            estado: counts.get(estado, 0) for estado in ESTADOS_REQUERIDOS
        },
        "tasa_cumplimiento_porcentaje": round(cumplidas * 100 / total, 2) if total else 0.0,
        "recomendaciones_vencidas_o_en_mora": anotar_vencimiento(
            recomendaciones, timezone.localdate()
        )
        .filter(vencida=True)
        .count(),
        "total_informes_cge": informes.count(),
    }
