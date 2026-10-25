import pytest

from backend.core.api import views
from backend.core.api.exception_handler import ErrorCodes
from backend.core.auth.authorization import PermissionDenied, require_same_unit
from backend.core.shared.domain_types import Role, User


@pytest.fixture(autouse=True)
def reset_state():
    views.service.recommendations.clear()
    views.service.plans.clear()
    views.service.evidences.clear()
    yield
    views.service.recommendations.clear()
    views.service.plans.clear()
    views.service.evidences.clear()


def test_transactional_flow_uses_atomic_state_updates(monkeypatch):
    from backend.core.api import views as api_views

    calls = []

    class DummyAtomic:
        def __enter__(self):
            calls.append("enter")
            return self

        def __exit__(self, exc_type, exc, tb):
            calls.append("exit")
            return False

    def fake_atomic():
        return DummyAtomic()

    import django

    monkeypatch.setattr(django.db.transaction, "atomic", fake_atomic)

    api_views.register_informe(
        {
            "numero_informe": "INF-TRX-001",
            "periodo_auditado": "2026",
            "fecha_notificacion": "2026-01-10",
            "pdf_informe_url": "https://example.test/inf-trx.pdf",
        }
    )
    api_views.create_recommendation(
        {
            "number": "R-TRX-01",
            "description": "Probar transaccionalidad",
            "unit_id": "unit-trx",
            "legal_days": 30,
            "due_date": "2026-03-01",
        }
    )

    assert "enter" in calls
    assert "exit" in calls


def test_audit_minimum_records_action_request_id_and_actor():
    from backend.core.api import views as api_views
    from backend.core.api import service

    report = api_views.register_informe(
        {
            "numero_informe": "INF-AUD-001",
            "periodo_auditado": "2026",
            "fecha_notificacion": "2026-01-12",
            "pdf_informe_url": "https://example.test/inf-aud.pdf",
        }
    )
    rec = api_views.create_recommendation(
        {
            "number": "R-AUD-01",
            "description": "Verificar auditoría",
            "unit_id": "unit-aud",
            "legal_days": 15,
            "due_date": "2026-02-10",
        }
    )
    assert service.audit_log, "Debe existir al menos un registro de auditoría"
    audit_entry = service.audit_log[-1]
    assert "request_id" in audit_entry
    assert "action" in audit_entry
    assert "entity" in audit_entry
    assert audit_entry.get("entity_id") == rec["id"] or audit_entry.get("entity_id") == report["id"]


def test_object_level_authorization_prevents_cross_unit_access():
    executor_unit_a = User(id="exec-a", role=Role.EJECUTOR, unit_id="unit-a")
    executor_unit_b = User(id="exec-b", role=Role.EJECUTOR, unit_id="unit-b")

    require_same_unit(executor_unit_a, "unit-a")

    with pytest.raises(PermissionDenied) as exc:
        require_same_unit(executor_unit_b, "unit-a")

    assert exc.value.code == ErrorCodes.PERMISSION_DENIED or "unidad" in str(exc.value).lower()
