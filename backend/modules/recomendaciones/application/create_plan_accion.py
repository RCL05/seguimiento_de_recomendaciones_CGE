"""Caso de uso: registrar un hito del plan de acción (RF-007).

Reglas de negocio:
- Solo el ejecutor de la unidad responsable puede registrar hitos.
- La recomendación debe estar en PENDIENTE o EN_PLANIFICACION para aceptar hitos.
  Si está PENDIENTE, avanza automáticamente a EN_PLANIFICACION.
- La fecha de compromiso no puede exceder fecha_vencimiento_legal.
- Al guardar el primer hito se transiciona a EN_EJECUCION.
- Operación atómica con select_for_update.
- Se audita dentro de la misma transacción.
"""
from __future__ import annotations

from datetime import date
from uuid import UUID

from django.db import transaction

from backend.core.audit.repository import record_audit
from backend.core.shared.domain_types import ConflictError, NotFoundError, ValidationError
from backend.modules.recomendaciones.models import PlanAccion, Recomendacion
from backend.modules.usuarios.models import Usuario


class CreatePlanAccion:
    @transaction.atomic
    def execute(
        self,
        *,
        actor: Usuario,
        request_id: UUID,
        recommendation_id: UUID,
        description: str,
        commitment_date: date,
        ip_address: str | None = None,
    ) -> PlanAccion:
        # Bloqueo pesimista sobre la fila de la recomendación
        rec = (
            Recomendacion.objects.select_for_update()
            .select_related("unidad_responsable")
            .filter(pk=recommendation_id)
            .first()
        )
        if rec is None:
            raise NotFoundError("La recomendación no existe.")

        # Autorización a nivel de objeto: el ejecutor debe pertenecer a la unidad
        if actor.unidad_org_id != rec.unidad_responsable_id:
            record_audit(
                request_id=request_id,
                user=actor,
                action="ACCESS_DENIED",
                entity="recomendacion",
                entity_id=rec.id,
                details={"reason": "different_unit"},
                resultado="DENIED",
                ip_address=ip_address,
                modulo="recomendaciones",
            )
            raise NotFoundError("La recomendación no existe.")

        # Validaciones de datos
        if not description:
            raise ValidationError("La descripción del hito es obligatoria.")
        if not commitment_date:
            raise ValidationError("La fecha de compromiso es obligatoria.")
        if commitment_date > rec.fecha_vencimiento_legal:
            raise ValidationError(
                "La fecha de compromiso no puede exceder el plazo legal de la recomendación."
            )

        # Transición de estado
        if rec.estado == Recomendacion.Estado.PENDIENTE:
            rec.estado = Recomendacion.Estado.EN_PLANIFICACION

        if rec.estado not in {
            Recomendacion.Estado.EN_PLANIFICACION,
            Recomendacion.Estado.RECHAZADA_CORRECCION,
        }:
            raise ConflictError(
                f"La recomendación en estado '{rec.estado}' no acepta planes de acción."
            )

        previous_state = rec.estado
        rec.estado = Recomendacion.Estado.EN_EJECUCION

        plan = PlanAccion.objects.create(
            recomendacion=rec,
            descripcion_hito=description,
            fecha_compromiso=commitment_date,
            creado_por=actor,
        )
        rec.save(update_fields=["estado"])

        record_audit(
            request_id=request_id,
            user=actor,
            action="CREATE_PLAN",
            entity="recomendacion",
            entity_id=rec.id,
            previous_state=previous_state,
            new_state=rec.estado,
            details={"plan_id": str(plan.id)},
            ip_address=ip_address,
            modulo="recomendaciones",
        )
        return plan
