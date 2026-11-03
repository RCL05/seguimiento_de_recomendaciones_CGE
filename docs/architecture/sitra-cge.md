# Arquitectura SITRA-CGE UNL

Documento de arquitectura C4 (contexto, contenedores y componentes) y límites
modulares del sistema de seguimiento de recomendaciones de la Contraloría
General del Estado para la Universidad Nacional de Loja.

## 1. Contexto (C4 nivel 1)

```text
┌──────────────┐        ┌──────────────────────┐        ┌────────────────────┐
│ UAI          │        │                      │        │ SSO institucional  │
│ Ejecutores   │───────▶│   SITRA-CGE UNL      │◀──────▶│ (LDAP/OIDC UNL)    │
│ Rectorado    │        │                      │        └────────────────────┘
│ DTI          │        │                      │        ┌────────────────────┐
│ Auditor CGE  │        │                      │◀──────▶│ SMTP institucional │
└──────────────┘        └──────────┬───────────┘        └────────────────────┘
                                   │                    ┌────────────────────┐
                                   └───────────────────▶│ Almacenamiento PDF │
                                                        └────────────────────┘
```

Actores y responsabilidades:

| Actor | Necesidad principal |
| --- | --- |
| UAI | Registrar informes/recomendaciones, revisar evidencias y consultar auditoría. |
| Ejecutor de unidad | Planificar hitos, cargar evidencias PDF y corregir rechazos. |
| Rectorado | Supervisar cumplimiento, mora y semáforo institucional. |
| DTI | Administrar identidad, notificaciones, almacenamiento y operación. |
| Auditor CGE | Consultar matriz, historial y evidencia sin modificar el flujo. |

## 2. Contenedores (C4 nivel 2)

| Contenedor | Tecnología | Responsabilidad |
| --- | --- | --- |
| `frontend/` | React 19 + TypeScript + Vite | Vistas por rol, cliente HTTP tipado, formularios y tablero. |
| `backend/` | Django 5.2 + Python 3.13 | API REST, reglas de dominio, persistencia y auditoría. |
| Base de datos | SQLite en desarrollo / PostgreSQL en producción | Informes, recomendaciones, evidencias, auditoría, notificaciones. |
| Almacenamiento de evidencias | Sistema de archivos o S3 compatible | PDFs con hash SHA-256 y control de autorización. |
| Jobs | Comando/endpoint interno | Evaluación de plazos, mora y entrega de alertas. |

Flujo de petición:

1. El frontend envía `X-User-ID`, `X-Role` y opcionalmente `X-Unit-ID`.
2. `backend/core/api` valida identidad, construye el sobre de respuesta y aplica
   el catálogo de errores.
3. La capa `application` de cada módulo ejecuta el caso de uso y registra
   auditoría dentro de la misma transacción.
4. La capa `infrastructure` persiste el estado y adapta servicios externos
   (SSO, SMTP, almacenamiento).
5. La respuesta incluye `meta.request_id` para correlación con logs y auditoría.

## 3. Componentes (C4 nivel 3)

```text
backend/
├── core/
│   ├── api/              # vistas HTTP, sobre de respuesta, errores, request id
│   ├── audit/            # AuditLog y consulta de historial
│   ├── security/         # autorización por rol/unidad y sanitización
│   └── shared/           # DomainError, Role, User, utilidades
├── modules/
│   ├── informes_cge/     # registro de informes
│   ├── recomendaciones/  # creación, plan, evidencias, dictamen
│   ├── evidencias/       # validación PDF y almacenamiento
│   ├── notificaciones/   # alertas, preferencias, configuración y jobs
│   ├── reportes/         # tablero y matriz CSV
│   └── usuarios/         # identidad, unidades y administración
└── config/               # settings, URLs, WSGI/ASGI
```

### Límites modulares

| Módulo | Puede depender de | No debe depender de |
| --- | --- | --- |
| `core` | Solo biblioteca estándar y Django | Módulos de negocio |
| `usuarios` | `core` | `recomendaciones`, `evidencias`, `notificaciones` |
| `informes_cge` | `core`, `usuarios` | `evidencias`, `notificaciones` |
| `recomendaciones` | `core`, `usuarios`, `informes_cge`, `evidencias` | `reportes`, `notificaciones` |
| `evidencias` | `core`, `recomendaciones` (solo IDs) | `notificaciones`, `reportes` |
| `notificaciones` | `core`, `usuarios`, `recomendaciones` (lectura) | `reportes` |
| `reportes` | `core`, `recomendaciones`, `usuarios` | `notificaciones` |

Reglas de cumplimiento:

- Las capas `application` no importan vistas ni modelos de otros módulos; usan
  casos de uso o puertos.
- Las vistas delegan la decisión de permisos en `core.security` o en el caso de
  uso, no en el template.
- La auditoría se escribe con `record_audit` dentro de la transacción del caso
  de uso.
- Los jobs de notificaciones son idempotentes por `(destinatario, tipo,
  recomendación, ventana)`.

### Deuda técnica conocida

- Conviven `backend/core/api/views.py` (API activa) y
  `backend/modules/*/presentation/views.py` (implementaciones parciales). La
  ruta canónica es `backend/config/urls.py`.
- `login_sso` espera un objeto con `.subject`, pero `SsoAdapter` devuelve un
  diccionario; debe unificarse antes de producción.
- Algunos tests heredados (`tests/api/test_http_api.py`,
  `tests/integration/test_foundation.py`) apuntan a la API anterior y deben
  actualizarse.

## 4. Persistencia y transacciones

- `InformeCGE` 1—N `Recomendacion`; `Recomendacion` 1—N `Evidencia`,
  `HitoPlanAccion` y `Notificacion`.
- `Recomendacion` usa bloqueo optimista (`version`) para evitar dictámenes
  concurrentes; el conflicto responde `409 CONFLICT`.
- `AuditLog` es append-only y guarda `request_id`, actor, entidad, estados,
  resultado, IP y timestamp UTC.
- `Evidencia` guarda `hash_sha256`, `tamano_bytes`, `mime_type`, `validada` y
  ruta de almacenamiento; nunca se sirve sin autorización de rol/unidad.
- `PreferenciaNotificacion` es única por `(usuario, tipo_alerta)`;
  `ConfiguracionNotificacion` es singleton (`pk=1`).

## 5. Seguridad

- Autorización por rol: UAI registra y dictamina; EJECUTOR planifica y carga;
  RECTORADO/UAI/CGE consultan tablero; DTI administra configuración y jobs.
- Aislamiento por unidad: el ejecutor solo ve recomendaciones de su
  `X-Unit-ID`; el acceso indebido responde `404` y genera `ACCESS_DENIED`.
- Validación de evidencia: MIME PDF, extensión, firma `%PDF`, tamaño máximo
  30 MB, SHA-256 y análisis antimalware.
- Secretos solo por variables de entorno; la configuración de notificaciones
  rechaza claves que contengan `smtp`, `password`, `token`, `secret` o
  `credential`.
- Logs sin credenciales, tokens ni contenido de PDF; solo IDs, hashes y
  resultados.

## 6. Decisiones relacionadas

- `docs/adr/ADR-0001-arquitectura-capas.md`
- `docs/adr/ADR-0002-autenticacion-jwt-sso.md`
- `docs/adr/ADR-0004-control-concurrencia.md`
- `docs/adr/ADR-0005-almacenamiento-evidencias.md`
- `docs/adr/ADR-0006-historial-auditoria.md`
- `docs/adr/ADR-0011-evidencias-pdf-supabase.md`
