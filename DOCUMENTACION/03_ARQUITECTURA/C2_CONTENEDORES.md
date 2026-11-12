## Propósito del nivel

Muestra las unidades desplegables (aplicaciones y almacenes de datos) y cómo se comunican. Corresponde a los servicios de `docker-compose.yml` más los procesos de desarrollo descritos en `README.md`. Fuente editable: `DIAGRAMAS/workspace.dsl` (vista `contenedores`).

## Diagrama

```{mermaid}
flowchart LR
  user(["Usuario institucional"])
  subgraph sitra["SITRA-CGE UNL"]
    spa["SPA web<br/>[React 19 · TypeScript · Vite]<br/>:5173"]
    api["API REST<br/>[Django 5.2 · DRF · drf-spectacular]<br/>:8000 /api/v1"]
    sch["Programador de plazos<br/>[mismo código Django · manage.py evaluar_plazos]"]
    db[("Base de datos<br/>[SQLite dev · PostgreSQL 16]")]
    fs[("Almacenamiento privado de PDF<br/>[MEDIA_ROOT · volumen backend_media]")]
    docs["Servidor de documentación<br/>[Quart] :8001"]
  end
  sso[["SSO UNL"]]
  smtp[["SMTP"]]
  user -->|HTTPS| spa
  spa -->|JSON · Bearer JWT · proxy /api| api
  api -->|ORM| db
  api -->|lectura/escritura en flujo| fs
  api -->|introspección| sso
  api -->|correo| smtp
  sch -->|ORM| db
  sch -->|correo| smtp
  user -->|HTTP| docs
```

## Contenedores

| Contenedor | Tecnología | Puerto | Responsabilidad | Definición |
|---|---|---|---|---|
| SPA web | React 19, TypeScript, Vite 6 | 5173 | Interfaz por rol, sesión JWT en `sessionStorage` del navegador, cliente HTTP | `frontend/`, servicio `frontend` |
| API REST | Python 3.12 (imagen) / 3.13 (local), Django 5.2, DRF 3.18 | 8000 | Casos de uso, autorización, auditoría, Swagger UI | `backend/`, servicio `backend` |
| Programador | Misma imagen del backend | — | Bucle `evaluar_plazos` cada `SCHEDULER_INTERVAL_SECONDS` | servicio `scheduler` |
| Base de datos | PostgreSQL 16-alpine / SQLite | 5432 | Persistencia transaccional | servicio `db` |
| Archivos | Volumen `backend_media` | — | PDF de evidencias e informes | `DJANGO_MEDIA_ROOT` |
| Documentación | Quart 0.23 + Markdown | 8001 | Renderiza `docs/**/*.md` | `docs_server/app.py` (no está en Compose) |

## Decisiones de despliegue verificadas

- Compose espera a que `db` esté sano (`pg_isready`) antes de iniciar `backend`, y a que `backend` responda `/health/` antes de iniciar `frontend`.
- El contenedor `backend` aplica migraciones al arrancar y ejecuta Gunicorn sobre `config.wsgi:application`.
- El frontend en Compose ejecuta `npm ci && npm run dev`, no un build estático.
