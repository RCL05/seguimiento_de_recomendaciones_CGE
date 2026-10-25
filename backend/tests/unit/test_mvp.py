import pytest

from backend.core.api.response_envelope import build_envelope
from backend.core.files.pdf_integrity import validate_pdf
from backend.core.shared.domain_types import (
    ConflictError,
    RecommendationState,
    Role,
    User,
)
from backend.modules.recomendaciones.application.service import RecommendationService


def users():
    return (
        User("uai-1", Role.UAI, "audit"),
        User("exec-1", Role.EJECUTOR, "unit-a"),
    )


def recommendation_in_execution(service, uai):
    recommendation = service.create(
        uai,
        report_id="report-1",
        number="R-001",
        description="Implementar control.",
        unit_id="unit-a",
        legal_days=30,
        due_date="2026-11-18",
        request_id="req-create",
    )
    recommendation.state = RecommendationState.EN_EJECUCION
    return recommendation


def test_pdf_hash_and_validation():
    content = b"%PDF-1.7 evidence"
    digest = validate_pdf("evidence.pdf", content)
    assert len(digest) == 64
    with pytest.raises(Exception):
        validate_pdf("evidence.txt", content)


def test_evidence_moves_recommendation_to_internal_review():
    uai, executor = users()
    service = RecommendationService()
    recommendation = recommendation_in_execution(service, uai)
    evidence = service.upload_evidence(
        executor,
        recommendation.id,
        filename="evidence.pdf",
        content=b"%PDF-1.7 evidence",
        request_id="req-upload",
    )
    assert recommendation.state is RecommendationState.EN_REVISION_INTERNA
    assert evidence.sha256
    assert len(service.audit.all()) == 2


def test_illegal_jump_to_completed_is_conflict():
    uai, _ = users()
    service = RecommendationService()
    recommendation = recommendation_in_execution(service, uai)
    with pytest.raises(ConflictError):
        from backend.modules.recomendaciones.domain.state_machine import transition

        transition(recommendation, RecommendationState.CUMPLIDA)


def test_executor_cannot_upload_for_another_unit():
    uai, executor = users()
    service = RecommendationService()
    recommendation = service.create(
        uai,
        report_id="report-1",
        number="R-002",
        description="Otra unidad.",
        unit_id="unit-b",
        legal_days=10,
        due_date="2026-10-29",
        request_id="req-create",
    )
    recommendation.state = RecommendationState.EN_EJECUCION
    with pytest.raises(Exception):
        service.upload_evidence(
            executor,
            recommendation.id,
            filename="evidence.pdf",
            content=b"%PDF-1.7 evidence",
            request_id="req-denied",
        )


def test_response_envelope_preserves_success_error_invariants():
    success = build_envelope(success=True, message="ok", data={"id": "1"})
    failure = build_envelope(success=False, message="bad", errors={"code": "CONFLICT"})
    assert success["data"] == {"id": "1"} and success["errors"] is None
    assert failure["data"] is None and failure["errors"]["code"] == "CONFLICT"
