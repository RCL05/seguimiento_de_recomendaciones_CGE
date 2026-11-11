## Ejecución local en tres terminales

Active `.venv` en cada terminal que ejecute Python.

| Terminal | Directorio | Comando | URL |
|---|---|---|---|
| 1 — API | `backend/` | `python manage.py runserver` | http://localhost:8000/ |
| 2 — Documentación Markdown (opcional) | **raíz** del repositorio | `python docs_server/app.py` | http://localhost:8001/ |
| 3 — Frontend | `frontend/` | `npm run dev` | http://localhost:5173/ |

El servidor Quart debe iniciarse desde la raíz porque resuelve `docs/` relativo al repositorio. En el entorno de escritorio del proyecto existe además `.claude/launch.json` con las configuraciones `backend` (127.0.0.1:8000) y `frontend` (127.0.0.1:5173).

## Puntos de acceso

| Servicio | URL |
|---|---|
| SPA | http://localhost:5173/ |
| Swagger UI | http://localhost:8000/api/docs/ |
| Esquema OpenAPI | http://localhost:8000/api/schema/ |
| Django Admin | http://localhost:8000/admin/ |
| Salud | http://localhost:8000/health/ |

## Iniciar sesión en desarrollo

Con `DJANGO_DEBUG=true`, en la pantalla de inicio de sesión se escribe uno de estos tokens:

| Token | Rol | Unidad |
|---|---|---|
| `uai-sso-token` | UAI | UAI |
| `ejecutor-sso-token` | EJECUTOR | DEP-A |
| `dti-sso-token` | DTI | DTI |
| `rectorado-sso-token` | RECTORADO | RECTORADO |

Desde la línea de comandos:

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login-sso \
  -H "Content-Type: application/json" -d '{"credential":"uai-sso-token"}'
```

## Evaluación de plazos

```bash
python backend/manage.py evaluar_plazos
```

Es idempotente y puede programarse con cron:

```cron
0 * * * * cd /opt/sitra/backend && /opt/sitra/.venv/bin/python manage.py evaluar_plazos
```

O ejecutarse manualmente como DTI con `POST /api/v1/evaluaciones-plazos`.

## Pruebas

```bash
cd backend && python -m pytest -q
cd frontend && npm test && npm run lint && npm run build
```

## Construir el portal de documentación

```bash
quarto render docs        # genera docs/_site/
quarto preview docs       # servidor local con recarga
```
