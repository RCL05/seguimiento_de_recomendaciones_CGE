## Identificación del proyecto

| Atributo | Valor verificado | Evidencia |
|---|---|---|
| Nombre | SITRA-CGE UNL — Sistema de seguimiento y trazabilidad de recomendaciones de la Contraloría General del Estado | `README.md`, `backend/config/settings.py` (`SPECTACULAR_SETTINGS.TITLE`) |
| Institución destinataria | Universidad Nacional de Loja (UNL) | `specs/001-seguimiento-recomendaciones/spec.md` |
| Tipo de sistema | Aplicación web institucional: API REST + SPA | `backend/`, `frontend/` |
| Repositorio | `https://github.com/RCL05/seguimiento_de_recomendaciones_CGE` | `git remote -v` |
| Rama auditada | `feature/sdd-spec-kit-structure` (último commit `a565ba2`, 2026-11-09) | `git log` |
| Versión de la API | `1.0.0` (contrato OpenAPI 3.0.3, prefijo `/api/v1`) | `backend/contracts/openapi.yaml` |
| Versión de paquetes | backend `0.1.0` (`pyproject.toml`), frontend `0.1.0` (`package.json`) | archivos citados |
| Metodología | Spec-Driven Development con GitHub Spec Kit | `.specify/`, `.github/agents/speckit.*`, `docs/flujo-speckit.md` |
| Fecha de auditoría | 2026-11-10 | — |

## Lenguajes

| Lenguaje | Uso | Evidencia |
|---|---|---|
| Python | Backend (Django/DRF), scripts, servidor de documentación Quart | `backend/**/*.py`, `docs_server/app.py` |
| TypeScript / TSX | Frontend React | `frontend/src/**/*.ts(x)` |
| CSS | Estilos del frontend y plantillas Django | `frontend/src/styles.css`, `backend/static/css/estilos.css` |
| HTML (plantillas Django) | Plantillas heredadas de la fase MVP | `backend/templates/**` |
| YAML | Contrato OpenAPI, Docker Compose, CI | `backend/contracts/openapi.yaml`, `docker-compose.yml`, `.github/workflows/ci.yml` |
| PowerShell | Scripts de Spec Kit | `.specify/scripts/powershell/*.ps1` |

## Frameworks, bibliotecas y versiones

Las versiones "instaladas" se obtuvieron con `pip list` sobre `.venv` y con `npm` sobre `frontend/node_modules` el 2026-11-10. Las "declaradas" son los rangos de los manifiestos.

### Backend

| Componente | Declarado | Instalado (verificado) | Función |
|---|---|---|---|
| Django | `==5.2.18` | 5.2.18 | Framework web, ORM, migraciones, admin |
| Django REST Framework | `>=3.15,<4.0` | 3.18.3 | API REST, serializers, permisos |
| drf-spectacular | `>=0.28,<1.0` | 0.30.0 | Generación del contrato OpenAPI 3.0.3 y Swagger UI |
| django-cors-headers | `>=4.4,<5.0` | 4.9.0 | CORS por lista explícita de orígenes |
| PyJWT | `>=2.10,<3.0` | 2.15.1 | Emisión y validación de JWT HS256 |
| psycopg[binary] | `>=3.2,<4.0` | 3.3.8 | Driver PostgreSQL |
| asgiref, sqlparse, tzdata | fijados | — | Dependencias de Django / zona horaria |
| pytest / pytest-django | extra `test` | 9.1.1 / 4.14.0 | Pruebas automatizadas |
| Quart + Markdown | `docs_server/requirements.txt` | 0.23.1 / 3.11.3 | Servidor de documentación Markdown (puerto 8001) |

Intérprete local verificado: Python 3.13.14. Imagen Docker y CI: Python 3.12.

### Frontend

| Componente | Declarado | Función |
|---|---|---|
| React / React DOM | `^19.0.0` | Interfaz SPA |
| TypeScript | `^5.7.2` | Tipado estático |
| Vite + `@vitejs/plugin-react` | `^6.0.0` / `^4.3.4` | Servidor de desarrollo, proxy `/api` y build |
| Vitest + Testing Library + jsdom | `^2.1.8` / `^16.3.3` / `^25.0.1` | Pruebas de componentes |
| Playwright | `^1.49.1` | Prueba end-to-end (1 escenario) |
| ESLint + typescript-eslint + Prettier | `^9.17.0` / `^8.18.2` / `^3.4.2` | Calidad estática y formato |

Node.js local verificado: v26.4.0. CI y Compose: Node 22.

## Estructura de directorios

