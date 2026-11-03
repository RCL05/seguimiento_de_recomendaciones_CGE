# Tareas de Implementación: Seguimiento de Recomendaciones CGE

**Entrada**: Diseño en `specs/001-seguimiento-recomendaciones/`

**Documentos de referencia**:

- [spec.md](./spec.md)
- [plan.md](./plan.md)
- [data-model.md](./data-model.md)
- [research.md](./research.md)
- [contracts/openapi.yaml](./contracts/openapi.yaml)
- [quickstart.md](./quickstart.md)

## Estrategia de implementación

Se implementará primero un MVP con el registro y asignación de recomendaciones
(US1), después el plan y las evidencias (US2), y finalmente la revisión UAI (US3).
Las historias de supervisión, auditoría y administración se incorporarán de forma
incremental. Cada fase debe conservar las fronteras de Clean Architecture, cubrir
sus escenarios de aceptación y mantener trazabilidad RF/RNF -> código -> prueba.

## Dependencias entre historias

```text
Setup -> Fundamentos
Fundamentos -> US1
US1 -> US2
US2 -> US3
US1 -> US4
US1 -> US5
Fundamentos -> US6
US3 -> US5
US2 -> US4
Todas las historias -> Pulido transversal
```

US4 y US6 pueden comenzar en paralelo después de Fundamentos y US1 cuando solo
consuman contratos y entidades ya estabilizados. US5 requiere el modelo de auditoría
y los eventos producidos por US1-US3.

## Fase 1: Preparación

**Objetivo**: Crear el esqueleto del servicio, configuración segura y herramientas.

- [X] T001 Crear el proyecto backend modular y sus paquetes en `backend/config/`, `backend/core/` y `backend/modules/`.
- [X] T002 [P] Crear la configuración de dependencias y versiones aprobadas en `backend/pyproject.toml`.
- [X] T003 [P] Crear variables de entorno de ejemplo sin secretos en `backend/.env.example`.
- [X] T004 [P] Configurar exclusión de secretos, archivos temporales y entornos locales en `.gitignore`.
- [X] T005 [P] Configurar lint, formato, tipado y ejecución de pruebas en `backend/pyproject.toml`.
- [X] T006 [P] Configurar la aplicación web, rutas base y health check en `backend/config/settings.py`.
- [X] T007 [P] Configurar el registro de módulos, URLs y comprobaciones de configuración en `backend/config/urls.py`.

## Fase 2: Fundamentos compartidos

**Objetivo**: Implementar las capacidades bloqueantes para todas las historias.

- [X] T008 Crear tipos de identificador, errores de dominio y resultados de casos de uso en `backend/core/shared/domain_types.py`.
- [X] T009 [P] Crear el puerto de unidad de trabajo y transacción en `backend/core/shared/unit_of_work.py`.
- [X] T010 [P] Crear generación y propagación de `request_id` UUID v4 en `backend/core/api/request_context.py`.
- [X] T011 [P] Implementar la envoltura universal `success`, `message`, `data`, `errors` y `meta` en `backend/core/api/response_envelope.py`.
- [X] T012 [P] Implementar el catálogo `VALIDATION_ERROR`, `AUTHENTICATION_REQUIRED`, `PERMISSION_DENIED`, `RESOURCE_NOT_FOUND`, `BUSINESS_RULE_VIOLATION`, `CONFLICT` e `INTERNAL_ERROR` en `backend/core/api/error_catalog.py`.
- [X] T013 Implementar el manejador global de excepciones y respuestas RFC 9457 sin trazas ni SQL en `backend/core/api/exception_handler.py`.
- [X] T014 [P] Crear puertos de autenticación, autorización RBAC y autorización a nivel de objeto en `backend/core/auth/ports.py`.
- [X] T015 [P] Crear tipos de roles `DTI`, `UAI`, `EJECUTOR`, `RECTORADO` y `CGE_AUDITOR` en `backend/core/shared/domain_types.py`.
- [X] T016 [P] Crear el puerto de almacenamiento de archivos PDF y su contrato de verificación en `backend/core/files/storage_ports.py`.
- [X] T017 [P] Crear el servicio SHA-256 y validadores MIME, extensión, tamaño y contenido en `backend/core/files/pdf_integrity.py`.
- [X] T018 [P] Crear el puerto de auditoría y el esquema de evento con `usuario_id`, timestamp UTC, IP, `request_id`, entidad, estados y resultado en `backend/core/audit/ports.py`.
- [X] T019 Implementar migración base y modelos de unidades y usuarios con UUID, correo institucional único, rol, dependencia y `activo` en `backend/modules/usuarios/models.py`.
- [X] T020 Implementar el repositorio transaccional y consultas de unidades y usuarios en `backend/modules/usuarios/infrastructure/repositories.py`.
- [X] T021 [P] Crear pruebas unitarias de envoltura, catálogo de errores, UUID, validación PDF y SHA-256 en `backend/tests/unit/test_mvp.py`.
- [ ] T022 [P] Crear pruebas de integración de transacción, auditoría mínima y autorización de objeto en `backend/tests/integration/test_foundation.py`.

