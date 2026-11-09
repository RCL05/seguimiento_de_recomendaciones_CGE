"""Caso de uso: registrar un hito del plan de acción (RF-007).

Reglas de negocio:
- Solo el ejecutor de la unidad responsable puede registrar hitos.
- Una recomendación Pendiente o Reabierta inicia ejecución (pasa a En Proceso).
- Una recomendación En Proceso puede recibir hitos adicionales (aunque esté vencida).
- Dentro del plazo, el hito no excede fecha_vencimiento_legal; con el plazo
  vencido, el hito se compromete desde hoy (domain/vencimiento.py).
- La transición de inicio pasa por la máquina de estados.
- Operación atómica con select_for_update.
- Se audita dentro de la misma transacción.
"""
from __future__ import annotations

from datetime import date
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from backend.core.audit.repository import record_audit
from backend.core.shared.domain_types import (
    ConflictError,
    NotFoundError,
    RecommendationState,
    ValidationError,
)
from backend.modules.recomendaciones.domain.state_machine import transition_state
from backend.modules.recomendaciones.domain.vencimiento import fecha_compromiso_valida
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
        motivo = fecha_compromiso_valida(
            compromiso=commitment_date,
            fecha_vencimiento=rec.fecha_vencimiento_legal,
            hoy=timezone.localdate(),
        )
        if motivo:
            raise ValidationError(motivo)

        # Transición de estado
        previous_state = rec.estado
        if rec.estado in {
            Recomendacion.Estado.PENDIENTE,
            Recomendacion.Estado.REABIERTA,
        }:
            rec.estado = transition_state(rec.estado, RecommendationState.EN_PROCESO)
        elif rec.estado != Recomendacion.Estado.EN_PROCESO:
            raise ConflictError(
                f"La recomendación en estado '{rec.estado}' no acepta planes de acción."
            )

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
