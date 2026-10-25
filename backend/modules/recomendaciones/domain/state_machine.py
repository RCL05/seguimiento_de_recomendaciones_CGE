from backend.core.shared.domain_types import (
    ConflictError,
    Recommendation,
    RecommendationState,
    ValidationError,
)


ALLOWED_TRANSITIONS = {
    RecommendationState.PENDIENTE: {RecommendationState.EN_PLANIFICACION},
    RecommendationState.EN_PLANIFICACION: {RecommendationState.EN_EJECUCION},
    RecommendationState.EN_EJECUCION: {RecommendationState.EN_REVISION_INTERNA},
    RecommendationState.EN_REVISION_INTERNA: {
        RecommendationState.CUMPLIDA,
        RecommendationState.RECHAZADA_CORRECCION,
    },
    RecommendationState.RECHAZADA_CORRECCION: {
        RecommendationState.EN_EJECUCION,
        RecommendationState.EN_REVISION_INTERNA,
    },
    RecommendationState.EN_MORA: set(),
    RecommendationState.CUMPLIDA: set(),
}


def transition(
    recommendation: Recommendation,
    target: RecommendationState,
    *,
    has_validated_evidence: bool = False,
) -> None:
    allowed = ALLOWED_TRANSITIONS[recommendation.state]
    if target not in allowed:
        raise ConflictError(
            f"Transición inválida: {recommendation.state.value} -> {target.value}."
        )
    if target is RecommendationState.CUMPLIDA:
        if not recommendation.had_internal_review or not has_validated_evidence:
            raise ConflictError(
                "Cumplida requiere revisión interna y evidencia PDF validada."
            )
    if target is RecommendationState.EN_REVISION_INTERNA:
        recommendation.had_internal_review = True
    recommendation.state = target