## Fase 3: Historia de Usuario 1 - Registrar y asignar recomendaciones (P1)

**Objetivo**: Registrar informes CGE, recomendaciones, responsables, plazos y estado
inicial. **Prueba independiente**: crear un informe y una recomendación completa,
consultar `Pendiente` y rechazar datos incompletos.

- [X] T023 [P] [US1] Crear modelos y migraciones de `InformeCGE` y `Recomendacion`, incluyendo `UNIQUE (informe_id, numero_recomendacion)`, `plazo_legal_dias > 0`, prioridad, responsable y estado inicial `PENDIENTE` en `backend/modules/recomendaciones/models.py`.
- [X] T024 [P] [US1] Crear entidades y reglas de creación de informe y recomendación en `backend/core/shared/domain_types.py`.
- [X] T025 [P] [US1] Crear repositorios de informes y recomendaciones con consultas por dependencia en `backend/modules/recomendaciones/infrastructure/repositories.py`.
- [X] T026 [US1] Implementar caso de uso para registrar informe con número único, período, fecha de notificación y documento oficial en `backend/modules/informes_cge/application/register_informe.py`.
- [X] T027 [US1] Implementar caso de uso para crear recomendación con plazo, prioridad, unidad responsable y estado `PENDIENTE` en `backend/modules/recomendaciones/application/service.py`.
- [X] T028 [US1] Implementar el endpoint `POST /api/v1/informes` en `backend/modules/informes_cge/presentation/views.py` y `POST /api/v1/recomendaciones` en `backend/modules/recomendaciones/presentation/views.py`, con DTOs, autorización UAI y envoltura universal.
- [X] T029 [US1] Implementar validación de duplicados, campos obligatorios y mensajes `VALIDATION_ERROR` en `backend/modules/informes_cge/presentation/serializers.py` y `backend/modules/recomendaciones/presentation/serializers.py`.
- [ ] T030 [US1] Registrar auditoría de creación de informes y recomendaciones con usuario, entidad, estado y `request_id` en `backend/modules/recomendaciones/application/audit_events.py`.
- [ ] T031 [US1] Crear pruebas unitarias de reglas de creación y cálculo de vencimiento en `backend/tests/unit/recomendaciones/test_creation_rules.py`.
- [ ] T032 [US1] Crear pruebas de integración de registro, asignación, duplicados y estado inicial en `backend/tests/integration/recomendaciones/test_registration.py`.

## Fase 4: Historia de Usuario 2 - Gestionar plan de acción y evidencias (P1)

**Objetivo**: Crear hitos y cargar evidencias PDF integras para llevar una
recomendación a revisión interna. **Prueba independiente**: crear hitos válidos,
cargar PDF, obtener SHA-256 y confirmar `EN_REVISION_INTERNA`.

- [X] T033 [P] [US2] Crear modelo y migración `PlanAccion` con recomendación, descripción de hito, fecha de compromiso, `completado` y creador en `backend/modules/recomendaciones/models.py`.
- [ ] T034 [P] [US2] Crear entidad de hito y reglas de fechas que no excedan `fecha_vencimiento_legal` en `backend/modules/recomendaciones/domain/plan_accion.py`.
- [ ] T035 [US2] Implementar caso de uso de creación de plan que valide estado `EN_PLANIFICACION` y fechas en `backend/modules/recomendaciones/application/create_plan_accion.py`.
- [X] T036 [P] [US2] Crear modelo y migración `Evidencia` con `mime_type = application/pdf`, `hash_sha256` de 64 caracteres hexadecimales, tamaño positivo, almacenamiento, creador e inmutabilidad en `backend/modules/recomendaciones/models.py`.
- [X] T037 [US2] Implementar caso de uso de carga que valide dependencia del ejecutor, PDF, tamaño, contenido, hash y transición a `EN_REVISION_INTERNA` en `backend/modules/recomendaciones/application/service.py`.
- [ ] T038 [US2] Implementar adaptador de almacenamiento de pruebas y producción detrás del puerto definido en `backend/modules/evidencias/infrastructure/storage_adapter.py`.
- [X] T039 [US2] Implementar el endpoint `POST /api/v1/recomendaciones/{id}/plan-accion` en `backend/modules/recomendaciones/presentation/views.py` y `POST /api/v1/recomendaciones/{id}/evidencias` en `backend/modules/evidencias/presentation/views.py`.
- [ ] T040 [US2] Registrar auditoría de plan, carga de evidencia, hash y transición en `backend/modules/evidencias/application/audit_events.py`.
- [ ] T041 [US2] Crear pruebas unitarias de fechas, MIME, extensión, tamaño, hash y autorización de unidad en `backend/tests/unit/evidencias/test_upload_rules.py`.
- [ ] T042 [US2] Crear pruebas de integración de plan, carga válida, carga inválida y transición a revisión en `backend/tests/integration/evidencias/test_upload_flow.py`.
- [ ] T043 [US2] Crear pruebas de seguridad BOLA/IDOR entre dos dependencias que exijan HTTP 404 sin revelar la existencia del recurso y registren el intento en auditoría en `backend/tests/security/test_evidence_object_authorization.py`.

