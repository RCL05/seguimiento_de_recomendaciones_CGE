## Variables de entorno

Plantilla: `backend/.env.example`. Los archivos `.env` y `.env.*` están ignorados por Git. La columna *Leída por el código* se verificó buscando cada variable en `backend/` y `frontend/src/`.

| Variable | Por defecto | Leída por el código | Uso |
|---|---|---|---|
| `DJANGO_DEBUG` | `false` | Sí (`settings.py`) | Modo depuración; activa tokens SSO de desarrollo. Actívelo solo en local |
| `DJANGO_SECRET_KEY` | aleatoria si `DEBUG`; obligatoria si no | Sí | Clave de Django y de JWT si falta `JWT_SIGNING_KEY` |
| `JWT_SIGNING_KEY` | `DJANGO_SECRET_KEY` | Sí (`sso_adapter.py`) | Firma HS256; ≥ 32 caracteres |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Sí | Hosts permitidos (separados por comas) |
| `DJANGO_LOG_LEVEL` | `INFO` | Sí (`settings.py`) | Nivel del logger raíz hacia consola |
| `DJANGO_CORS_ALLOWED_ORIGINS` | Vite local si `DEBUG`; vacío si no | Sí | Orígenes CORS |
| `DJANGO_MEDIA_ROOT` | `backend/media` | Sí | Raíz de PDF |
| `DJANGO_SQLITE_PATH` | `backend/development.sqlite3` | Sí | Ruta de SQLite |
| `POSTGRES_DB` | vacío | Sí | Si tiene valor, activa PostgreSQL |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_HOST` / `POSTGRES_PORT` | `postgres` / vacío / `localhost` / `5432` | Sí | Conexión PostgreSQL |
| `MAX_PDF_SIZE_BYTES` | `31457280` (30 MB) | Sí (`upload_evidencia.py`) | Tamaño máximo de PDF |
| `SSO_INTROSPECTION_URL` | vacío | Sí | Endpoint de introspección OAuth2 |
| `SSO_CLIENT_ID` / `SSO_CLIENT_SECRET` | vacío | Sí | Credenciales del cliente SSO |
| `EMAIL_HOST` | vacío | Sí | Servidor SMTP; vacío + `DEBUG` → correo por consola |
| `EMAIL_PORT` / `EMAIL_TIMEOUT` | `587` / `10` | Sí | Puerto y timeout SMTP |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | vacío | Sí | Credenciales SMTP |
| `EMAIL_USE_TLS` / `EMAIL_USE_SSL` | `true` / `false` | Sí | STARTTLS o SMTPS (excluyentes) |
| `EMAIL_BACKEND` | según `EMAIL_HOST`/`DEBUG` | Sí | Fuerza backend de correo (`smtp`, `console`, `locmem`) |
| `DEFAULT_FROM_EMAIL` | `SITRA-CGE <no-reply@unl.edu.ec>` | Sí | Remitente |
| `SCHEDULER_INTERVAL_SECONDS` | `3600` | Sí (comando del servicio `scheduler`) | Frecuencia del job |
| `GUNICORN_WORKERS` / `GUNICORN_TIMEOUT` | `3` / `60` | Sí (contenedor) | Workers y timeout de Gunicorn |
| `VITE_API_BASE` | `""` (misma URL) | Sí (`frontend/src/api/client.ts`) | Base de la API para el build del frontend |
| `VITE_BACKEND_PROXY_TARGET` | `http://127.0.0.1:8000` | Sí (`vite.config.ts`) | Destino del proxy de desarrollo |
| `POSTGRES_HOST_PORT` | `5432` | Sí (Compose) | Puerto publicado de PostgreSQL |
| `APP_ENV` | `development` | **No** | Sin efecto |
| `SSO_ISSUER`, `SSO_REDIRECT_URI` | — | **No** | Reservadas; sin efecto |
| `EVIDENCE_STORAGE_BACKEND`, `EVIDENCE_S3_BUCKET`, `EVIDENCE_S3_ENDPOINT`, `EVIDENCE_S3_ACCESS_KEY`, `EVIDENCE_S3_SECRET_KEY` | — | **No** | Reservadas; no existe adaptador S3 (H-04) |

## Configuración funcional en tiempo de ejecución

Administrada por la DTI desde la SPA (`/administracion/notificaciones`) o la API (`PUT /api/v1/notificaciones/configuracion`):

| Parámetro | Por defecto | Rango |
|---|---|---|
| `umbral_dias` | 15 | 1–90 |
| `notificaciones_activas`, `canal_interno_activo`, `canal_email_activo` | `true` | booleano |
| `destinatarios_vencimiento` | `["UAI"]` | roles |
| `destinatarios_mora` | `["UAI", "RECTORADO"]` | roles |

Las preferencias por usuario (`PUT /api/v1/notificaciones/preferencias`) pueden desactivar canales para cada tipo de alerta. Todos los cambios se auditan; las claves que parezcan secretos se rechazan.

## Ejemplo de `.env` mínimo para un entorno no local

```dotenv
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=<valor aleatorio largo desde el gestor de secretos>
JWT_SIGNING_KEY=<otro valor aleatorio de 32+ caracteres>
DJANGO_ALLOWED_HOSTS=sitra.example.edu.ec
DJANGO_CORS_ALLOWED_ORIGINS=https://sitra.example.edu.ec
POSTGRES_DB=sitra_cge
POSTGRES_USER=sitra_app
POSTGRES_PASSWORD=<secreto>
POSTGRES_HOST=db
SSO_INTROSPECTION_URL=<URL entregada por la DTI>
SSO_CLIENT_ID=sitra-cge
SSO_CLIENT_SECRET=<secreto>
EMAIL_HOST=<servidor SMTP>
EMAIL_HOST_USER=<cuenta>
EMAIL_HOST_PASSWORD=<secreto>
```
