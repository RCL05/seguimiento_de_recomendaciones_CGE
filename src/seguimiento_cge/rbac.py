from __future__ import annotations

from datetime import UTC, datetime
from typing import Dict, Iterable, List, Tuple

from .models import EstadoRecomendacion, HistorialAuditoria, Recomendacion, Rol, Usuario

Transition = Tuple[EstadoRecomendacion, EstadoRecomendacion]


class InvalidTransitionError(ValueError):
    pass


class PermissionDeniedError(PermissionError):
    pass


class StateMachine:
    """Máquina de estados con control RBAC para recomendaciones CGE."""

    _allowed: Dict[Rol, Iterable[Transition]] = {
        Rol.ADMINISTRADOR: {
            (EstadoRecomendacion.REGISTRADA, EstadoRecomendacion.EN_PLANIFICACION),
            (EstadoRecomendacion.EN_PLANIFICACION, EstadoRecomendacion.NO_APLICABLE),
            (EstadoRecomendacion.EN_REVISION_UAI, EstadoRecomendacion.CERRADA),
            (EstadoRecomendacion.EN_REVISION_UAI, EstadoRecomendacion.EN_EJECUCION),
            (EstadoRecomendacion.CERRADA, EstadoRecomendacion.EN_REVISION_UAI),
            (EstadoRecomendacion.NO_APLICABLE, EstadoRecomendacion.EN_PLANIFICACION),
        },
        Rol.MAXIMA_AUTORIDAD: {
            (EstadoRecomendacion.EN_REVISION_UAI, EstadoRecomendacion.CERRADA),
            (EstadoRecomendacion.CERRADA, EstadoRecomendacion.EN_REVISION_UAI),
        },
        Rol.RESPONSABLE_EJECUTOR: {
            (EstadoRecomendacion.EN_PLANIFICACION, EstadoRecomendacion.EN_EJECUCION),
            (EstadoRecomendacion.EN_EJECUCION, EstadoRecomendacion.EN_REVISION_UAI),
            (EstadoRecomendacion.EN_EJECUCION, EstadoRecomendacion.EN_PLANIFICACION),
        },
        Rol.CONSULTOR_OBSERVADOR: set(),
    }

    def __init__(self) -> None:
        self._audit_log: List[HistorialAuditoria] = []

    @property
    def audit_log(self) -> List[HistorialAuditoria]:
        return list(self._audit_log)

    def can_transition(
        self,
        rol: Rol,
        current: EstadoRecomendacion,
        target: EstadoRecomendacion,
    ) -> bool:
        return (current, target) in self._allowed.get(rol, set())

    def transition(
        self,
        recomendacion: Recomendacion,
        target: EstadoRecomendacion,
        actor: Usuario,
    ) -> HistorialAuditoria:
        current = recomendacion.estado_actual
        if current == target:
            raise InvalidTransitionError("El estado origen y destino no pueden ser iguales")

        if not self.can_transition(actor.rol, current, target):
            raise PermissionDeniedError(
                f"El rol {actor.rol.value} no puede mover {current.value} -> {target.value}"
            )

        recomendacion.estado_actual = target
        audit = HistorialAuditoria(
            id=len(self._audit_log) + 1,
            entidad_afectada="Recomendacion",
            registro_id=recomendacion.id,
            usuario_id=actor.id,
            accion_realizada="transition",
            valor_anterior=current.value,
            valor_nuevo=target.value,
            timestamp=datetime.now(UTC),
        )
        self._audit_log.append(audit)
        return audit