## Fase 5: Historia de Usuario 3 - Revisar, aprobar o devolver evidencias (P1)

**Objetivo**: Permitir el dictamen UAI y hacer cumplir la máquina de estados,
incluyendo el bloqueo del salto ilegal a `CUMPLIDA`. **Prueba independiente**:
aprobar una evidencia válida o rechazarla con observaciones y revisar auditoría.

- [ ] T044 [P] [US3] Crear enums, entidad y tabla `DictamenUAI` con resultados `APROBADO` y `RECHAZADO` en `backend/modules/evidencias/domain/dictamen.py`.
- [X] T045 [US3] Implementar la máquina de estados con transiciones permitidas, precondiciones, roles y eventos en `backend/modules/recomendaciones/domain/state_machine.py`.
- [ ] T046 [US3] Implementar caso de uso de dictamen con `transaction.atomic`, `SELECT FOR UPDATE`, validación de revisión previa, evidencia validada y escritura del audit log en `backend/modules/evidencias/application/issue_dictamen.py`.
- [ ] T047 [US3] Implementar rechazo con observaciones, estado `RECHAZADA_CORRECCION` y conservación de archivos y revisiones anteriores en `backend/modules/evidencias/application/reject_evidence.py`.
- [ ] T048 [US3] Implementar endpoint `PATCH /api/v1/recomendaciones/{id}/dictamen` con permisos UAI y conflictos HTTP 409 en `backend/modules/evidencias/presentation/views.py`.
- [ ] T049 [US3] Crear modelo y repositorio de `DictamenUAI` con relación a evidencia y evaluador en `backend/modules/evidencias/infrastructure/repositories.py`.
- [X] T050 [US3] Crear pruebas unitarias de la invariante de `CUMPLIDA` y reglas críticas en `backend/tests/unit/test_mvp.py`.
- [ ] T051 [US3] Crear pruebas de integración de aprobación, rechazo, observaciones, historial y error 409 en `backend/tests/integration/evidencias/test_dictamen_flow.py`.
- [ ] T052 [US3] Crear prueba de concurrencia con dos dictámenes simultáneos y bloqueo de recomendación en `backend/tests/concurrency/test_recommendation_locking.py`.

## Fase 6: Historia de Usuario 4 - Supervisar riesgos y vencimientos (P2)

**Objetivo**: Automatizar alertas, morosidad y tablero ejecutivo. **Prueba
independiente**: evaluar recomendaciones con reloj controlado y consultar indicadores
por rol.

- [ ] T053 [P] [US4] Crear modelos y migración de `Notificacion` con `clave_idempotencia` única, destinatario, estado, intentos y fechas en `backend/modules/notificaciones/infrastructure/models.py`.
- [ ] T054 [P] [US4] Crear política de plazos y clasificación de riesgo en `backend/modules/notificaciones/domain/deadline_policy.py`.
- [ ] T055 [US4] Implementar caso de uso idempotente de alertas a 15 días o menos, persistencia visible en la bandeja interna y reintentos SMTP sin perder la alerta interna en `backend/modules/notificaciones/application/send_deadline_alerts.py`.
- [ ] T056 [US4] Implementar caso de uso de transición a `EN_MORA` con ausencia de evidencia aprobada, auditoría y notificación a máxima autoridad en `backend/modules/notificaciones/application/mark_overdue.py`.
- [ ] T057 [US4] Implementar adaptador SMTP detrás de puerto con registro de fallos sin revertir la transacción de negocio en `backend/modules/notificaciones/infrastructure/smtp_adapter.py`.
- [ ] T058 [US4] Implementar tarea programada observable con zona horaria y frecuencia configurables en `backend/modules/notificaciones/infrastructure/scheduled_jobs.py`.
- [ ] T059 [US4] Implementar consulta del tablero con porcentaje, semáforo y unidades en mora en `backend/modules/reportes/application/get_dashboard.py`.
- [ ] T060 [US4] Implementar endpoint de tablero con autorización exclusiva para `RECTORADO` y roles aprobados en `backend/modules/reportes/presentation/views.py`.
- [ ] T060a [US4] Implementar consulta de bandeja de notificaciones internas con autorización por destinatario, estado de lectura e idempotencia en `backend/modules/notificaciones/presentation/views.py`.
- [ ] T061 [US4] Crear pruebas unitarias de umbrales, evidencia presentada frente a validada e idempotencia en `backend/tests/unit/notificaciones/test_deadlines.py`.
- [ ] T062 [US4] Crear pruebas de integración de SMTP fallido, reintento, `EN_MORA` y tablero en `backend/tests/integration/notificaciones/test_scheduled_flows.py`.

## Fase 7: Historia de Usuario 5 - Auditar y exportar el cumplimiento (P2)

**Objetivo**: Proteger y consultar la trazabilidad, verificar hashes y exportar la
matriz institucional. **Prueba independiente**: consultar eventos y generar un
reporte con un usuario UAI o CGE.

