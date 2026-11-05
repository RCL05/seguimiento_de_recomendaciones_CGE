"""Regla de vencimiento de recomendaciones (decisión del equipo: opción 2).

"Vencida" NO es un estado del flujo de cumplimiento: es una condición derivada
del plazo legal. Una recomendación puede estar En Proceso o En Validación y,
además, vencida; se puede cumplir tarde y el dictamen UAI sigue disponible.

Una recomendación está vencida cuando:
- no está CUMPLIDA,
- la fecha actual (America/Guayaquil) es posterior a su fecha de vencimiento legal, y
- no tiene una evidencia entregada a tiempo que siga pendiente de dictamen
  (la demora en la revisión de la UAI no se imputa al ejecutor).
"""
from __future__ import annotations

from datetime import date

from backend.core.shared.domain_types import RecommendationState


def esta_vencida(
    *,
    estado: RecommendationState | str,
    fecha_vencimiento: date,
    hoy: date,
    entrega_oportuna_en_revision: bool,
) -> bool:
    estado = RecommendationState(estado)
    if estado is RecommendationState.CUMPLIDA:
        return False
    if hoy <= fecha_vencimiento:
        return False
    if estado is RecommendationState.EN_VALIDACION and entrega_oportuna_en_revision:
        return False
    return True


def fecha_compromiso_valida(*, compromiso: date, fecha_vencimiento: date, hoy: date) -> str | None:
    """Devuelve el motivo de rechazo de una fecha de hito, o None si es válida (RF-007).

    Dentro del plazo, el hito no puede exceder el plazo legal. Con el plazo ya
    vencido, el plazo legal no se modifica y el hito debe comprometerse desde hoy.
    """
    if hoy <= fecha_vencimiento:
        if compromiso > fecha_vencimiento:
            return "La fecha de compromiso no puede exceder el plazo legal de la recomendación."
        return None
    if compromiso < hoy:
        return "El plazo legal ya venció: la fecha de compromiso debe ser hoy o posterior."
    return None
