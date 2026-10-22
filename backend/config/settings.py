import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = Path(os.getenv("DJANGO_MEDIA_ROOT", BASE_DIR / "media"))
MEDIA_URL = "/media/"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "development-only-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"
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
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
]
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