- [ ] T063 [P] [US5] Crear migración y modelo `AuditLog` con `request_id`, timestamp UTC, actor, IP, módulo, acción, entidad, estados y `detalles_jsonb` en `backend/core/audit/models.py`.
- [ ] T064 [US5] Implementar interceptor transaccional de auditoría para operaciones mutativas en `backend/core/audit/audit_interceptor.py`.
- [ ] T065 [US5] Implementar protección de consulta y prohibición de modificación o eliminación de auditoría en `backend/core/audit/audit_repository.py`.
- [ ] T066 [US5] Implementar verificación de hash contra almacenamiento y resultado de integridad en `backend/modules/evidencias/application/verify_integrity.py`.
- [ ] T067 [US5] Implementar consultas de historial con autorización `UAI` y `CGE_AUDITOR` en `backend/core/audit/query_audit_log.py`.
- [ ] T068 [US5] Implementar servicio de matriz normalizada y exportación exclusivamente CSV UTF-8 mediante `POST /api/v1/reportes/matriz-cge` en `backend/modules/reportes/application/export_matriz.py`.
- [ ] T069 [US5] Implementar endpoint de matriz y paginación de consultas en `backend/modules/reportes/presentation/views.py`.
- [ ] T070 [US5] Crear pruebas de contrato contra `contracts/openapi.yaml` para envoltura, estados, errores y paginación en `backend/tests/contract/test_api_contract.py`.
- [ ] T071 [US5] Crear pruebas de seguridad de consulta de auditoría, integridad de hash y filtrado de datos no autorizados en `backend/tests/security/test_audit_and_reports.py`.
- [ ] T072 [US5] Crear pruebas de rendimiento de tablero y exportación CSV con objetivos p95 de 3 y 5 segundos usando una carga reproducible de 1.000 recomendaciones, 200 usuarios y 20 consultas concurrentes en `backend/tests/integration/reportes/test_report_performance.py`.

## Fase 8: Historia de Usuario 6 - Administrar identidad y configuración (P3)

**Objetivo**: Integrar identidad institucional, gestionar roles y mantener
dependencias y configuración de notificaciones. **Prueba independiente**: autenticar
un usuario, cambiar su rol o unidad y comprobar permisos y auditoría.

- [X] T073 [P] [US6] Implementar adaptador SSO institucional detrás del puerto de autenticación y mapeo de identidad en `backend/modules/usuarios/infrastructure/sso_adapter.py`.
- [X] T074 [US6] Implementar caso de uso de inicio de sesión seguro con expiración y roles vigentes en `backend/modules/usuarios/application/login_sso.py`.
- [X] T075 [US6] Implementar casos de uso DTI para asignar y revocar roles con segregación de funciones en `backend/modules/usuarios/application/manage_roles.py`.
- [X] T076 [US6] Implementar casos de uso para crear, actualizar y reasignar dependencias sin perder historial en `backend/modules/usuarios/application/manage_units.py`.
- [X] T077 [US6] Implementar endpoint `POST /api/v1/auth/login-sso` y endpoints administrativos protegidos en `backend/modules/usuarios/presentation/views.py`.
- [X] T078 [US6] Registrar auditoría de autenticación, cambios de roles y reasignaciones administrativas en `backend/modules/usuarios/application/audit_events.py`.
- [X] T079 [US6] Crear pruebas unitarias de roles, segregación, expiración y reasignación en `backend/tests/unit/usuarios/test_identity_rules.py`.
- [X] T080 [US6] Crear pruebas de integración del adaptador SSO simulado y administración DTI en `backend/tests/integration/usuarios/test_admin_flow.py`.
- [X] T081 [P] [US6] Crear modelo y migración de preferencias de notificación por usuario y tipo de alerta en `backend/modules/notificaciones/infrastructure/preferences_models.py`.
- [X] T082 [US6] Implementar caso de uso DTI para configurar umbrales, destinatarios y canales de notificación sin guardar secretos SMTP en `backend/modules/notificaciones/application/manage_notification_settings.py`.
- [X] T083 [US6] Implementar consulta y actualización de preferencias de notificación con autorización exclusiva del usuario o DTI en `backend/modules/notificaciones/presentation/preferences_views.py`.
- [X] T084 [US6] Registrar auditoría de cambios de umbrales, destinatarios, canales y preferencias de notificación en `backend/modules/notificaciones/application/settings_audit_events.py`.
- [X] T085 [US6] Crear pruebas unitarias de validación de configuración, segregación de funciones y ausencia de secretos en `backend/tests/unit/notificaciones/test_settings_rules.py`.
- [X] T086 [US6] Crear pruebas de integración de configuración de alertas, preferencias e idempotencia de notificaciones en `backend/tests/integration/notificaciones/test_settings_flow.py`.
- [X] T087 [US6] Documentar variables de entorno y procedimiento de configuración institucional de SSO, SMTP y almacenamiento en `docs/manual-tecnico.md`.
- [X] T088 [US6] Validar el flujo administrativo completo de identidad y configuración en `backend/tests/integration/usuarios/test_identity_configuration_flow.py`.

## Fase 9: Frontend y experiencia de usuario

**Objetivo**: Construir una interfaz comprensible para los cinco actores sin duplicar
reglas de negocio del backend.