```text
.
├── backend/                 API Django (monolito modular)
│   ├── config/              settings, urls, wsgi/asgi
│   ├── core/                api (envoltura, errores, salud), audit, auth, files, security, shared, web
│   ├── modules/             usuarios, informes_cge, recomendaciones, evidencias, notificaciones, reportes
│   ├── contracts/           openapi.yaml publicado
│   ├── scripts/             seed_initial_data.py
│   ├── templates/, static/  vistas heredadas del MVP
│   └── tests/               unit, integration, api, contract, security, concurrency
├── frontend/                SPA React + TypeScript + Vite (features por rol)
├── docs/                    documentación Markdown existente + portal Quarto (este trabajo)
├── docs_server/             servidor Quart que renderiza docs/*.md (puerto 8001)
├── specs/001-…/             especificación SDD vigente (spec, plan, tasks, data-model, contrato)
├── .spec/                   especificación SDD anterior (numeración HU/F distinta)
├── .specify/, .github/      plantillas, agentes y prompts de Spec Kit; workflow CI
├── DOCUMENTACION/           control maestro y fuentes de la documentación (este trabajo)
├── docker-compose.yml       db (PostgreSQL 16), backend, scheduler, frontend
└── feature-map.md           mapa de funcionalidades de la fase inicial
```

## Componentes y módulos del backend

| Módulo | Capas presentes | Responsabilidad | App Django registrada |
|---|---|---|---|
| `core/api` | — | Vista base, envoltura universal, catálogo de errores, middleware, `request_id`, `/health/` | No (paquete) |
| `core/audit` | modelos, repositorio, consulta | `AuditLog` inmutable y consulta de historial | Sí (`AuditConfig`) |
| `core/auth` | — | `JWTBearerAuthentication`, `IsAuthenticatedActor`, `require_roles` | No |
| `core/files` | — | Validación PDF y puertos de almacenamiento | No |
| `core/security` | — | Redacción de secretos en logs | No |
| `usuarios` | application, infrastructure, ports, presentation | Login SSO, JWT, usuarios, unidades orgánicas | Sí |
| `informes_cge` | application, presentation | Registro y consulta de informes CGE | No (modelos en `recomendaciones`) |
| `recomendaciones` | domain, application, infrastructure, presentation | Recomendaciones, máquina de estados, plan de acción, dictamen, reapertura, vencimiento | Sí |
| `evidencias` | domain, application, infrastructure, presentation | Carga, anulación, descarga e integridad de PDF | No (modelos en `recomendaciones`) |
| `notificaciones` | domain, application, infrastructure, ports, presentation, management | Alertas, mora, preferencias, configuración, comando `evaluar_plazos` | Sí |
| `reportes` | application, presentation | KPIs, tablero ejecutivo, matriz CSV, consulta de auditoría | Sí |

## Persistencia

| Elemento | Verificado |
|---|---|
| Motor de desarrollo | SQLite (`backend/development.sqlite3`, ignorado por Git) cuando `POSTGRES_DB` está vacío |
| Motor de despliegue | PostgreSQL 16 (`docker-compose.yml`), activado por `POSTGRES_DB` |
| Tablas propias | `unidades_organicas`, `usuarios`, `informes_cge`, `recomendaciones`, `planes_accion`, `evidencias`, `dictamenes_uai`, `audit_logs`, `notificaciones`, `preferencias_notificacion`, `configuracion_notificaciones` |
| Migraciones | `core/audit` (3), `usuarios` (1), `recomendaciones` (7), `notificaciones` (2) |
| Archivos | PDF en `MEDIA_ROOT/evidencias/<uuid>.pdf` e `informes/`; `backend/media/` ignorado por Git y no publicado como estático |

## APIs e integraciones

| Elemento | Verificado |
|---|---|
| API REST | 24 rutas y 31 operaciones bajo `/api/v1`, más `GET /health/` (32 operaciones en el contrato OpenAPI 3.0.3) |
| Documentación interactiva | Swagger UI en `/api/docs/`, esquema en `/api/schema/` |
| Salud | `GET /health/` (pública) |
| SSO | Introspección OAuth2 (`SSO_INTROSPECTION_URL`) o tokens de desarrollo con `DEBUG=true` |
| Correo | `django.core.mail` con backend SMTP o consola |
| Programación | Comando `manage.py evaluar_plazos` (servicio `scheduler` o cron) y `POST /api/v1/evaluaciones-plazos` |

## Infraestructura, herramientas y automatización

| Elemento | Verificado | Observación |
|---|---|---|
| Docker | `backend/Dockerfile` (python:3.12-slim), `docker-compose.yml` (4 servicios) | Docker no está instalado en el equipo auditado; no se ejecutó |
| CI | `.github/workflows/ci.yml`: `manage.py check`, pytest, lint, Vitest y build | Se dispara en `main`, `develop`, `feature/**` y PR |
| Lanzadores locales | `.claude/launch.json` (backend 8000, frontend 5173) | — |
| Documentación | Markdown en `docs/`, Swagger UI, Quart, y desde esta auditoría Quarto | — |
| Despliegue productivo | No existe configuración (sin servidor WSGI/ASGI de producción, proxy TLS ni IaC) | Documentado como pendiente |
