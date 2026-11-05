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
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "backend.core.audit.apps.AuditConfig",
    "backend.modules.usuarios.apps.UsuariosConfig",
    "backend.modules.recomendaciones.apps.RecomendacionesConfig",
    "backend.modules.reportes.apps.ReportesConfig",
    "backend.modules.notificaciones.apps.NotificacionesConfig",
    "rest_framework",
    "drf_spectacular",
    "corsheaders",
]
MIDDLEWARE = [
    # CORS va primero para responder preflights OPTIONS antes de la autenticación.
    "corsheaders.middleware.CorsMiddleware",
    "backend.core.api.middleware.ApiErrorEnvelopeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
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
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "backend.core.auth.authentication.JWTBearerAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "backend.core.auth.permissions.IsAuthenticatedActor",
    ],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
    # Sin django.contrib.auth: el usuario es `Usuario`, resuelto por JWTBearerAuthentication.
    "UNAUTHENTICATED_USER": None,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "SITRA-CGE UNL API",
    "DESCRIPTION": (
        "API del Sistema de Seguimiento de Recomendaciones de la Contraloría General "
        "del Estado (CGE) para la Universidad Nacional de Loja. Toda respuesta JSON usa "
        "la envoltura universal `success`, `message`, `data`, `errors`, `meta`."
    ),
    "VERSION": "1.0.0",
    "OAS_VERSION": "3.0.3",
    "SERVE_INCLUDE_SCHEMA": False,
    "SERVE_AUTHENTICATION": [],
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": r"/api/v1",
    "ENUM_NAME_OVERRIDES": {
        "RolInstitucionalEnum": "backend.modules.usuarios.models.Usuario.Rol",
        "EstadoRecomendacionEnum": "backend.modules.recomendaciones.models.Recomendacion.Estado",
        "EstadoEvidenciaEnum": "backend.modules.recomendaciones.models.Evidencia.Estado",
        "TipoEvidenciaEnum": "backend.modules.recomendaciones.models.Evidencia.Tipo",
        "PrioridadEnum": "backend.modules.recomendaciones.presentation.serializers.PRIORIDADES",
    },
    "SWAGGER_UI_SETTINGS": {"persistAuthorization": True, "displayRequestDuration": True},
}

LANGUAGE_CODE = "es"
USE_I18N = True

# Plantillas: necesarias para Swagger UI (drf-spectacular) en /api/docs/.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]},
    }
]
DEFAULT_EXCEPTION_REPORTER_FILTER = "django.views.debug.SafeExceptionReporterFilter"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
STATIC_URL = "/static/"
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
            "NAME": os.getenv("DJANGO_SQLITE_PATH") or BASE_DIR / "development.sqlite3",
        }
    }
#prueba de conexion de comits en discord :)S
