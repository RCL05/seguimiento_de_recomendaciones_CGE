"""Caso de uso: registrar una recomendación CGE (RF-006).

Reglas de negocio:
- Solo el rol UAI puede crear recomendaciones.
- El informe debe existir.
- La unidad responsable debe existir.
- plazo_legal_dias > 0.
- El número de recomendación debe ser único dentro del informe.
- Estado inicial: PENDIENTE.
- Se audita la creación dentro de la misma transacción.
"""
from __future__ import annotations

from datetime import date
from uuid import UUID

from django.db import IntegrityError, transaction

from backend.core.audit.repository import record_audit
from backend.core.shared.domain_types import ConflictError, DomainError, ValidationError
from backend.modules.recomendaciones.infrastructure.repositories import (
    RecommendationRepository,
    ReportRepository,
)
from backend.modules.recomendaciones.models import Recomendacion
from backend.modules.usuarios.models import UnidadOrganica, Usuario


class CreateRecomendacion:
    def __init__(
        self,
        report_repo: ReportRepository | None = None,
        rec_repo: RecommendationRepository | None = None,
    ) -> None:
        self._report_repo = report_repo or ReportRepository()
        self._rec_repo = rec_repo or RecommendationRepository()

    @transaction.atomic
    def execute(
        self,
        *,
        actor: Usuario,
        request_id: UUID,
        report_id: UUID,
        number: str,
        description: str,
        unit_id: str,
        legal_days: int,
        due_date: date,
        priority: str = "MEDIA",
        ip_address: str | None = None,
    ) -> Recomendacion:
        # Validaciones básicas
        if not all([report_id, number, description, unit_id]):
            raise ValidationError("Faltan campos obligatorios: informe, número, descripción y unidad.")
        if legal_days <= 0:
            raise ValidationError("El plazo legal debe ser mayor que cero.")

        # Informe debe existir
        report = self._report_repo.get(report_id)
        if report is None:
            raise DomainError("El informe CGE especificado no existe.")

        # Unidad responsable debe existir
        unit = UnidadOrganica.objects.filter(codigo=unit_id).first()
        if unit is None:
            raise DomainError(f"La unidad responsable '{unit_id}' no existe.")

        try:
            rec = Recomendacion.objects.create(
                informe=report,
                numero_recomendacion=number,
                descripcion=description,
                prioridad=priority,
                unidad_responsable=unit,
                plazo_legal_dias=legal_days,
                fecha_vencimiento_legal=due_date,
                estado=Recomendacion.Estado.PENDIENTE,
            )
        except IntegrityError as exc:
            raise ConflictError(
                "Ya existe una recomendación con ese número en el informe."
            ) from exc

        record_audit(
            request_id=request_id,
            user=actor,
            action="CREATE",
            entity="recomendacion",
            entity_id=rec.id,
            new_state=rec.estado,
            ip_address=ip_address,
            modulo="recomendaciones",
        )
        return rec