- [X] T089 [P] [US1] Inicializar la aplicación React/TypeScript/Vite en `frontend/` y configurar Vitest, ESLint y Prettier.
- [X] T090 [P] [US1] Crear cliente HTTP tipado a partir de `specs/001-seguimiento-recomendaciones/contracts/openapi.yaml` en `frontend/src/api/client.ts`.
- [X] T091 [US1] Crear pantalla de registro y asignación de recomendaciones para UAI en `frontend/src/features/recomendaciones/pages/RegistroRecomendacionPage.tsx`.
- [X] T092 [US2] Crear bandeja del ejecutor y formulario de plan de acción en `frontend/src/features/planes/pages/PlanAccionPage.tsx`.
- [X] T093 [US2] Crear componente de carga PDF con mensajes de validación y progreso en `frontend/src/features/evidencias/components/EvidenceUpload.tsx`.
- [X] T094 [US3] Crear pantalla de revisión UAI con aprobación, rechazo y observaciones en `frontend/src/features/evidencias/pages/ReviewEvidencePage.tsx`.
- [X] T095 [US4] Crear dashboard de Rectorado con semáforo, cumplimiento y mora en `frontend/src/features/dashboard/pages/ExecutiveDashboardPage.tsx`.
- [X] T096 [P] [US1] Crear pruebas de componentes y flujos de permisos en `frontend/src/features/**/*.test.tsx`.
- [X] T097 [P] [US4] Crear pruebas Playwright del flujo principal en `frontend/tests/e2e/recommendation-flow.spec.ts`.

## Fase 10: Pulido y controles transversales

**Objetivo**: Asegurar cumplimiento constitucional, calidad, documentación y
operación antes de integrar.

- [X] T098 [P] Actualizar `specs/001-seguimiento-recomendaciones/contracts/openapi.yaml` con los esquemas y respuestas finales implementadas.
- [X] T099 [P] Añadir documentación de arquitectura C4 y límites modulares en `docs/architecture/sitra-cge.md`.
- [X] T100 [P] Añadir documentación de configuración segura, SSO, SMTP, almacenamiento y variables de entorno en `docs/operations/configuration.md`.
- [X] T101 [P] Crear comprobación automática de secretos y datos sensibles en logs en `backend/tests/security/test_secret_and_log_safety.py`.
- [X] T102 [P] Crear prueba de humo de los escenarios de `specs/001-seguimiento-recomendaciones/quickstart.md` en `backend/tests/integration/test_quickstart.py`.
- [X] T103 Ejecutar lint, tipado, pruebas unitarias, integración, contrato, seguridad y concurrencia desde `backend/pyproject.toml` y `frontend/package.json`.
- [X] T104 Revisar trazabilidad RF/RNF -> componente -> entidad -> endpoint -> prueba y actualizar `specs/001-seguimiento-recomendaciones/plan.md`.
- [X] T105 Verificar los criterios SC-001 a SC-010 y documentar resultados en `specs/001-seguimiento-recomendaciones/quickstart.md`.

## Grafo de dependencias y oportunidades paralelas

```text
T001-T007
  └── T008-T022
        ├── T023-T032 (US1)
        │     ├── T033-T043 (US2)
        │     │     └── T044-T052 (US3)
        │     │           └── T063-T072 (US5)
        │     ├── T053-T062 (US4)
        │     └── T073-T088 (US6)
        ├── T089-T097 (Frontend, después de contratos y flujos relevantes)
        └── T098-T105 (Pulido, después de historias y frontend relevantes)
```

### Ejecución paralela por historia

- **Fundamentos**: T009, T010, T011, T012, T014, T015, T016, T017 y T018 pueden
  trabajarse en paralelo después de T001-T008; T019-T020 dependen de la configuración.
- **US1**: T023, T024 y T025 son paralelizables; T026-T030 dependen de entidades y
  repositorios; T031-T032 pueden avanzar junto con la implementación.
- **US2**: T033-T034 y T036 pueden avanzar en paralelo; T035, T037-T040 dependen
  del modelo y los puertos; T041-T043 son pruebas paralelizables.
- **US3**: T044 y T049 pueden avanzar en paralelo; T045-T048 dependen de contratos;
  T050-T052 son pruebas paralelizables después del dominio.
- **US4**: T053-T054 pueden avanzar en paralelo; T055-T060 dependen de sus puertos;
  T061-T062 son pruebas paralelizables.
- **US5**: T063 y T066 pueden avanzar en paralelo; T064-T069 dependen del modelo;
  T070-T072 son pruebas paralelizables.
- **US6**: T073 y T075-T076 pueden avanzar en paralelo; T074 y T077-T078 dependen
  de los puertos; T081 puede avanzar en paralelo con T073; T082-T084 dependen de
  los modelos y puertos; T079-T080 y T085-T088 son pruebas/documentación
  paralelizables después de la implementación correspondiente.
- **Frontend**: T089-T090 pueden avanzar en paralelo; T091-T095 dependen del cliente
  tipado y los contratos; T096-T097 pueden avanzar con las pantallas.

## Criterios de completitud por historia

