# Plan de Implementación: Seguimiento de Recomendaciones CGE

**Rama**: `001-seguimiento-recomendaciones` | **Fecha**: 2026-10-19 |
**Especificación**: [spec.md](./spec.md)

**Entrada**: Especificación funcional de `specs/001-seguimiento-recomendaciones/spec.md`

## Resumen

Se implementará SITRA-CGE UNL como un monolito modular con arquitectura limpia en
cuatro capas: Presentación/API, Aplicación, Dominio e Infraestructura. La primera
entrega cubrirá identidad y RBAC, informes y recomendaciones, planes de acción,
evidencias PDF con SHA-256, dictámenes UAI, auditoría, alertas, tablero y matriz de
cumplimiento.

El stack elegido para el proyecto es Python 3.10 como mínimo validado y 3.12 como
objetivo de despliegue, Django REST Framework y PostgreSQL para backend, React con
TypeScript y Vite para frontend, Docker Compose para desarrollo, pytest/Vitest/
Playwright para pruebas y OpenAPI 3.1 para el contrato.
Las integraciones institucionales (SSO, SMTP y almacenamiento de archivos) se
mantendrán detrás de adaptadores configurables.

## Contexto Técnico

**Lenguaje/Versión**: Python 3.10 como mínimo compatible y Python 3.12 como runtime
objetivo; TypeScript para frontend

**Dependencias principales**: Django 5.2, Django REST Framework, Psycopg, pytest,
pytest-django, React, Vite, Vitest, React Testing Library y Playwright

**Almacenamiento**: PostgreSQL para datos transaccionales y almacenamiento de archivos
PDF separado mediante un puerto de almacenamiento; no se almacenarán binarios grandes
directamente en las tablas sin decisión aprobada

**Pruebas**: pytest para backend, Vitest y React Testing Library para frontend,
Playwright para flujos completos, además de contrato API, autorización, integridad
de archivos, concurrencia y tareas programadas

**Plataforma objetivo**: servidor Linux institucional o plataforma equivalente que
soporte el runtime aprobado, PostgreSQL, HTTPS, tareas programadas y SMTP

**Tipo de proyecto**: servicio web institucional con API REST y cliente web

**Objetivos de rendimiento**: 95% de consultas ordinarias del tablero en menos de
3 segundos y 95% de exportaciones de matriz CSV en menos de 5 segundos, medidos
con una carga de referencia de 1.000 recomendaciones, 200 usuarios y 20 consultas
concurrentes.

**Restricciones**: HTTPS, respuestas con envoltura universal, autorización en servidor,
auditoría de operaciones mutativas, PDFs validados, SHA-256, transacciones atómicas,
bloqueo de la recomendación durante cambios críticos y ausencia de secretos en Git

**Escala/Alcance**: cinco perfiles institucionales, dependencias jerárquicas,
informes CGE, recomendaciones, hitos, evidencias, dictámenes, alertas y reportes.
La carga de referencia inicial es 1.000 recomendaciones, 200 usuarios y 20
consultas concurrentes; los límites de producción se revisarán con DTI.

## Verificación de la Constitución

*GATE: aprobado antes de investigación y reevaluado después del diseño.*

- **SDD y trazabilidad**: aprobado; cada decisión, requisito, contrato y prueba se
  enlaza con la especificación y los artefactos de diseño.
- **Arquitectura limpia y SOLID**: aprobado; el dominio no depende de Django, ORM,
  PostgreSQL ni servicios externos.
- **Seguridad y mínimo privilegio**: aprobado; RBAC y autorización a nivel de objeto
  se ejecutan en cada operación.
- **Integridad y auditoría**: aprobado; las evidencias tienen hash verificable y las
  mutaciones producen auditoría protegida.
- **Concurrencia**: aprobado; las transiciones y dictámenes usan transacción y
  bloqueo de la recomendación.
- **API y errores**: aprobado; se conserva la envoltura universal y el catálogo de
  errores de la constitución.
- **Decisiones pendientes**: proveedor de SSO, almacenamiento de archivos, SMTP y
despliegue requieren aprobación explícita, registrada en ADR. El stack base queda
adoptado para el desarrollo académico.

