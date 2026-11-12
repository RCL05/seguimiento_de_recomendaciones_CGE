## Pila tecnológica

Las versiones se verificaron el 2026-11-10 sobre el entorno local (`.venv`, `frontend/node_modules`). El detalle completo de versiones declaradas e instaladas está en *Auditoría → Inventario técnico*.

| Capa | Tecnología | Versión verificada | Función en el proyecto | Dónde se usa |
|---|---|---|---|---|
| Lenguaje backend | Python | 3.13.14 local · 3.12 en Docker y CI | Backend, scripts, servidor de docs | `backend/`, `docs_server/` |
| Framework web | Django | 5.2.18 | ORM, migraciones, enrutamiento, middleware, admin | `backend/config`, modelos |
| API | Django REST Framework | 3.18.3 | Vistas `APIView`, serializers, autenticación y permisos pluggables, manejo de excepciones | `core/api/base.py`, `*/presentation` |
| Contrato | drf-spectacular | 0.30.0 | OpenAPI 3.0.3 desde el código, Swagger UI | `config/settings.py::SPECTACULAR_SETTINGS`, `core/api/schema.py` |
| Seguridad | PyJWT | 2.15.1 | JWT HS256 con `iss`, `aud`, `exp` | `usuarios/infrastructure/sso_adapter.py` |
| CORS | django-cors-headers | 4.9.0 | Orígenes explícitos, cabeceras permitidas y expuestas | `config/settings.py` |
| Base de datos | SQLite / PostgreSQL | SQLite integrado · PostgreSQL 16-alpine | Persistencia | `DATABASES` |
| Driver | psycopg[binary] | 3.3.8 | Conexión PostgreSQL | — |
| Pruebas backend | pytest + pytest-django | 9.1.1 / 4.14.0 | 231 pruebas | `backend/tests/` |
| Lenguaje frontend | TypeScript | ^5.7.2 | Tipado del cliente y componentes | `frontend/src/` |
| UI | React / React DOM | ^19.0.0 | SPA por rol | `frontend/src/` |
| Build | Vite + plugin React | ^6.0.0 | Dev server, proxy `/api`, build de producción | `frontend/vite.config.ts` |
| Pruebas frontend | Vitest, Testing Library, jsdom | ^2.1.8 / ^16.3.3 / ^25.0.1 | 12 pruebas de componentes | `frontend/src/**/*.test.tsx` |
| E2E | Playwright | ^1.49.1 | 1 recorrido por roles con API simulada | `frontend/tests/e2e/` |
| Calidad estática | ESLint 9, typescript-eslint, Prettier | ^9.17 / ^8.18 / ^3.4 | Lint y formato | `frontend/eslint.config.js` |
| Documentación | Quart + Markdown | 0.23.1 / 3.11.3 | Servidor Markdown :8001 | `docs_server/app.py` |
| Documentación | Quarto | 1.11.9 (usado en esta auditoría) | Portal técnico publicado en GitHub Pages | `docs/_quarto.yml` |
| Contenedores | Docker, Docker Compose | No verificado (no instalado en el equipo auditado) | Entorno reproducible | `backend/Dockerfile`, `docker-compose.yml` |
| CI | GitHub Actions | — | Integración continua y publicación del portal | `.github/workflows/` |
| Metodología | GitHub Spec Kit | — | Flujo SDD (specify → plan → tasks → implement) | `.specify/`, `.github/agents/` |

## Tecnologías declaradas pero no utilizadas

| Tecnología | Dónde se menciona | Situación |
|---|---|---|
| Almacenamiento S3 compatible | `.env.example`, `docs/operations/configuration.md` | Sin implementación (H-04) |
| OpenAPI 3.1 | `specs/…/plan.md` | El contrato real es 3.0.3 |
| OIDC/LDAP | `docs/architecture/sitra-cge.md` | Solo introspección OAuth2 genérica |
| Antimalware | `docs/operations/configuration.md` | Sin implementación (H-03) |