| Historia | Incremento independiente | Criterio de aceptación |
| --- | --- | --- |
| US1 | Informe y recomendación asignada | Registro completo, `PENDIENTE`, validaciones y auditoría |
| US2 | Plan y evidencia | Hitos dentro de plazo, PDF válido, hash y `EN_REVISION_INTERNA` |
| US3 | Dictamen UAI | Aprobación válida, rechazo trazable y 409 ante salto ilegal |
| US4 | Alertas y tablero | Alertas idempotentes, `EN_MORA` correcto e indicadores |
| US5 | Auditoría y matriz | Historial protegido, hash verificable y exportación autorizada |
| US6 | Administración | SSO/RBAC, reasignación con historial y configuración auditada |

## MVP recomendado

El MVP comprende T001-T052 y una primera pantalla de validación de T089-T094:
fundamentos, US1, US2, US3 y las pantallas mínimas. Con ese alcance se puede
registrar una recomendación, asignarla, ejecutar un plan, cargar evidencia, revisar
la evidencia y evitar declaraciones de cumplimiento inválidas. US4, US5 y US6 se
entregan después sin romper los contratos ni las entidades del MVP.

## Phase 11: Convergence

**Purpose**: Close the remaining gaps found by `sitra-completeness-review` after
the current implementation pass. These tasks are append-only follow-up work and
must preserve the existing contracts and constitutional constraints.

- [ ] T106 Integrar los endpoints y casos de uso MVP con repositorios Django persistentes, eliminando el almacenamiento en memoria para informes, recomendaciones, planes y evidencias según RF-005-RF-010 (contradicts) en `backend/core/api/views.py`, `backend/modules/recomendaciones/application/service.py` y `backend/modules/recomendaciones/infrastructure/repositories.py`.
- [ ] T107 Implementar el modelo, migración, repositorio e interceptor de `AuditLog` inmutable y transaccional para todas las operaciones mutativas y denegaciones BOLA según Constitution IV y RF-017 (missing) en `backend/core/audit/models.py`, `backend/core/audit/audit_interceptor.py`, `backend/core/audit/audit_repository.py` y `backend/modules/recomendaciones/application/audit_events.py`.
- [ ] T108 Completar el flujo persistente de planes, evidencias y dictámenes con validación de fechas, almacenamiento PDF, observaciones, conservación de revisiones y transición de estados según RF-007-RF-010 y US2/AC1-US3/AC3 (partial) en `backend/modules/recomendaciones/application/create_plan_accion.py`, `backend/modules/evidencias/application/issue_dictamen.py`, `backend/modules/evidencias/application/reject_evidence.py` y `backend/modules/evidencias/infrastructure/storage_adapter.py`.
- [ ] T109 Ejecutar cambios de estado, cargas de evidencia y dictámenes dentro de `transaction.atomic` con `select_for_update`, y crear pruebas de carreras concurrentes según Constitution VI y RF-020 (missing) en `backend/modules/evidencias/application/issue_dictamen.py` y `backend/tests/concurrency/test_recommendation_locking.py`.
- [ ] T110 Implementar notificaciones internas idempotentes, reintentos SMTP, evaluación de mora, tablero ejecutivo y exportación CSV autorizada según RF-011-RF-014, US4 y US5 (missing) en `backend/modules/notificaciones/`, `backend/modules/reportes/` y `backend/tests/integration/reportes/`.
- [ ] T111 Implementar autenticación SSO mediante adaptador, RBAC persistente, administración DTI de roles/unidades y configuración auditada de notificaciones según RF-001-RF-004 y US6 (missing) en `backend/modules/usuarios/infrastructure/sso_adapter.py`, `backend/modules/usuarios/application/` y `backend/modules/notificaciones/application/`.
- [ ] T112 Conectar el manejador global de excepciones a Django y uniformar respuestas 405, autenticación, autorización, validación, 404 y errores internos con el envelope universal según RF-015-RF-016 y RNF-004 (contradicts) en `backend/config/settings.py`, `backend/core/api/exception_handler.py` y `backend/core/api/views.py`.
- [ ] T113 Configurar PostgreSQL mediante Psycopg, conservar auditoría en UTC y calcular vencimientos/alertas de negocio en `America/Guayaquil` según plan, research y las aclaraciones aceptadas (contradicts) en `backend/config/settings.py`, `backend/.env.example` y `backend/tests/integration/test_timezone_behavior.py`.
- [ ] T114 Integrar Django REST Framework en las vistas publicadas, registrar serializers y permisos, y crear pruebas automáticas contra `contracts/openapi.yaml` según el plan y RF-022 (missing) en `backend/config/settings.py`, `backend/modules/*/presentation/` y `backend/tests/contract/test_api_contract.py`.
- [ ] T115 Crear el frontend React/TypeScript/Vite mínimo para registro, plan, evidencia, dictamen y tablero, con cliente tipado y pruebas de permisos según el plan y US1-US4 (missing) en `frontend/` y `frontend/tests/e2e/recommendation-flow.spec.ts`.
- [ ] T116 Completar la defensa BOLA/IDOR para consulta, plan, evidencia y dictamen, registrando intentos no autorizados y devolviendo HTTP 404 sin filtrar existencia según RF-019 y RNF-003 (partial) en `backend/core/auth/authorization.py`, `backend/core/api/views.py` y `backend/tests/security/test_evidence_object_authorization.py`.
- [ ] T117 Ejecutar la validación completa del quickstart, pruebas de integridad contra almacenamiento, SMTP fallido, jobs idempotentes, seguridad, rendimiento p95 y criterios SC-001-SC-010 según RNF-001-RNF-008 y quickstart.md (missing) en `backend/tests/integration/`, `backend/tests/security/`, `backend/tests/concurrency/` y `backend/tests/integration/reportes/test_report_performance.py`.

