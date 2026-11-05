from datetime import date

import pytest

from backend.core.shared.domain_types import ConflictError, RecommendationState as State
from backend.modules.recomendaciones.domain.state_machine import (
    ALLOWED_TRANSITIONS,
    transition_state,
)
from backend.modules.recomendaciones.domain.vencimiento import esta_vencida, fecha_compromiso_valida


def test_machine_uses_exact_specification_states_and_transitions():
    # Opción 2: el vencimiento es un indicador, no un estado del flujo.
    assert set(ALLOWED_TRANSITIONS) == {
        State.PENDIENTE,
        State.EN_PROCESO,
        State.EN_VALIDACION,
        State.REABIERTA,
        State.CUMPLIDA,
    }
    assert ALLOWED_TRANSITIONS == {
        State.PENDIENTE: {State.EN_PROCESO},
        State.EN_PROCESO: {State.EN_VALIDACION},
        State.EN_VALIDACION: {State.CUMPLIDA, State.EN_PROCESO},
        State.CUMPLIDA: {State.REABIERTA},
        State.REABIERTA: {State.EN_PROCESO},
    }
    assert not hasattr(State, "VENCIDA")


@pytest.mark.parametrize(
    ("source", "target"),
    [
        (State.PENDIENTE, State.EN_PROCESO),
        (State.EN_PROCESO, State.EN_VALIDACION),
        (State.EN_VALIDACION, State.EN_PROCESO),
        (State.CUMPLIDA, State.REABIERTA),
        (State.REABIERTA, State.EN_PROCESO),
    ],
)
def test_allows_transitions_defined_by_spec(source, target):
    assert transition_state(source, target) is target


@pytest.mark.parametrize(
    ("source", "target"),
    [
        (State.PENDIENTE, State.EN_VALIDACION),
        (State.EN_PROCESO, State.CUMPLIDA),
        (State.REABIERTA, State.CUMPLIDA),
        (State.CUMPLIDA, State.EN_PROCESO),
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


VENCE = date(2026, 6, 30)


@pytest.mark.parametrize(
    ("estado", "hoy", "entrega_oportuna", "esperado"),
    [
        (State.EN_PROCESO, date(2026, 6, 30), False, False),  # el último día aún está en plazo
        (State.EN_PROCESO, date(2026, 7, 1), False, True),
        (State.PENDIENTE, date(2026, 7, 1), False, True),
        (State.REABIERTA, date(2026, 7, 1), False, True),
        (State.CUMPLIDA, date(2026, 7, 1), False, False),
        # Entregó a tiempo y la UAI no ha dictaminado: la demora no se imputa al ejecutor.
        (State.EN_VALIDACION, date(2026, 7, 15), True, False),
        # Entregó tarde: sigue vencida mientras se revisa.
        (State.EN_VALIDACION, date(2026, 7, 15), False, True),
    ],
)
def test_regla_de_vencimiento(estado, hoy, entrega_oportuna, esperado):
    assert (
        esta_vencida(
            estado=estado,
            fecha_vencimiento=VENCE,
            hoy=hoy,
            entrega_oportuna_en_revision=entrega_oportuna,
        )
        is esperado
    )


def test_fecha_de_hito_dentro_y_fuera_de_plazo():
    dentro = date(2026, 6, 1)
    assert fecha_compromiso_valida(compromiso=date(2026, 6, 30), fecha_vencimiento=VENCE, hoy=dentro) is None
    assert fecha_compromiso_valida(compromiso=date(2026, 7, 1), fecha_vencimiento=VENCE, hoy=dentro)

    vencido = date(2026, 7, 10)
    assert fecha_compromiso_valida(compromiso=date(2026, 8, 1), fecha_vencimiento=VENCE, hoy=vencido) is None
    assert fecha_compromiso_valida(compromiso=date(2026, 7, 9), fecha_vencimiento=VENCE, hoy=vencido)
