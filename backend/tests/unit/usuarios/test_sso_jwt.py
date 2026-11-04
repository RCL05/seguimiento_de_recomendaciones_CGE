from datetime import datetime, timedelta, timezone

import jwt

from backend.modules.usuarios.infrastructure.sso_adapter import SsoAdapter


def test_emits_jwt_with_expiration_and_authorization_claims(monkeypatch):
    monkeypatch.setenv("JWT_SIGNING_KEY", "test-signing-key-with-at-least-32-characters")
    adapter = SsoAdapter()
    token = adapter.issue_session(
        {
            "user_id": "user-123",
            "email": "person@example.test",
            "role": "EJECUTOR",
            "unit_id": "UNIT-01",
        },
        expires_in=120,
    )

    claims = jwt.decode(
        token,
        "test-signing-key-with-at-least-32-characters",
        algorithms=["HS256"],
        audience=adapter.audience,
        issuer=adapter.issuer,
    )
    assert claims["sub"] == "user-123"
    assert claims["user_id"] == "user-123"
    assert claims["email"] == "person@example.test"
    assert claims["role"] == "EJECUTOR"
    assert claims["unit_id"] == "UNIT-01"
    assert claims["exp"] - claims["iat"] == 120
    assert adapter.validate_session(token)["rol"] == "EJECUTOR"


def test_rejects_expired_or_tampered_jwt(monkeypatch):
    monkeypatch.setenv("JWT_SIGNING_KEY", "test-signing-key-with-at-least-32-characters")
    adapter = SsoAdapter()
    claims = {
        "iss": adapter.issuer,
        "aud": adapter.audience,
        "sub": "user-123",
        "user_id": "user-123",
        "email": "person@example.test",
        "role": "UAI",
        "unit_id": None,
        "iat": datetime.now(timezone.utc) - timedelta(minutes=2),
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        "jti": "token-id",
    }
    expired = jwt.encode(claims, adapter._signing_key(), algorithm="HS256")
    assert adapter.validate_session(expired) == {}
    assert adapter.validate_session(expired + "x") == {}
