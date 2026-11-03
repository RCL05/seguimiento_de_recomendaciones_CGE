from __future__ import annotations

from datetime import date

from django.db.models import Count, Q

from backend.modules.recomendaciones.models import Recomendacion


def get_dashboard(*, unit_id: str | None = None):
    qs = Recomendacion.objects.all()
    if unit_id:
        qs = qs.filter(unidad_responsable_id=unit_id)

    total = qs.count()
    cumplidas = qs.filter(estado=Recomendacion.Estado.CUMPLIDA).count()
    en_mora = qs.filter(estado=Recomendacion.Estado.EN_MORA).count()
    porcentaje_cumplimiento = round((cumplidas / total * 100), 2) if total else 0.0

    por_unidad = (
        qs.values("unidad_responsable__codigo", "unidad_responsable__nombre")
        .annotate(
            total=Count("id"),
            cumplidas=Count("id", filter=Q(estado=Recomendacion.Estado.CUMPLIDA)),
            en_mora=Count("id", filter=Q(estado=Recomendacion.Estado.EN_MORA)),
        )
        .order_by("unidad_responsable__codigo")
    )

    return {
        "porcentaje_cumplimiento": porcentaje_cumplimiento,
        "semaforo": "VERDE" if porcentaje_cumplimiento >= 80 else ("AMARILLO" if porcentaje_cumplimiento >= 50 else "ROJO"),
        "unidades_en_mora": list(por_unidad),
        "totales": {"total": total, "cumplidas": cumplidas, "en_mora": en_mora},
        "fecha_corte": date.today().isoformat(),
    }
