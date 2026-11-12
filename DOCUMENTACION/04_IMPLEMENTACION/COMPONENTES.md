## Componentes transversales (`backend/core`)

| Componente | Propósito | Procesamiento clave | Archivos |
|---|---|---|---|
| Vista base | Unificar la forma de todas las vistas | `ApiView` expone `actor`, `request_id`, `client_ip`; `ok()` construye la envoltura con `meta.pagination` opcional | `core/api/base.py`, `response_envelope.py` |
| Errores | Traducir excepciones a la envoltura sin filtrar detalles | `handle_exception` mapea `DomainError` y excepciones DRF a `{code, detail}`; `ApiErrorEnvelopeMiddleware` cubre 404/405/500 fuera de DRF | `exception_handler.py`, `middleware.py`, `error_catalog.py` |
| Correlación | Identificar cada petición | Usa `X-Request-ID` si es UUID válido; si no, genera UUID v4 | `request_context.py` |
| Salud | Comprobación de disponibilidad | `GET /health/` sin autenticación → `{"status": "ok"}` | `health.py` |
| Autenticación | Resolver el actor | Valida JWT y exige que rol y unidad del token coincidan con la cuenta activa | `core/auth/authentication.py` |
| Permisos | RBAC declarativo | `IsAuthenticatedActor`, `require_roles(*roles)` | `core/auth/permissions.py` |
| Auditoría | Bitácora inmutable | `record_audit(...)` inserta `AuditLog` en la transacción en curso | `core/audit/repository.py`, `models.py` |
| Seguridad de logs | Evitar fuga de secretos | `redact_sensitive` reemplaza valores de claves sensibles por `[REDACTED]` | `core/security/log_safety.py` |
| Tipos de dominio | Vocabulario común | `Role`, `RecommendationState`, jerarquía `DomainError` con `code` y `status_code` | `core/shared/domain_types.py` |

## Módulos de negocio

### usuarios

| Aspecto | Detalle |
|---|---|
| Propósito | Identidad, sesión y estructura orgánica |
| Entradas | Credencial SSO; datos de unidad; cambios de rol/unidad/estado de usuario |
| Procesamiento | `IniciarSesionSso` → `SsoAdapter.authenticate` (tokens de desarrollo o introspección) → persistencia de identidad → `issue_session` (JWT 1 h) → auditoría. `manage_roles.py` y `manage_units.py` aplican cambios solo para DTI |
| Salidas | Sesión `{access_token, token_type, expires_in, user_id, email, display_name, role, unit_id}`; catálogos |
| Reglas | Solo DTI administra; roles válidos limitados a `Usuario.Rol`; un token deja de valer si cambia el rol o la unidad |
| Persistencia | `usuarios`, `unidades_organicas` |
| Integraciones | SSO UNL (`SSO_INTROSPECTION_URL`, `SSO_CLIENT_ID`, `SSO_CLIENT_SECRET`) |

### informes_cge

| Aspecto | Detalle |
|---|---|
| Propósito | Registrar los informes de examen especial |
| Entradas | `multipart/form-data` o JSON con número, período, fecha de notificación, PDF opcional o URL |
| Procesamiento | Valida rol UAI, tamaño ≤ `MAX_PDF_SIZE_BYTES`, unicidad; guarda; audita. Consulta paginada para UAI, RECTORADO y CGE_AUDITOR |
| Salidas | Informe (201 con cabecera `Location`), listado, documento PDF por endpoint autenticado |
| Persistencia | `informes_cge` (modelo en `recomendaciones/models.py`), archivo en `MEDIA_ROOT/informes/` |

### recomendaciones

