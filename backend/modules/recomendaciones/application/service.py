from uuid import uuid4

from backend.core.audit.in_memory import AuditLog
from backend.core.auth.authorization import require_role, require_same_unit
from backend.core.files.pdf_integrity import validate_pdf
from backend.core.shared.domain_types import (
    AuditEvent,
    ConflictError,
    Evidence,
    NotFoundError,
    Recommendation,
    RecommendationState,
    Role,
    User,
    ValidationError,
    ensure,
)
from ..domain.state_machine import transition


class RecommendationService:
    def __init__(self, audit: AuditLog | None = None) -> None:
        self.recommendations: dict[str, Recommendation] = {}
        self.evidences: dict[str, Evidence] = {}
        self.plans: dict[str, dict] = {}
        self.audit = audit or AuditLog()

    def create(
        self,
        user: User,
        *,
        report_id: str,
        number: str,
        description: str,
        unit_id: str,
        legal_days: int,
        due_date: str,
        request_id: str,
    ) -> Recommendation:
        require_role(user, Role.UAI)
        ensure(bool(report_id and number and description and unit_id), "Faltan campos obligatorios.")
        ensure(legal_days > 0, "El plazo legal debe ser mayor que cero.")
        recommendation = Recommendation(
            id=str(uuid4()),
            report_id=report_id,
            number=number,
            description=description,
            unit_id=unit_id,
            legal_days=legal_days,
            due_date=due_date,
        )
        self.recommendations[recommendation.id] = recommendation
        self._audit(user, request_id, "CREATE", recommendation, None, recommendation.state.value)
        return recommendation

    def upload_evidence(
        self,
        user: User,
        recommendation_id: str,
        *,
        filename: str,
        content: bytes,
        request_id: str,
    ) -> Evidence:
        recommendation = self._get(recommendation_id)
        require_same_unit(user, recommendation.unit_id)
        if recommendation.state not in {
            RecommendationState.EN_EJECUCION,
            RecommendationState.RECHAZADA_CORRECCION,
        }:
            raise ConflictError("La recomendación no acepta evidencias en su estado actual.")
        digest = validate_pdf(filename, content)
        evidence = Evidence(
            id=str(uuid4()),
            recommendation_id=recommendation.id,
            filename=filename,
            content=content,
            sha256=digest,
            uploaded_by=user.id,
        )
        self.evidences[evidence.id] = evidence
        previous = recommendation.state.value
        transition(recommendation, RecommendationState.EN_REVISION_INTERNA)
        self._audit(user, request_id, "UPLOAD_EVIDENCE", recommendation, previous, recommendation.state.value)
        return evidence

    def issue_dictamen(
        self,
        user: User,
        recommendation_id: str,
        *,
        evidence_id: str,
        approved: bool,
        request_id: str,
    ) -> Recommendation:
        require_role(user, Role.UAI)
        recommendation = self._get(recommendation_id)
        evidence = self.evidences.get(evidence_id)
        if evidence is None or evidence.recommendation_id != recommendation.id:
            raise ValidationError("La evidencia no pertenece a la recomendación.")
        previous = recommendation.state.value
        if approved:
            evidence.validated = True
            transition(
                recommendation,
                RecommendationState.CUMPLIDA,
                has_validated_evidence=True,
            )
        else:
            transition(recommendation, RecommendationState.RECHAZADA_CORRECCION)
        self._audit(user, request_id, "ISSUE_DICTAMEN", recommendation, previous, recommendation.state.value)
        return recommendation

    def _get(self, recommendation_id: str) -> Recommendation:
        recommendation = self.recommendations.get(recommendation_id)
        if recommendation is None:
            raise NotFoundError("La recomendación no existe.")
        return recommendation

    def _audit(
        self,
        user: User,
        request_id: str,
        action: str,
        recommendation: Recommendation,
        previous: str | None,
        new: str | None,
    ) -> None:
        self.audit.record(
            AuditEvent(
                user_id=user.id,
                request_id=request_id,
                action=action,
                entity="recommendation",
                entity_id=recommendation.id,
                previous_state=previous,
                new_state=new,
            )
        )
