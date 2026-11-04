from backend.core.shared.domain_types import (
    ConflictError,
    Recommendation,
    RecommendationState,
    ValidationError,
)


ALLOWED_TRANSITIONS = {
    RecommendationState.PENDIENTE: {RecommendationState.EN_PROCESO, RecommendationState.VENCIDA},
    RecommendationState.EN_PROCESO: {RecommendationState.EN_VALIDACION, RecommendationState.VENCIDA},
    RecommendationState.EN_VALIDACION: {
        RecommendationState.CUMPLIDA,
        RecommendationState.EN_PROCESO,
        RecommendationState.VENCIDA,
    },
    RecommendationState.VENCIDA: {RecommendationState.EN_PROCESO},
    RecommendationState.CUMPLIDA: {RecommendationState.REABIERTA},
    RecommendationState.REABIERTA: {RecommendationState.EN_PROCESO},
}


def transition(
    recommendation: Recommendation,
    target: RecommendationState,
    *,
    has_validated_evidence: bool = False,
) -> None:
    recommendation.state = transition_state(
        recommendation.state,
        target,
        had_internal_review=recommendation.had_internal_review,
        has_validated_evidence=has_validated_evidence,
    )
    if target is RecommendationState.EN_VALIDACION:
        recommendation.had_internal_review = True


def transition_state(
    current_state: RecommendationState | str,
    target: RecommendationState,
    *,
    had_internal_review: bool = False,
    has_validated_evidence: bool = False,
) -> RecommendationState:
    current_state = RecommendationState(current_state)
    allowed = ALLOWED_TRANSITIONS[current_state]
    if target not in allowed:
        raise ConflictError(
            f"Transición inválida: {current_state.value} -> {target.value}."
        )
    if target is RecommendationState.CUMPLIDA:
        if not had_internal_review or not has_validated_evidence:
            raise ConflictError(
                "Cumplida requiere revisión interna y evidencia PDF validada."
            )
    return target
