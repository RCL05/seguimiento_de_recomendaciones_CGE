## Fuente y método

La fuente única de requisitos es `specs/001-seguimiento-recomendaciones/spec.md` (estado: *en revisión, pendiente de validar con el docente*). Los requisitos están redactados en sintaxis **EARS** y cada historia tiene escenarios **BDD** (*Dado / Cuando / Entonces*). Esta página **no** los reescribe: los resume y añade su **estado de implementación verificado** el 2026-11-10.

Estados: **Implementado y probado** · **Implementado parcialmente** · **No implementado** · **Documental** (se cumple en los artefactos, no en el código).

## Historias de usuario

| HU | Prioridad | Historia | Estado |
|---|---|---|---|
| HU1 | P1 | La UAI registra informes y asigna recomendaciones con plazo legal | Implementado y probado |
| HU2 | P1 | El ejecutor formula hitos y carga evidencias PDF | Implementado y probado |
| HU3 | P1 | La UAI revisa, aprueba o devuelve evidencias; puede reabrir | Implementado y probado |
| HU4 | P2 | El Rectorado supervisa riesgo y vencimientos | Implementado; rendimiento sin medir |
| HU5 | P2 | UAI/CGE auditan y exportan la matriz | Implementado; columnas por validar con la UAI |
| HU6 | P3 | La DTI administra identidad y configuración | Implementado; SSO productivo por definir |

## Requisitos funcionales

| ID | Resumen | Estado | Evidencia principal |
|---|---|---|---|
| RF-001 | Autenticación SSO y token con expiración | Parcial — introspección OAuth2 y JWT HS256 de 1 h implementados; proveedor productivo no definido | `sso_adapter.py`, `test_sso_jwt.py` |
| RF-002 | DTI asigna y revoca los cinco roles | Implementado y probado | `manage_roles.py`, `test_dti_asigna_rol_y_unidad` |
| RF-003 | Reasignar una recomendación a otra unidad conservando historial | Implementado y probado | `reasignar_recomendacion.py`, `test_reassignment.py` |
| RF-004 | Alertas internas y correo según configuración | Implementado — reintento acotado (máx. 3 intentos) | `service.py`, `test_delivery_retries.py` |
| RF-005 | Registrar informe (número, fecha, período, documento) | Implementado y probado | `register_informe.py`, `test_endpoints_base.py` |
| RF-006 | Recomendación con plazo, prioridad y unidad; estado inicial `PENDIENTE` | Implementado y probado | `create_recomendacion.py`, `test_registration.py` |
| RF-007 | Plan con N hitos; fechas dentro del plazo o desde hoy si venció | Implementado y probado | `vencimiento.py`, `create_plan_accion.py`, `test_vencimientos.py` |
| RF-008 | PDF: extensión, firma `%PDF-`, ≤ 30 MB, SHA-256 | Implementado y probado | `upload_evidencia.py`, `storage.py`, `test_upload_rules.py` |
| RF-009 | Flujo de cinco estados; transición no definida → 409 | Implementado y probado | `state_machine.py`, `test_state_machine_spec.py` (19 pruebas) |
| RF-010 | Rechazo exige observaciones y devuelve a `EN_PROCESO` | Implementado y probado | `issue_dictamen.py`, `DictamenCreateSerializer.validate`, `test_rechazo_sin_observaciones_responde_400` |
| RF-011 | Alerta a ≤ 15 días sin evidencia presentada | Implementado y probado | `send_deadline_alerts.py`, `test_deadlines.py` |
| RF-012 | Marcar vencida sin cambiar estado y notificar una vez | Implementado y probado | `mark_overdue.py`, `test_job_registra_y_notifica_sin_cambiar_estado_y_es_idempotente` |
| RF-013 | Tablero con semáforo, porcentaje y unidades en mora | Implementado y probado | `get_dashboard.py`, `test_tablero_lista_unidades_en_mora` |
| RF-014 | Matriz CSV UTF-8 normalizada | Implementado y probado; conformidad con Acuerdo 010-CG-2022 por validar | `export_matriz.py`, `test_matriz_csv_restingida_por_rol`; H-09 |
| RF-015 | Envoltura JSON universal con `request_id` y timestamp | Implementado y probado | `response_envelope.py`, `test_api_contract.py` |
| RF-016 | Catálogo de errores sin detalles internos | Implementado y probado | `exception_handler.py`, `test_catalogo_de_errores_mapea_estado_y_codigo` |
| RF-017 | Auditoría de toda operación mutativa | Implementado y probado | `core/audit`, `test_flujo_principal_aprobacion_y_cadena_de_auditoria` |
| RF-018 | Auditor CGE con acceso de solo lectura | Implementado y probado | `AuditoriaView`, `verify_integrity.py` |
| RF-019 | BOLA/IDOR: otra unidad → 404 y registro del intento | Implementado y probado | `get_recomendacion.py`, `test_evidence_object_authorization.py` |
| RF-020 | Operaciones atómicas sin actualizaciones perdidas | Implementado y probado (bloqueo pesimista) | `select_for_update`, `test_recommendation_locking.py` |
| RF-021 | Jobs idempotentes y observables | Implementado y probado | `clave_idempotencia`, `test_scheduled_job.py` |
| RF-022 | OpenAPI sincronizado y verificado | Implementado y probado | `test_contrato_publicado_coincide_con_el_codigo` |
| RF-023 | Reapertura de `CUMPLIDA` con motivo, solo UAI | Implementado y probado | `reabrir_recomendacion.py`, `test_archivos_y_reapertura.py` |
| RF-024 | Archivos solo por operaciones autenticadas | Implementado y probado | `config/urls.py` (sin `static()`), `test_media_no_se_publica_ni_con_debug` |