| Aspecto | Detalle |
|---|---|
| Propósito | Núcleo del flujo de cumplimiento |
| Entradas | Recomendación (informe, número, descripción, unidad, `legal_days`, `due_date`, prioridad); hito; dictamen; reapertura con motivo; filtros de listado (`state`, `unit_id`, `priority`, `due_*`, `vencida`, paginación) |
| Procesamiento | Casos de uso transaccionales con `select_for_update`; `transition_state` valida la transición; `anotar_vencimiento` calcula el indicador `vencida` en la consulta |
| Salidas | Recomendación con `state`, `vencida`, `overdue_registered_at`; detalle con evidencias; hitos; dictamen |
| Reglas | RN-01…RN-07 (ver *Requisitos*) |
| Persistencia | `recomendaciones`, `planes_accion`, `dictamenes_uai`, `evidencias` |
| Archivos | `domain/state_machine.py`, `domain/vencimiento.py`, `application/*.py`, `infrastructure/repositories.py`, `infrastructure/storage.py` |

### evidencias

| Aspecto | Detalle |
|---|---|
| Propósito | Gestión segura de los PDF de evidencia |
| Entradas | Cuerpo binario (`application/pdf`) con cabeceras `X-Filename` y `X-Evidence-Type`; identificador de evidencia |
| Procesamiento | Carga en flujo por bloques de 64 KiB: suma SHA-256 y tamaño mientras escribe; aborta y borra si supera el máximo o la firma no es `%PDF-`. Anulación lógica (UAI). Descarga solo para UAI o ejecutor de la misma unidad (evidencias anuladas solo UAI). Integridad: recalcula SHA-256 y compara (UAI, CGE_AUDITOR) |
| Salidas | Evidencia con `sha256`, `size_bytes`, `type`, `status`; flujo PDF; resultado de integridad |
| Persistencia | `evidencias`; archivo `MEDIA_ROOT/evidencias/<uuid>.pdf` |

### notificaciones

| Aspecto | Detalle |
|---|---|
| Propósito | Alertas de plazo y vencimiento por canal interno y correo |
| Entradas | Configuración institucional (DTI), preferencias por usuario, ejecución del programador |
| Procesamiento | `send_deadline_alerts` (≤ `umbral_dias` sin evidencia presentada), `mark_overdue_recommendations` (una vez por ciclo), `schedule_notification` con clave de idempotencia, `deliver_pending_notifications` vía `django.core.mail` |
| Salidas | Bandeja del usuario (últimas 100), resumen JSON del job |
| Reglas | Canal efectivo = configuración global ∧ preferencia del usuario; la configuración rechaza claves con aspecto de secreto |
| Persistencia | `notificaciones`, `preferencias_notificacion`, `configuracion_notificaciones` (singleton `pk=1`) |
| Integraciones | SMTP (`EMAIL_*`); en desarrollo sin `EMAIL_HOST`, backend de consola |

### reportes

| Aspecto | Detalle |
|---|---|
| Propósito | Información agregada para decisión y auditoría |
| Procesamiento | `get_kpis` (sin restricción de rol; EJECUTOR limitado a su unidad, H-14 parcial), `get_dashboard` (semáforo 75/40 %, unidades en mora), `export_matriz_cge_csv` (10 columnas, BOM UTF-8), `query_audit_log` (filtros y límite) |
| Roles | Tablero y matriz: UAI, RECTORADO, CGE_AUDITOR. Auditoría: UAI, CGE_AUDITOR |
| Persistencia | Solo lectura |

## Frontend

| Componente | Propósito | Integración |
|---|---|---|
| `api/client.ts` | Tipos de dominio, sesión en `sessionStorage`, `fetch` con `Authorization: Bearer`, `ApiError` con código y estado | Todas las operaciones de la API |
| `App.tsx` + `routes.tsx` | Inicio de sesión con token SSO, menú lateral filtrado por rol, página de entrada por rol | `routes[].roles` coincide con los permisos del backend |
| Páginas por rol | Formularios con `FormStepper`, carga de PDF, revisión con dictamen, tablero, auditoría y matriz, administración | Endpoints de cada módulo |
