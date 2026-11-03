from dataclasses import dataclass
from datetime import date

from backend.core.shared.domain_types import ValidationError


@dataclass(frozen=True)
class PlanAccionHito:
    descripcion_hito: str
    fecha_compromiso: date

    def __post_init__(self):
        if not self.descripcion_hito or not self.descripcion_hito.strip():
            raise ValidationError("La descripción del hito es obligatoria.")
        if self.fecha_compromiso is None:
            raise ValidationError("La fecha de compromiso es obligatoria.")


def validar_fechas_hito_contra_vencimiento(
    fecha_compromiso: date,
    fecha_vencimiento_legal: date,
) -> None:
    """Las fechas comprometidas no deben exceder la fecha de vencimiento legal."""
    if fecha_compromiso > fecha_vencimiento_legal:
        raise ValidationError("La fecha de compromiso no puede exceder la fecha de vencimiento legal.")
