"""Límite de intentos para el inicio de sesión (mitiga fuerza bruta sobre el SSO)."""
from __future__ import annotations

from django.conf import settings
from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    """Cuenta los intentos de login por IP de conexión.

    Usa `REMOTE_ADDR` y no `X-Forwarded-For`, porque el cliente puede falsificar
    esa cabecera. Detrás de un proxy, este debe fijar `REMOTE_ADDR`.
    La tasa se lee en cada solicitud desde `LOGIN_THROTTLE_RATE`.
    """

    scope = "login"

    def get_rate(self) -> str | None:
        return getattr(settings, "LOGIN_THROTTLE_RATE", "10/min")

    def get_cache_key(self, request, view) -> str:
        return self.cache_format % {
            "scope": self.scope,
            "ident": request.META.get("REMOTE_ADDR") or "unknown",
        }
