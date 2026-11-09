"""Caso de uso: indicadores clave del dashboard operativo."""
from __future__ import annotations

from django.db.models import Count
from django.utils import timezone

from backend.modules.recomendaciones.infrastructure.repositories import anotar_vencimiento
from backend.modules.recomendaciones.models import InformeCGE, Recomendacion

ESTADOS_REQUERIDOS = (
    Recomendacion.Estado.PENDIENTE,
    Recomendacion.Estado.EN_PROCESO,
    Recomendacion.Estado.EN_VALIDACION,
    Recomendacion.Estado.CUMPLIDA,
)


def get_kpis() -> dict:
    counts = dict(Recomendacion.objects.values_list("estado").annotate(total=Count("id")))
    total = sum(counts.values())
    cumplidas = counts.get(Recomendacion.Estado.CUMPLIDA, 0)
    return {
        "total_recomendaciones": total,
        "recomendaciones_por_estado": {
            estado: counts.get(estado, 0) for estado in ESTADOS_REQUERIDOS
        },
        "tasa_cumplimiento_porcentaje": round(cumplidas * 100 / total, 2) if total else 0.0,
        "recomendaciones_vencidas_o_en_mora": anotar_vencimiento(
            Recomendacion.objects.all(), timezone.localdate()
        )
        .filter(vencida=True)
        .count(),
        "total_informes_cge": InformeCGE.objects.count(),
    }