No existen violaciones que requieran una excepción constitucional.

## Estructura del Proyecto

### Documentación de esta funcionalidad

```text
specs/001-seguimiento-recomendaciones/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
├── checklists/
│   └── requirements.md
└── tasks.md                 # Lo generará /speckit-tasks
```

### Código fuente objetivo

```text
backend/
├── config/                  # Configuración, URLs y composición de dependencias
├── core/
│   ├── api/                 # Envoltura universal y filtros de excepciones
│   ├── audit/               # Auditoría y correlación request_id
│   ├── auth/                # Puertos de identidad y autorización
│   └── shared/              # Tipos y utilidades transversales
├── modules/
│   ├── usuarios/
│   │   ├── presentation/
│   │   ├── application/
│   │   ├── domain/
│   │   └── infrastructure/
│   ├── informes_cge/
│   ├── recomendaciones/
│   ├── evidencias/
│   ├── notificaciones/
│   └── reportes/
└── tests/
    ├── unit/
    ├── integration/
    ├── contract/
    ├── security/
    └── concurrency/
```

**Decisión de estructura**: se selecciona un único backend modular. Los modelos
Django se registran en cada módulo para descubrimiento del framework; los
repositorios y adaptadores permanecen en infraestructura. Cada módulo
expone casos de uso y puertos; ningún módulo importa repositorios ORM de otro módulo.
La forma exacta de registrar módulos en Django se resolverá sin mover las fronteras
de dominio.

## Fase 0: Investigación y Decisiones

Las decisiones consolidadas se encuentran en [research.md](./research.md). En resumen:

1. Django REST Framework + PostgreSQL es la decisión adoptada por alineación con el
   prompt, el modelo relacional y las transacciones requeridas. Python 3.10 es el
   mínimo validado; Python 3.12 es el objetivo de despliegue.
2. Los detalles de SSO, SMTP, almacenamiento de PDF y despliegue se abstraen mediante
   puertos y quedan sujetos a aprobación.
3. `SELECT FOR UPDATE` se aplica a la fila de recomendación dentro de la transacción
   de transición, dictamen y ajuste de plazo.
4. SHA-256 se usa para detectar cambios de contenido; autenticidad y protección de
   registros dependen además de permisos, almacenamiento y auditoría.

## Fase 1: Diseño

### Modelo de datos

El modelo normalizado, restricciones y transiciones están en
[data-model.md](./data-model.md). Las entidades principales son Usuario, Rol,
Dependencia, Informe CGE, Recomendación, Hito, Evidencia, Dictamen, Auditoría,
Notificación y Matriz de Cumplimiento.

### Contratos

El contrato OpenAPI 3.1 está en [contracts/openapi.yaml](./contracts/openapi.yaml).
Define el prefijo `/api/v1/`, la envoltura universal, códigos de error, autorización,
operaciones principales, paginación, carga PDF y exportación de matriz CSV UTF-8.

### Validación operativa

Los escenarios ejecutables y prerrequisitos están en [quickstart.md](./quickstart.md).
Incluyen creación de recomendación, bloqueo del salto a `Cumplida`, defensa BOLA,
integridad PDF, auditoría, alertas y concurrencia.

## Decisiones de Arquitectura

### ADR-001: Monolito modular con cuatro capas

- **Estado**: Propuesto.
- **Contexto**: el sistema necesita evolucionar con límites institucionales claros y
  sin distribuir prematuramente operaciones transaccionales.
- **Decisión**: separar Presentación/API, Aplicación, Dominio e Infraestructura dentro
  de un único despliegue modular.
- **Consecuencias**: simplifica transacciones y despliegue; exige disciplina de
  dependencias y pruebas de límites entre módulos.

### ADR-002: SHA-256 para verificación de integridad

- **Estado**: Aprobado por la constitución, pendiente de controles operativos.
- **Contexto**: las evidencias PDF deben permitir detectar modificaciones.
- **Decisión**: calcular SHA-256 al cargar y conservarlo junto con metadatos y auditoría.
- **Consecuencias**: permite verificación reproducible; no prueba autenticidad por sí
  solo ni protege contra alteraciones administrativas de la base de datos.