## Requisitos no funcionales

| ID | Resumen | Estado | Evidencia / observación |
|---|---|---|---|
| RNF-001 | Integridad documental por SHA-256 | Implementado y probado | `test_integridad_detecta_archivo_alterado` |
| RNF-002 | Bitácora protegida contra modificación | Implementado y probado a nivel ORM | `test_audit_immutability.py`; sin protección a nivel de base de datos |
| RNF-003 | Autorización RBAC y por objeto en servidor | Implementado y probado | permisos DRF + casos de uso |
| RNF-004 | `errors=null` en éxito, `data=null` en error | Implementado y probado | `test_response_envelope_preserves_success_error_invariants` |
| RNF-005 | 95 % del tablero < 3 s | **Sin verificar** | Prueba de marcador (H-19) |
| RNF-006 | 95 % de la matriz < 5 s | **Sin verificar** | Prueba de marcador (H-19) |
| RNF-007 | Fallo de correo no revierte negocio y se reintenta | Implementado y probado | No revierte; reintenta hasta 3 intentos (`test_delivery_retries.py`) |
| RNF-008 | Sin secretos ni trazas en respuestas y logs | Implementado y probado | `test_secret_and_log_safety.py` |
| RNF-009 | EARS + BDD | Documental — cumplido en `spec.md` | — |
| RNF-010 | OpenAPI 3.0.3 válido y CSV legible | Implementado y probado | contrato `openapi: 3.0.3`; CSV con BOM UTF-8 |
| RNF-011 | Cada rol ve solo sus secciones | Implementado; SC-009 (evaluación con usuarios) no realizada | `routes.tsx`, `App.test.tsx` |
| RNF-012 | Accesibilidad (etiquetas, teclado, no solo color) | Sin verificar | No hay pruebas de accesibilidad automatizadas |
| RNF-013 | Reglas de dominio con pruebas; API sin reglas de negocio | Implementado en lo esencial | Dominio probado; algunas vistas consultan el ORM directamente (p. ej. `BandejaView`) |

## Restricciones

- Evidencias solo PDF hasta 30 MB (`MAX_PDF_SIZE_BYTES`, por defecto 31 457 280 bytes).
- Zona horaria de negocio `America/Guayaquil` (`TIME_ZONE`); `USE_TZ=True`; auditoría en UTC.
- API versionada `/api/v1` y contrato OpenAPI 3.0.3.

## Reglas de negocio verificadas

| ID | Regla | Ubicación |
|---|---|---|
| RN-01 | Toda recomendación nace en `PENDIENTE`; el cliente envía `legal_days` (> 0) y `due_date`. El servidor **no** comprueba que ambos sean coherentes con la fecha de notificación del informe (H-24) | `create_recomendacion.py` |
| RN-02 | El primer hito mueve `PENDIENTE`/`REABIERTA` → `EN_PROCESO` | `create_plan_accion.py` |
| RN-03 | Cargar evidencia exige al menos un hito y mueve `EN_PROCESO` → `EN_VALIDACION` | `upload_evidencia.py`, `test_evidence_requires_plan_then_moves_to_review_and_locks_plan` |
| RN-04 | `CUMPLIDA` exige revisión interna previa y evidencia validada | `state_machine.py` |
| RN-05 | Un rechazo exige observaciones y devuelve a `EN_PROCESO`; la evidencia se conserva | `issue_dictamen.py`, `DictamenCreateSerializer` |
| RN-06 | "Vencida" es un indicador calculado, no un estado; una entrega a tiempo pendiente de dictamen no cuenta como vencida | `domain/vencimiento.py` |
| RN-07 | Con plazo vencido, los nuevos hitos deben tener fecha de hoy en adelante | `fecha_compromiso_valida` |
| RN-08 | Semáforo: verde ≥ 75 %, amarillo ≥ 40 %, rojo < 40 % de cumplidas | `get_dashboard.py` |
| RN-09 | Alerta cuando faltan ≤ `umbral_dias` (15 por defecto, 1–90) | `ConfiguracionNotificacion` |
| RN-10 | La configuración de notificaciones rechaza claves que parezcan secretos | `manage_notification_settings.py` |

## Criterios de aceptación y de éxito

Los escenarios BDD de HU1–HU6 y los criterios SC-001…SC-010 están en `spec.md`. Su verificación se resume en el capítulo *Calidad → Matriz de verificación*.
