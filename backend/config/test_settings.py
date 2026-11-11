"""Configuración de Django para la suite automatizada.

Las pruebas no usan secretos reales ni envían correo. Se define una
`DJANGO_SECRET_KEY` efímera antes de cargar `config.settings`, porque el valor
seguro por defecto de `DEBUG` es `false` y Django exige la clave en ese caso.
"""

import os

os.environ.setdefault(
    "DJANGO_SECRET_KEY",
    "pytest-only-secret-key-not-for-production-0123456789",
)
os.environ["EMAIL_BACKEND"] = "django.core.mail.backends.locmem.EmailBackend"
# Las pruebas inician muchas sesiones seguidas; el límite se prueba aparte.
os.environ.setdefault("LOGIN_THROTTLE_RATE", "10000/min")

from .settings import *  # noqa: E402,F401,F403

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
