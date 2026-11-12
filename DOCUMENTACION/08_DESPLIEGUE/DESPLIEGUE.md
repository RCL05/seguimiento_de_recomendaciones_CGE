## Estado

El repositorio contiene configuración de **contenedores** e **integración continua**. El backend del contenedor ya arranca con **Gunicorn** y aplica valores seguros por defecto (`DJANGO_DEBUG=false`, hosts locales). Todavía no incluye proxy TLS ni automatización completa de despliegue productivo; esta página describe lo existente y separa las recomendaciones.

## Dockerfile del backend (`backend/Dockerfile`)

| Instrucción | Efecto |
|---|---|
| `FROM python:3.12-slim` | Imagen base |
| `ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 GUNICORN_WORKERS=3 GUNICORN_TIMEOUT=60` | Sin `.pyc`; salida sin búfer; parámetros de Gunicorn |
| `WORKDIR /workspace/backend` | Directorio de trabajo |
| `COPY requirements.txt` + `pip install` | Dependencias en capa propia (caché) |
| `COPY . .` | Código (excluye lo listado en `backend/.dockerignore`) |
| `EXPOSE 8000` | Puerto de la API |
| `CMD migrate --noinput && exec gunicorn config.wsgi:application ...` | Migra y arranca con el servidor WSGI de producción |

## Docker Compose (`docker-compose.yml`)

| Servicio | Imagen / build | Depende de | Salud | Volúmenes |
|---|---|---|---|---|
| `db` | `postgres:16-alpine` | — | `pg_isready` cada 5 s | `postgres_data` |
| `backend` | build `./backend` | `db` sano | `GET /health/` cada 10 s | `backend_media` |
| `scheduler` | build `./backend` | `db` sano | — | `backend_media` |
| `frontend` | `node:22-alpine` (`npm ci && npm run dev`) | `backend` sano | — | `./frontend` montado, `frontend_node_modules` |

Todos los servicios usan `restart: unless-stopped`.

## Integración continua (`.github/workflows/ci.yml`)

| Job | Entorno | Pasos |
|---|---|---|
| `backend` | ubuntu-latest, Python 3.12, caché pip | instalar → `manage.py check` → `pytest -q` |
| `frontend` | ubuntu-latest, Node 22, caché npm | `npm ci` → lint → Vitest → build |

Disparadores: `push` a `main`, `develop`, `feature/**`; `pull_request`.

## Publicación del portal (`.github/workflows/publish-quarto.yml`)

Creado en esta auditoría. Construye `docs/` con Quarto y lo publica en GitHub Pages. Ver *Publicación en GitHub Pages*.

## Recomendación para producción (implementación parcial)

```{mermaid}
flowchart LR
  u([Usuarios]) -->|HTTPS| px["Proxy inverso<br/>Nginx · TLS · HSTS"]
  px -->|/| st["Build estático del frontend<br/>(npm run build → dist/)"]
  px -->|/api, /health| app["Gunicorn/Uvicorn<br/>Django · DEBUG=false"]
  app --> pg[("PostgreSQL gestionado<br/>respaldos cifrados")]
  app --> vol[("Volumen privado de PDF")]
  cron["Programador<br/>evaluar_plazos"] --> pg
```

Lista de verificación:

1. `DJANGO_DEBUG=false`, `DJANGO_SECRET_KEY` y `JWT_SIGNING_KEY` desde un gestor de secretos.
2. `DJANGO_ALLOWED_HOSTS` y `DJANGO_CORS_ALLOWED_ORIGINS` explícitos.
3. `python manage.py check --deploy` sin advertencias críticas; configurar `SECURE_HSTS_SECONDS`, `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`.
4. El contenedor ya usa Gunicorn; falta el proxy inverso con TLS/HSTS y la política de workers por entorno.
5. Migraciones como paso controlado del despliegue, con respaldo previo.
6. `MEDIA_ROOT` en volumen privado, respaldado junto con la base de datos.
7. Programador de `evaluar_plazos` monitoreado.
8. Frontend compilado con `VITE_API_BASE` apuntando a la API pública.