## Phase 12: Convergence

**Purpose**: Make the pending convergence work independently executable and
verifiable after the previous implementation pass.

- [X] T118 Reemplazar completamente los diccionarios `reports`, `service.recommendations` y `service.plans` de la API por casos de uso persistentes que creen y consulten `InformeCGE`, `Recomendacion` y `PlanAccion` mediante repositorios Django según T106 y Constitution III (contradicts) en `backend/core/api/views.py`, `backend/modules/informes_cge/application/register_informe.py` y `backend/modules/recomendaciones/application/`.
- [ ] T119 Registrar en una tabla `AuditLog` persistente cada creación, cambio de estado, carga de evidencia, dictamen y denegación BOLA, incluyendo `request_id`, usuario, IP, estados y resultado, y protegerla contra UPDATE/DELETE según T107 y RF-017 (missing) en `backend/core/audit/models.py`, `backend/core/audit/audit_interceptor.py` y `backend/tests/integration/test_foundation.py`.
- [X] T120 Crear el flujo ORM completo de evidencia y dictamen con `transaction.atomic`, `select_for_update`, almacenamiento aislado, observaciones de rechazo y conservación de revisiones, verificando `Cumplida` solo con evidencia aprobada según T108-T109 y US2/AC2-US3/AC2 (partial) en `backend/modules/evidencias/` y `backend/tests/concurrency/test_recommendation_locking.py`.
- [ ] T121 Implementar los módulos de notificaciones y reportes con modelos, endpoints y pruebas para alertas internas, reintentos SMTP, mora, tablero y CSV UTF-8, incluyendo autorización UAI/RECTORADO/CGE según T110 y RF-011-RF-014 (missing) en `backend/modules/notificaciones/`, `backend/modules/reportes/` y `backend/tests/integration/reportes/`.
- [ ] T122 Implementar SSO/RBAC persistente, reasignación de unidad con historial y configuración de notificaciones sin secretos en código según T111 y RF-001-RF-004 (missing) en `backend/modules/usuarios/application/`, `backend/modules/usuarios/infrastructure/sso_adapter.py` y `backend/modules/notificaciones/application/`.
- [ ] T123 Conectar el manejador de excepciones y Django REST Framework al enrutamiento real, haciendo que métodos no permitidos, errores de autenticación, validación, permisos, 404 y conflictos usen el envelope definido y sean comprobables contra OpenAPI según T112 y T114 (contradicts) en `backend/config/settings.py`, `backend/config/urls.py`, `backend/core/api/exception_handler.py` y `backend/tests/contract/test_api_contract.py`.
- [ ] T124 Configurar PostgreSQL por variables de entorno, mantener timestamps técnicos en UTC y calcular vencimientos de negocio en `America/Guayaquil`, y añadir la aplicación React/Vite mínima para el flujo US1-US4 según T113 y T115 (missing) en `backend/config/settings.py`, `backend/.env.example`, `frontend/` y `frontend/tests/e2e/recommendation-flow.spec.ts`.
- [ ] T125 Ejecutar una validación de cierre que demuestre persistencia tras reinicio, autorización 404 entre unidades, integridad PDF, concurrencia, alertas idempotentes, CSV y criterios SC-001-SC-010 según T116-T117 y quickstart.md (missing) en `backend/tests/integration/`, `backend/tests/security/` y `backend/tests/concurrency/`.

## Phase 13: Convergence

**Purpose**: Close the remaining gaps found after implementing the persistence,
evidence, reporting and initial frontend foundations.

