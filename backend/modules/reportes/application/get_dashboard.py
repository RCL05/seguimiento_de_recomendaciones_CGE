"""Caso de uso: tablero ejecutivo de riesgo institucional (RF-013, HU-4)."""
from __future__ import annotations

from collections import Counter

from django.utils import timezone

from backend.core.shared.domain_types import PermissionDenied
from backend.modules.recomendaciones.infrastructure.repositories import anotar_vencimiento
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

    hoy = timezone.localdate()
    filas = list(
        anotar_vencimiento(Recomendacion.objects.all(), hoy).values_list(
            "estado",
            "vencida",
            "unidad_responsable__codigo",
            "unidad_responsable__nombre",
        )
    )
    por_estado = Counter(estado for estado, *_ in filas)
    total = len(filas)
    cumplidas = por_estado.get(Recomendacion.Estado.CUMPLIDA, 0)
    porcentaje = round((cumplidas / total) * 100, 2) if total else 0

    totales_unidad: Counter = Counter()
    vencidas_unidad: Counter = Counter()
    for _, vencida, codigo, nombre in filas:
        totales_unidad[(codigo, nombre)] += 1
        if vencida:
            vencidas_unidad[(codigo, nombre)] += 1

    unidades_en_mora = [
        {"unidad_codigo": codigo, "unidad_nombre": nombre, "vencidas": vencidas, "total": totales_unidad[(codigo, nombre)]}
        for (codigo, nombre), vencidas in sorted(vencidas_unidad.items(), key=lambda item: (-item[1], item[0][0]))
    ]

    return {
        "total": total,
        "cumplimiento_porcentaje": porcentaje,
        "semaforo_riesgo": semaforo_para(porcentaje),
        "en_mora": sum(vencidas_unidad.values()),
        "en_revision_interna": por_estado.get(Recomendacion.Estado.EN_VALIDACION, 0),
        "por_estado": dict(por_estado),
        "unidades_en_mora": unidades_en_mora,
        "fecha_corte": hoy,
    }
