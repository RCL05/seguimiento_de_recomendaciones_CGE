from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timedelta, timezone
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import uuid4

import jwt
from django.conf import settings
from django.db import transaction

from backend.core.shared.domain_types import Role
from backend.modules.usuarios.models import UnidadOrganica, Usuario


class SsoAdapter:
    """Validates institutional credentials and issues short-lived JWT access tokens."""

    issuer = "sitra-cge"
    audience = "sitra-cge-api"
    algorithm = "HS256"
    token_ttl_seconds = 3600

    @staticmethod
    def _signing_key() -> str:
        key = os.getenv("JWT_SIGNING_KEY") or settings.SECRET_KEY
        if not key or len(key) < 32:
            raise RuntimeError("JWT_SIGNING_KEY debe tener al menos 32 caracteres.")
        return key

    def authenticate(self, *, token: str) -> dict:
        if not token:
            return {}

        if settings.DEBUG:
            development_identity = self._development_identity(token)
            if development_identity:
                return self._persist_identity(development_identity)

        endpoint = os.getenv("SSO_INTROSPECTION_URL")
        client_id = os.getenv("SSO_CLIENT_ID")
        client_secret = os.getenv("SSO_CLIENT_SECRET")
        if not endpoint or not client_id or not client_secret:
            return {}

        body = urlencode({"token": token}).encode()
        request = Request(
            endpoint,
            data=body,
            headers={
                "Authorization": f"Basic {base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=5) as response:
                claims = json.loads(response.read())
        except (URLError, TimeoutError, ValueError):
            return {}

        if not claims.get("active"):
            return {}
        email = claims.get("email") or claims.get("correo")
        role = claims.get("role") or claims.get("rol")
        if not email or not role:
            return {}
        try:
            Role(role)
        except ValueError:
            return {}
        return self._persist_identity(
            {
                "email": email,
                "nombres": claims.get("name") or claims.get("nombres") or email,
                "rol": role,
                "unidad_codigo": claims.get("unit_id") or claims.get("unidad_codigo"),
            }
        )

    @staticmethod
    def _development_identity(token: str) -> dict:
        identities = {
            "uai-sso-token": {
                "email": "uai@unl.edu.ec",
                "nombres": "Usuario UAI",
                "rol": Role.UAI.value,
                "unidad_codigo": "UAI",
            },
            "valid-sso-token": {
                "email": "uai@unl.edu.ec",
                "nombres": "Usuario UAI",
                "rol": Role.UAI.value,
                "unidad_codigo": "UAI",
            },
            "ejecutor-sso-token": {
                "email": "ejecutor@unl.edu.ec",
                "nombres": "Usuario Ejecutor",
                "rol": Role.EJECUTOR.value,
                "unidad_codigo": "DEP-A",
            },
            "dti-sso-token": {
                "email": "dti@unl.edu.ec",
                "nombres": "Usuario DTI",
                "rol": Role.DTI.value,
                "unidad_codigo": "DTI",
            },
            "rectorado-sso-token": {
                "email": "rectorado@unl.edu.ec",
                "nombres": "Usuario Rectorado",
                "rol": Role.RECTORADO.value,
                "unidad_codigo": "RECTORADO",
            },
        }
        identity = identities.get(token)
        return identity.copy() if identity else {}

    @staticmethod
    @transaction.atomic
    def _persist_identity(identity: dict) -> dict:
        role = identity.get("rol")
        email = identity.get("email") or identity.get("correo")
        if not email or not role:
            return {}
        try:
            Role(role)
        except ValueError:
            return {}

        unit_code = identity.get("unidad_codigo")
        unit = None
        if unit_code:
            unit, _ = UnidadOrganica.objects.get_or_create(
                codigo=unit_code,
                defaults={"nombre": unit_code},
            )

        user, _ = Usuario.objects.get_or_create(
            correo_institucional=email,
            defaults={
                "nombres": identity.get("nombres") or email,
                "rol": role,
                "unidad_org": unit,
                "activo": True,
            },
        )
        if not user.activo:
            return {}
        if unit and user.unidad_org_id is None:
            user.unidad_org = unit
            user.save(update_fields=["unidad_org"])

        effective_unit = user.unidad_org
        return {
            "sub": str(user.id),
            "email": user.correo_institucional,
            "nombres": user.nombres,
            "rol": user.rol,
            "unidad_id": str(user.unidad_org_id) if user.unidad_org_id else None,
            # Compatibility keys consumed by login_sso and the JWT API view.
            "user_id": str(user.id),
            "correo": user.correo_institucional,
            "unidad_codigo": effective_unit.codigo if effective_unit else None,
        }

    def issue_session(self, identity: dict, *, expires_in: int | None = None) -> str:
        user_id = identity.get("user_id") or identity.get("id")
        email = identity.get("email") or identity.get("correo")
        role = identity.get("role") or identity.get("rol")
        unit_id = identity.get("unit_id") or identity.get("unidad_codigo")
        if not user_id or not email or not role:
            raise ValueError("JWT requiere user_id, email y role.")
        Role(role)

        now = datetime.now(timezone.utc)
        ttl = expires_in or self.token_ttl_seconds
        if ttl <= 0:
            raise ValueError("La expiración del JWT debe ser positiva.")
        claims = {
            "iss": self.issuer,
            "aud": self.audience,
            "sub": str(user_id),
            "user_id": str(user_id),
            "email": email,
            "role": role,
            "unit_id": unit_id,
            "iat": now,
            "exp": now + timedelta(seconds=ttl),
            "jti": str(uuid4()),
        }
        return jwt.encode(claims, self._signing_key(), algorithm=self.algorithm)

    def validate_session(self, token: str) -> dict:
        if not token:
            return {}
        try:
            claims = jwt.decode(
                token,
                self._signing_key(),
                algorithms=[self.algorithm],
                issuer=self.issuer,
                audience=self.audience,
                options={"require": ["exp", "iat", "iss", "aud", "sub", "user_id", "email", "role", "jti"]},
            )
            Role(claims["role"])
        except (jwt.PyJWTError, ValueError, RuntimeError):
            return {}

        return {
            "user_id": claims["user_id"],
            "correo": claims["email"],
            "rol": claims["role"],
            "unidad_codigo": claims.get("unit_id"),
            "exp": claims["exp"],
            "jti": claims["jti"],
        }
