"""Caso de uso: tablero ejecutivo de riesgo institucional (RF-013, HU-4)."""
from __future__ import annotations

from django.db.models import Count, Q
from django.utils import timezone

from backend.core.shared.domain_types import PermissionDenied
from backend.modules.recomendaciones.models import Recomendacion
from backend.modules.usuarios.models import Usuario

ROLES_TABLERO = {Usuario.Rol.RECTORADO, Usuario.Rol.UAI, Usuario.Rol.CGE_AUDITOR}

# Semáforo por porcentaje global de recomendaciones cumplidas.
UMBRAL_VERDE = 75
UMBRAL_AMARILLO = 40


def semaforo_para(porcentaje: float) -> str:
    if porcentaje >= UMBRAL_VERDE:
        return "VERDE"
    if porcentaje >= UMBRAL_AMARILLO:
        return "AMARILLO"
    return "ROJO"


def get_dashboard(*, actor: Usuario) -> dict:
    if actor.rol not in ROLES_TABLERO:
        raise PermissionDenied("No tiene permisos para consultar el tablero.")

    por_estado = {
        row["estado"]: row["total"]
        for row in Recomendacion.objects.values("estado").annotate(total=Count("id"))
    }
    total = sum(por_estado.values())
    cumplidas = por_estado.get(Recomendacion.Estado.CUMPLIDA, 0)
    porcentaje = round((cumplidas / total) * 100, 2) if total else 0

    unidades_en_mora = [
        {
            "unidad_codigo": row["unidad_responsable__codigo"],
            "unidad_nombre": row["unidad_responsable__nombre"],
            "vencidas": row["vencidas"],
            "total": row["total"],
        }
        for row in (
            Recomendacion.objects.values("unidad_responsable__codigo", "unidad_responsable__nombre")
            .annotate(
                total=Count("id"),
                vencidas=Count("id", filter=Q(estado=Recomendacion.Estado.VENCIDA)),
            )
            .filter(vencidas__gt=0)
            .order_by("-vencidas", "unidad_responsable__codigo")
        )
    ]

    return {
        "total": total,
        "cumplimiento_porcentaje": porcentaje,
        "semaforo_riesgo": semaforo_para(porcentaje),
        "en_mora": por_estado.get(Recomendacion.Estado.VENCIDA, 0),
        "en_revision_interna": por_estado.get(Recomendacion.Estado.EN_VALIDACION, 0),
        "por_estado": por_estado,
        "unidades_en_mora": unidades_en_mora,
        "fecha_corte": timezone.localdate(),
    }
