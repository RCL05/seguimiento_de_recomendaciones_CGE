import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = Path(os.getenv("DJANGO_MEDIA_ROOT", BASE_DIR / "media"))
MEDIA_URL = "/media/"
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if not DEBUG:
        raise RuntimeError("DJANGO_SECRET_KEY es obligatorio cuando DEBUG está desactivado.")
    SECRET_KEY = secrets.token_urlsafe(48)
ROOT_URLCONF = "config.urls"
ALLOWED_HOSTS = [host for host in os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",") if host]
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "backend.core.audit.apps.AuditConfig",
    "backend.modules.usuarios.apps.UsuariosConfig",
    "backend.modules.recomendaciones.apps.RecomendacionesConfig",
    "backend.modules.reportes.apps.ReportesConfig",
    "backend.modules.notificaciones.apps.NotificacionesConfig",
    "rest_framework",
    "corsheaders",
]
MIDDLEWARE = [
    # CORS va primero para responder preflights OPTIONS antes de la autenticación.
    "corsheaders.middleware.CorsMiddleware",
    "backend.core.api.middleware.ApiErrorEnvelopeMiddleware",
    "django.middleware.security.SecurityMiddleware",
]

# CORS: orígenes explícitos por entorno (lista separada por comas). Sin valor, en
# desarrollo se admite el servidor de Vite; fuera de DEBUG no se admite ningún origen.
_default_cors_origins = "http://localhost:5173,http://127.0.0.1:5173" if DEBUG else ""
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in (os.getenv("DJANGO_CORS_ALLOWED_ORIGINS") or _default_cors_origins).split(",")
    if origin.strip()
]
CORS_URLS_REGEX = r"^/(api|health)/.*$"
CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "x-filename",
    "x-evidence-type",
    "x-request-id",
)
CORS_EXPOSE_HEADERS = ("Location", "Content-Disposition")
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "backend.core.api.exception_handler.handle_exception",
}
DEFAULT_EXCEPTION_REPORTER_FILTER = "django.views.debug.SafeExceptionReporterFilter"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
TIME_ZONE = "America/Guayaquil"
if os.getenv("POSTGRES_DB"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["POSTGRES_DB"],
            "USER": os.getenv("POSTGRES_USER", "postgres"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "HOST": os.getenv("POSTGRES_HOST", "localhost"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "development.sqlite3",
        }
    }
#prueba de conexion de comits en discord :)S
