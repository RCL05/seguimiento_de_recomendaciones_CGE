## Requisitos previos

| Herramienta | Versión mínima | Verificado en la auditoría | Uso |
|---|---|---|---|
| Git | cualquiera reciente | Sí | Clonar el repositorio |
| Python | 3.10 (`requires-python >=3.10`); 3.12 recomendado (Docker y CI) | 3.13.14 | Backend y servidor de documentación |
| Node.js + npm | 18 (README); 22 en CI y Compose | v26.4.0 | Frontend |
| Docker + Docker Compose v2 | — | No instalado (no verificado) | Entorno contenedorizado opcional |
| PostgreSQL | 16 (imagen `postgres:16-alpine`) | No verificado | Opcional; sin él se usa SQLite |
| Quarto | 1.4 o superior (probado con 1.11.9) | Sí | Solo para construir este portal |

## Puertos

| Puerto | Servicio |
|---|---|
| 8000 | API Django (`/api/v1`, `/api/docs/`, `/admin/`, `/health/`) |
| 5173 | Frontend Vite |
| 8001 | Servidor Quart de documentación Markdown |
| 5432 | PostgreSQL (Compose, `POSTGRES_HOST_PORT`) |

## Dependencias

- Backend: `backend/requirements.txt` (Django, DRF, drf-spectacular, django-cors-headers, PyJWT, psycopg, tzdata…). Pruebas: `pytest`, `pytest-django` (extra `test` de `pyproject.toml`).
- Documentación Markdown: `docs_server/requirements.txt` (Quart, Markdown).
- Frontend: `frontend/package.json` + `package-lock.json` (instalación reproducible con `npm ci`).

## Requisitos de producción (no cubiertos por el repositorio)

Servidor Linux con HTTPS (proxy inverso), servidor WSGI/ASGI de producción, PostgreSQL gestionado con respaldos, volumen privado para PDF, SMTP institucional, proveedor SSO y programador de tareas. Ver *Despliegue*.
