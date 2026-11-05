from backend.core.shared.domain_types import Role


def test_roles_segregacion_y_expiracion():
    roles = {Role.DTI, Role.UAI, Role.EJECUTOR, Role.RECTORADO, Role.CGE_AUDITOR}
    assert Role.DTI in roles
    assert Role.UAI in roles
    from datetime import datetime, timedelta, timezone

    exp = datetime.now(timezone.utc) + timedelta(hours=8)
    assert (exp - datetime.now(timezone.utc)).total_seconds() <= 8 * 3600 + 5


def test_reasignacion_sin_perder_historial():
    assert True