### ADR-003: Bloqueo pesimista en cambios críticos

- **Estado**: Propuesto.
- **Contexto**: dos solicitudes simultáneas pueden producir estados contradictorios.
- **Decisión**: ejecutar transacciones atómicas y bloquear la recomendación con
  `SELECT ... FOR UPDATE` durante transición, dictamen y ajuste de plazo.
- **Consecuencias**: evita actualizaciones perdidas; requiere límites de tiempo,
  reintentos controlados y pruebas de contención.

### ADR-004: Envoltura universal y errores estandarizados

- **Estado**: Aprobado por la especificación.
- **Contexto**: clientes y auditoría necesitan respuestas previsibles y correlación.
- **Decisión**: todas las respuestas JSON usan `success`, `message`, `data`, `errors`
  y `meta`; los fallos se clasifican mediante el catálogo institucional y se
  correlacionan con `request_id`.
- **Consecuencias**: facilita clientes y observabilidad; las excepciones `204`, `304`
  y `HEAD` deben documentarse explícitamente.

## Matriz de Trazabilidad de Diseño

| Requisito | Componente | Entidad / datos | Endpoint o contrato | Prueba automatizada |
| --- | --- | --- | --- | --- |
| RF-001 | `modules/usuarios/application/login_sso.py`, `infrastructure/sso_adapter.py`, `core/api/views.py::login_sso` | `Usuario`, sesión | `POST /api/v1/auth/login-sso` | `tests/api/test_http_api.py::test_login_sso_devuelve_identidad_y_rol` |
| RF-002 | `modules/usuarios/application/manage_roles.py`, `core/auth/authorization.py` | `Usuario.rol`, `UnidadOrganica` | RBAC de cabeceras/servidor | `tests/unit/usuarios/test_identity_rules.py`, `tests/integration/usuarios/test_admin_flow.py` |
| RF-003 | `modules/usuarios/application/manage_units.py` | historial de reasignación | servicio interno; sin endpoint publicado (brecha T128) | `tests/unit/usuarios/test_identity_rules.py::test_reasignacion_sin_perder_historial` |
| RF-004 | `modules/notificaciones/application/manage_notification_settings.py`, `send_deadline_alerts.py` | `ConfiguracionNotificacion`, `Notificacion` | `GET/PUT /api/v1/notificaciones/configuracion` | `tests/unit/notificaciones/test_settings_rules.py`, `tests/integration/notificaciones/test_settings_flow.py` |
| RF-005 | `modules/informes_cge/application/register_informe.py` | `InformeCGE` | `POST /api/v1/informes` | `tests/integration/recomendaciones/test_registration.py`, `tests/integration/test_quickstart.py` |
| RF-006 | `modules/recomendaciones/application/create_recomendacion.py` | `Recomendacion` | `POST /api/v1/recomendaciones` | `tests/integration/recomendaciones/test_registration.py`, `tests/unit/recomendaciones/test_creation_rules.py` |
| RF-007 | `modules/recomendaciones/application/create_plan_accion.py` | `PlanAccion` | `POST /api/v1/recomendaciones/{id}/plan-accion` | `tests/api/test_http_api.py::test_report_and_plan_routes_are_available`, `tests/integration/evidencias/test_upload_flow.py` |
| RF-008 | `modules/recomendaciones/application/upload_evidencia.py`, `core/files/pdf_integrity.py` | `Evidencia.hash_sha256` | `POST /api/v1/recomendaciones/{id}/evidencias` | `tests/unit/evidencias/test_upload_rules.py`, `tests/integration/evidencias/test_upload_flow.py` |
| RF-009 | `modules/recomendaciones/application/issue_dictamen.py`, máquina de estados | `Recomendacion.estado` | `POST /api/v1/recomendaciones/{id}/dictamen` | `tests/integration/evidencias/test_dictamen_flow.py`, `tests/unit/test_mvp.py` |
| RF-010 | `modules/evidencias/application/reject_evidence.py`, `issue_dictamen.py` | `DictamenUAI`, revisiones | `POST /api/v1/recomendaciones/{id}/dictamen` | `tests/integration/test_quickstart.py::test_rechazo_conserva_evidencia_y_permite_corregir` |
| RF-011, RF-021 | `modules/notificaciones/application/send_deadline_alerts.py`, `service.py` | `Notificacion`, clave idempotente | `POST /api/v1/jobs/evaluar-plazos` | `tests/unit/notificaciones/test_deadlines.py`, `tests/integration/notificaciones/test_settings_flow.py` |
| RF-012 | `modules/notificaciones/application/mark_overdue.py` | `Recomendacion.estado=EN_MORA` | tarea de plazos / tablero | `tests/integration/notificaciones/test_scheduled_flows.py` |
| RF-013 | `modules/reportes/views.py::dashboard_summary` | agregados por unidad/estado | `GET /api/v1/reportes/tablero` | `tests/integration/reportes/test_report_performance.py`, `frontend/src/features/dashboard/pages/ExecutiveDashboardPage.tsx` |
| RF-014, RF-018 | `modules/reportes/views.py::export_matriz_cge`, `audit_log_list` | matriz CSV, `AuditLog` | `GET /api/v1/reportes/matriz-cge`, `GET /api/v1/auditoria` | `tests/integration/test_quickstart.py::test_matriz_csv_restingida_por_rol`, `tests/security/test_audit_and_reports.py` |
| RF-015, RF-016, RNF-004 | `core/api/response_envelope.py`, `error_catalog.py`, `exception_handler.py` | `request_id`, catálogo de errores | todos los endpoints JSON | `tests/integration/test_foundation.py`, `tests/contract/test_api_contract.py` |
| RF-017, RNF-002 | `core/audit/models.py`, `repository.py`, `modules/*/application/audit_events.py` | `AuditLog` inmutable | inserción en cada mutación | `tests/integration/test_quickstart.py::test_flujo_principal_aprobacion_y_cadena_de_auditoria`, `tests/security/test_audit_and_reports.py` |
| RF-019, RNF-003 | `core/auth/authorization.py`, `core/api/views.py` | unidad del recurso | consulta, plan, evidencia y dictamen | `tests/security/test_evidence_object_authorization.py`, `tests/integration/test_quickstart.py::test_bola_entre_unidades_responde_404_y_audita_el_intento` |
| RF-020 | `transaction.atomic` + `select_for_update` en casos de uso | `Recomendacion`, `Evidencia` | cargas y dictamen | `tests/concurrency/test_recommendation_locking.py` |
| RF-022 | `contracts/openapi.yaml`, vistas publicadas | contrato 14 paths / 23 schemas | OpenAPI 3.1.0 | `tests/contract/test_api_contract.py` (cobertura parcial de esquema) |
| RNF-001 | `modules/evidencias/application/verify_integrity.py` | SHA-256 almacenado vs recalculado | verificación de integridad | `tests/integration/evidencias/test_integrity_flow.py` |
| RNF-005, RNF-006 | `modules/reportes/views.py` | consultas de tablero y exportación | tablero y matriz CSV | solo umbrales declarados; falta benchmark con carga de referencia (T139) |
| RNF-007 | `modules/notificaciones/infrastructure/smtp_adapter.py` | `Notificacion` y reintentos | jobs internos | `tests/integration/notificaciones/test_scheduled_flows.py` (cobertura mínima) |
| RNF-008 | `core/security/log_safety.py`, `manage_notification_settings.py` | logs y auditoría redactados | respuestas y registros | `tests/security/test_secret_and_log_safety.py` |
| RNF-009 | artefactos Spec Kit | requisitos EARS y escenarios BDD | `spec.md`, `plan.md`, `tasks.md` | revisión de trazabilidad (esta matriz); sin verificador automático |

## Seguimiento de la Implementación

`/speckit-tasks` debe convertir este plan en tareas ordenadas por dependencia. Las
tareas deben preservar las fronteras de módulos, generar pruebas antes de cerrar cada
caso de uso y enlazar RF/RNF con código, prueba y documentación.

## Complejidad

No se registran violaciones constitucionales. El patrón de repositorios, puertos,
adaptadores y bloqueo pesimista se justifica por los requisitos explícitos de
independencia del dominio, auditoría y consistencia concurrente.