- [ ] T126 Proteger `AuditLog` contra UPDATE, DELETE y borrado en cascada mediante restricciones de modelo, permisos de infraestructura y pruebas, registrar IP y resultado, y auditar todas las denegaciones BOLA según Constitution IV-V, RF-017 y US5/AC1 (critical, partial) en `backend/core/audit/models.py`, `backend/core/audit/repository.py`, `backend/core/api/views.py` y `backend/tests/security/`.
- [ ] T127 Implementar la ejecución de notificaciones internas y correo institucional con adaptador SMTP, reintentos acotados, clave idempotente, evaluación de vencimientos/mora y tablero ejecutivo según RF-011-RF-014, US4/AC1-US4/AC3 y US3/AC2 (high, missing) en `backend/modules/notificaciones/application/`, `backend/modules/notificaciones/infrastructure/`, `backend/modules/reportes/` y `backend/tests/integration/`.
- [ ] T128 Sustituir la autenticación de desarrollo por puertos de SSO configurables, aplicar RBAC persistente por endpoint, gestionar reasignaciones con historial y administrar unidades/configuración DTI según RF-001-RF-004, US6 y Constitution V (critical, contradicts) en `backend/core/auth/`, `backend/modules/usuarios/application/`, `backend/modules/usuarios/infrastructure/` y `backend/tests/security/`.
- [ ] T129 Integrar realmente Django REST Framework, serializers, permisos y el manejador global de excepciones para que autenticación, validación, 404, 405, conflictos y errores internos usen el envelope universal y coincidan con OpenAPI según RF-015, RF-016, RF-022 y Constitution III-VI (critical, contradicts) en `backend/config/settings.py`, `backend/config/urls.py`, `backend/core/api/exception_handler.py`, `backend/modules/*/presentation/` y `backend/tests/contract/`.
- [ ] T130 Reorganizar las vistas para que la capa de presentación no consulte ORM directamente, trasladar la coordinación a casos de uso y eliminar el servicio de memoria de los flujos publicados según Constitution III y el plan de arquitectura limpia (high, contradicts) en `backend/core/api/views.py`, `backend/modules/informes_cge/application/`, `backend/modules/recomendaciones/application/` y `backend/modules/recomendaciones/infrastructure/`.
- [ ] T131 Completar el frontend React con rutas y vistas protegidas para DTI, UAI, Ejecutor, Rectorado y Auditor CGE, incluyendo formularios de informe/recomendación, plan, evidencia, dictamen, tablero, auditoría y exportación según US1-US6, RNF-003 y el plan (high, partial) en `frontend/src/` y `frontend/tests/`.
- [ ] T132 Crear pruebas automatizadas del quickstart y de los criterios SC-001-SC-010 para persistencia tras reinicio, BOLA 404, integridad PDF, dictámenes, concurrencia, notificaciones idempotentes, CSV y límites p95 con la carga de referencia según RNF-001-RNF-008 y quickstart.md (high, missing) en `backend/tests/integration/`, `backend/tests/security/`, `backend/tests/concurrency/`, `backend/tests/contract/` y `frontend/tests/`.

## Phase 14: Convergence

**Purpose**: Close the remaining gaps after the initial security, notification,
DRF configuration and role-interface implementation.

- [ ] T133 Enforce audit immutability at the database and repository boundaries, prevent bulk UPDATE/DELETE and cascade removal, capture operation results and add regression tests for direct ORM attempts according to Constitution IV and RF-017 (critical, partial) in `backend/core/audit/models.py`, `backend/core/audit/repository.py`, migrations and `backend/tests/security/test_audit_immutability.py`.
- [ ] T134 Replace development headers and the deterministic SSO placeholder with a configurable institutional identity adapter that issues an expiring authenticated session/token, and add role/endpoint authorization tests according to Constitution V, RF-001-RF-004 and US6 (critical, contradicts) in `backend/core/auth/`, `backend/modules/usuarios/infrastructure/sso_adapter.py`, `backend/core/api/views.py` and `backend/tests/security/`.
- [ ] T135 Publish the API through DRF `APIView`/serializers/permissions, adapt the universal exception handler to DRF's required callable contract, and return the envelope for 404, 405, validation, authentication, authorization and conflict responses according to RF-015, RF-016, RF-022 and OpenAPI (critical, contradicts) in `backend/config/settings.py`, `backend/config/urls.py`, `backend/core/api/exception_handler.py`, `backend/modules/*/presentation/` and `backend/tests/contract/`.
- [ ] T136 Implement scheduled deadline evaluation that distinguishes presented from validated evidence, marks recommendations `EN_MORA`, creates idempotent internal/email notifications with bounded retry behavior, and exposes the executive risk dashboard according to RF-011-RF-014 and US4/AC1-US4/AC3 (high, partial) in `backend/modules/notificaciones/application/`, `backend/modules/reportes/` and `backend/tests/integration/test_deadlines.py`.
- [ ] T137 Move ORM coordination out of HTTP views into application use cases and repositories, remove the published dependency on `RecommendationService` memory collections, and preserve transaction/audit behavior according to Constitution III and the clean-architecture plan (high, contradicts) in `backend/core/api/views.py`, `backend/modules/informes_cge/application/`, `backend/modules/recomendaciones/application/` and `backend/modules/recomendaciones/infrastructure/`.
- [ ] T138 Replace role selector placeholders in React with protected routes and working forms/actions for UAI, Ejecutor, Rectorado, DTI and Auditor CGE, including report/recommendation creation, plan/evidence submission, dictamen, dashboard, audit history and CSV export according to US1-US6 and RNF-003 (high, partial) in `frontend/src/` and `frontend/tests/`.
- [ ] T139 Add executable contract, security, concurrency, integrity, notification, persistence-after-restart, quickstart and performance tests for the 1,000-recommendation/200-user/20-concurrent-request reference load, and document the validation command according to RNF-001-RNF-008, SC-001-SC-010 and quickstart.md (high, missing) in `backend/tests/`, `frontend/tests/` and `docs/manual-tecnico.md`.
