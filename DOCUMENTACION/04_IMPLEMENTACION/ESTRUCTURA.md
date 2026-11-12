## Organización del repositorio

| Ruta | Contenido | Responsable lógico |
|---|---|---|
| `backend/` | Proyecto Django (paquete importable como `backend.*`) | API |
| `frontend/` | Proyecto Vite/React | SPA |
| `docs/` | Documentación Markdown histórica, ADR y portal Quarto | Documentación |
| `docs_server/` | Servidor Quart de lectura de `docs/` | Documentación |
| `specs/001-seguimiento-recomendaciones/` | Especificación SDD vigente | Requisitos |
| `.spec/` | Especificación SDD inicial (histórico) | Requisitos |
| `.specify/`, `.github/agents`, `.github/prompts`, `.github/skills` | Plantillas, scripts y agentes de Spec Kit | Proceso |
| `.github/workflows/` | `ci.yml`, `publish-quarto.yml` | Automatización |
| `DOCUMENTACION/` | Control maestro y fuentes de los capítulos del portal | Documentación |

## Backend

```text
backend/
├── manage.py                 # inserta la raíz en sys.path; DJANGO_SETTINGS_MODULE=config.settings
├── config/                   # settings.py, urls.py, asgi.py, wsgi.py
├── core/
│   ├── api/                  # ApiView, ok(), envoltura, errores, middleware, schema, health
│   ├── audit/                # AuditLog, record_audit, consultas, admin, migraciones
│   ├── auth/                 # JWTBearerAuthentication, permisos, puertos
│   ├── files/                # validate_pdf, puertos de almacenamiento
│   ├── security/             # log_safety (redacción)
│   ├── shared/               # domain_types (Role, RecommendationState, errores), unit_of_work
│   └── web/                  # vista HTML de demostración en "/"
├── modules/<módulo>/
│   ├── domain/               # reglas puras (cuando existen)
│   ├── application/          # casos de uso + audit_events.py
│   ├── infrastructure/       # repositorios, almacenamiento, adaptadores externos
│   ├── ports/                # interfaces (SSO, notificación)
│   ├── presentation/         # views.py, serializers.py, urls.py
│   ├── migrations/           # solo en apps registradas
│   └── management/commands/  # evaluar_plazos (notificaciones)
├── contracts/openapi.yaml    # contrato publicado
├── scripts/seed_initial_data.py
├── templates/, static/       # plantillas del MVP (Django Admin y vistas heredadas)
└── tests/{unit,integration,api,contract,security,concurrency}/
```

Convenciones observadas:

- Un archivo por caso de uso, nombrado con verbo (`create_recomendacion.py`, `issue_dictamen.py`, `verify_integrity.py`).
- `audit_events.py` por módulo centraliza los nombres de acciones auditadas.
- Las rutas usan sustantivos en plural y el método HTTP expresa la operación (comentario en `config/urls.py`).
- Identificadores UUID en todas las entidades de negocio; `AuditLog` usa `BigAutoField`.

## Frontend

```text
frontend/
├── index.html, vite.config.ts, tsconfig.json, eslint.config.js, playwright.config.ts
├── src/
│   ├── main.tsx, App.tsx, routes.tsx, styles.css
│   ├── api/client.ts            # tipos, sesión (sessionStorage), fetch con Bearer, ApiError
│   ├── components/              # ui.tsx, FormStepper, Toast, format, roles
│   ├── hooks/useToast.ts
│   ├── features/<área>/pages|components/
│   └── test/setup.ts            # jest-dom para Vitest
└── tests/e2e/recommendation-flow.spec.ts
```

## Archivos generados y no versionados

`.venv/`, `node_modules/`, `frontend/dist/`, `backend/development.sqlite3`, `backend/media/`, `.env`, `docs/_site/`, `docs/.quarto/` (ver `.gitignore`). Excepción: `frontend/tsconfig.tsbuildinfo` está versionado y se modifica con cada build (H-20).
