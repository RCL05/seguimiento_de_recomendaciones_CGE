import pytest

from backend.core.shared.domain_types import ConflictError, RecommendationState as State
from backend.modules.recomendaciones.domain.state_machine import (
    ALLOWED_TRANSITIONS,
    transition_state,
)


def test_machine_uses_exact_specification_states_and_transitions():
    assert set(ALLOWED_TRANSITIONS) == {
        State.PENDIENTE,
        State.EN_PROCESO,
        State.EN_VALIDACION,
        State.VENCIDA,
        State.REABIERTA,
        State.CUMPLIDA,
    }
    assert ALLOWED_TRANSITIONS == {
        State.PENDIENTE: {State.EN_PROCESO, State.VENCIDA},
        State.EN_PROCESO: {State.EN_VALIDACION, State.VENCIDA},
        State.EN_VALIDACION: {State.CUMPLIDA, State.EN_PROCESO, State.VENCIDA},
        State.VENCIDA: {State.EN_PROCESO},
        State.CUMPLIDA: {State.REABIERTA},
        State.REABIERTA: {State.EN_PROCESO},
    }


@pytest.mark.parametrize(
    ("source", "target"),
    [
        (State.PENDIENTE, State.EN_PROCESO),
        (State.EN_PROCESO, State.EN_VALIDACION),
        (State.EN_VALIDACION, State.EN_PROCESO),
        (State.VENCIDA, State.EN_PROCESO),
        (State.REABIERTA, State.EN_PROCESO),
        (State.EN_VALIDACION, State.VENCIDA),
    ],
)
def test_allows_transitions_defined_by_spec(source, target):
    assert transition_state(source, target) is target


@pytest.mark.parametrize(
    ("source", "target"),
    [
        (State.PENDIENTE, State.EN_VALIDACION),
        (State.EN_PROCESO, State.CUMPLIDA),
        (State.VENCIDA, State.CUMPLIDA),
        (State.REABIERTA, State.CUMPLIDA),
    ],
)
def test_rejects_unlisted_transitions(source, target):
    with pytest.raises(ConflictError):
        transition_state(source, target)


def test_completion_requires_validated_evidence_and_internal_review():
    with pytest.raises(ConflictError):
        transition_state(
            State.EN_VALIDACION,
            State.CUMPLIDA,
            had_internal_review=True,
            has_validated_evidence=False,
        )
    assert transition_state(
        State.EN_VALIDACION,
        State.CUMPLIDA,
        had_internal_review=True,
        has_validated_evidence=True,
    ) is State.CUMPLIDA
