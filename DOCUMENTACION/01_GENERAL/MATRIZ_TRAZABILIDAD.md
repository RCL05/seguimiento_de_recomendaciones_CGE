## Cómo leer la matriz

Cada fila sigue la cadena **Requisito → Funcionalidad → Componente → Implementación → Prueba → Evidencia**. Solo se registran relaciones comprobadas leyendo el código y los nombres de las pruebas; la columna *Evidencia* indica el resultado de la ejecución del 2026-11-11 (`pytest`: 231 pruebas aprobadas). Cuando falta un eslabón, se indica explícitamente.

Rutas abreviadas: `rec/` = `backend/modules/recomendaciones/`, `evi/` = `backend/modules/evidencias/`, `not/` = `backend/modules/notificaciones/`, `rep/` = `backend/modules/reportes/`, `usu/` = `backend/modules/usuarios/`, `inf/` = `backend/modules/informes_cge/`, `t/` = `backend/tests/`.

## Matriz

| Requisito | Funcionalidad | Componente | Implementación | Prueba | Evidencia |
|---|---|---|---|---|---|
| RF-001 | Inicio de sesión SSO y JWT | `usuarios` | `usu/application/login_sso.py`, `usu/infrastructure/sso_adapter.py`, `core/auth/authentication.py` | `t/unit/usuarios/test_sso_jwt.py`, `t/integration/usuarios/test_admin_flow.py`, `t/api/test_http_api.py::test_login_sso_devuelve_jwt_con_claims_de_identidad` | Aprobadas |
| RF-002 | Asignar/revocar rol | `usuarios` | `usu/application/manage_roles.py`, `PATCH /usuarios/{id}` | `t/api/test_endpoints_base.py::test_dti_asigna_rol_y_unidad`, `t/unit/usuarios/test_identity_rules.py::test_roles_segregacion_y_expiracion` | Aprobadas |
| RF-003 | Reasignar recomendación | `recomendaciones` | `rec/application/reasignar_recomendacion.py`, `PATCH /recomendaciones/{id}` con `unit_id` | `t/integration/recomendaciones/test_reassignment.py` | Aprobadas |
| RF-004 | Alertas internas y correo | `notificaciones` | `not/application/service.py`, `manage_notification_settings.py` | `t/integration/notificaciones/test_settings_flow.py`, `t/unit/notificaciones/test_settings_rules.py`, `t/integration/notificaciones/test_delivery_retries.py` | Aprobadas (reintento acotado) |
| RF-005 | Registrar informe | `informes_cge` | `inf/application/register_informe.py`, `POST /informes` | `t/api/test_endpoints_base.py::test_informe_201_con_location_y_consulta_por_id`, `test_informe_duplicado_responde_409` | Aprobadas |
| RF-006 | Registrar recomendación | `recomendaciones` | `rec/application/create_recomendacion.py`, `POST /recomendaciones` | `t/integration/recomendaciones/test_registration.py`, `t/unit/recomendaciones/test_creation_rules.py` | Aprobadas |
| RF-007 | Plan de acción | `recomendaciones` | `rec/application/create_plan_accion.py`, `rec/domain/vencimiento.py` | `t/unit/recomendaciones/test_state_machine_spec.py::test_fecha_de_hito_dentro_y_fuera_de_plazo`, `t/integration/notificaciones/test_vencimientos.py` | Aprobadas |
| RF-008 | Carga de PDF | `evidencias` | `rec/application/upload_evidencia.py`, `rec/infrastructure/storage.py`, `evi/presentation/views.py` | `t/unit/evidencias/test_upload_rules.py`, `t/integration/evidencias/test_upload_flow.py` | Aprobadas |
| RF-009 | Máquina de estados | `recomendaciones` | `rec/domain/state_machine.py` | `t/unit/recomendaciones/test_state_machine_spec.py` (19), `t/unit/test_mvp.py::test_illegal_jump_to_completed_is_conflict` | Aprobadas |
| RF-010 | Dictamen y rechazo | `recomendaciones`, `evidencias` | `rec/application/issue_dictamen.py`, `rec/presentation/serializers.py::DictamenCreateSerializer` | `t/integration/evidencias/test_dictamen_flow.py`, `t/api/test_endpoints_base.py::test_rechazo_sin_observaciones_responde_400` | Aprobadas |
| RF-011 | Alertas ≤ 15 días | `notificaciones` | `not/application/send_deadline_alerts.py` | `t/unit/notificaciones/test_deadlines.py` | Aprobadas |
| RF-012 | Registro de vencimiento | `notificaciones`, `recomendaciones` | `not/application/mark_overdue.py`, `rec/domain/vencimiento.py` | `t/integration/notificaciones/test_vencimientos.py` (7) | Aprobadas |
| RF-013 | Tablero ejecutivo | `reportes` | `rep/application/get_dashboard.py`, `GET /reportes/tablero` | `t/api/test_endpoints_base.py::test_tablero_lista_unidades_en_mora`, `t/api/test_http_api.py::test_rectorado_inicia_sesion_y_consulta_tablero` | Aprobadas |
| RF-014 | Matriz CSV | `reportes` | `rep/application/export_matriz.py` | `t/security/test_audit_and_reports.py::test_matriz_csv_restingida_por_rol`, `test_matriz_es_get_y_csv` | Aprobadas; conformidad normativa sin evidencia (H-09) |
| RF-015 | Envoltura universal | `core/api` | `core/api/response_envelope.py`, `base.py` | `t/contract/test_api_contract.py::test_contract_envoltorio_exitoso_y_error` | Aprobadas |
| RF-016 | Catálogo de errores | `core/api` | `core/api/exception_handler.py`, `middleware.py` | `t/integration/test_foundation.py::test_catalogo_de_errores_mapea_estado_y_codigo`, `t/api/test_http_semantics.py` | Aprobadas |
| RF-017 | Auditoría mutativa | `core/audit` | `core/audit/repository.py::record_audit`, `*/application/audit_events.py` | `t/integration/test_quickstart.py::test_flujo_principal_aprobacion_y_cadena_de_auditoria` | Aprobadas |
| RF-018 | Consulta CGE | `reportes`, `evidencias` | `AuditoriaView`, `evi/application/verify_integrity.py` | `t/security/test_audit_and_reports.py::test_consulta_auditoria_solo_autorizados_y_sin_modificacion` | Aprobadas |
| RF-019 | Protección BOLA/IDOR | `recomendaciones`, `evidencias` | `rec/application/get_recomendacion.py`, `upload_evidencia.py::_authorize` | `t/security/test_evidence_object_authorization.py` | Aprobadas |
| RF-020 | Concurrencia | `recomendaciones` | `select_for_update` en `issue_dictamen.py`, `create_plan_accion.py`, `reabrir_recomendacion.py` | `t/concurrency/test_recommendation_locking.py` | Aprobada |
| RF-021 | Jobs idempotentes | `notificaciones` | `Notificacion.clave_idempotencia`, `scheduled_jobs.py`, `evaluar_plazos` | `t/integration/notificaciones/test_scheduled_job.py` | Aprobadas |
| RF-022 | OpenAPI sincronizado | `config` | `drf-spectacular`, `backend/contracts/openapi.yaml` | `t/contract/test_api_contract.py::test_contrato_publicado_coincide_con_el_codigo` | Aprobada; además el esquema regenerado coincide con ambas copias |
| RF-023 | Reapertura | `recomendaciones` | `rec/application/reabrir_recomendacion.py`, `PATCH /recomendaciones/{id}` | `t/security/test_archivos_y_reapertura.py` (3 pruebas de reapertura) | Aprobadas |
| RF-024 | Archivos protegidos | `evidencias`, `informes_cge` | `evi/application/get_evidence_file.py`, `InformeDocumentoView` | `t/security/test_archivos_y_reapertura.py::test_media_no_se_publica_ni_con_debug`, `test_documento_del_informe_requiere_token_y_rol` | Aprobadas |
| RNF-001 | Integridad SHA-256 | `evidencias` | `verify_integrity.py` | `t/integration/evidencias/test_integrity_flow.py` | Aprobadas |
| RNF-002 | Bitácora inmutable | `core/audit` | `ImmutableAuditLogQuerySet`, `AuditLog.save/delete` | `t/security/test_audit_immutability.py` | Aprobadas |
| RNF-005/006 | Rendimiento | `reportes` | `get_kpis.py`, `export_matriz.py` | `t/integration/reportes/test_report_performance.py` (umbral de tiempo y ausencia de N+1) | Aprobadas |
| RNF-008 | Privacidad en logs | `core/security` | `log_safety.py` | `t/security/test_secret_and_log_safety.py` | Aprobadas |
| RNF-011 | Navegación por rol | frontend | `frontend/src/routes.tsx`, `App.tsx` | `frontend/src/App.test.tsx`, E2E `recommendation-flow.spec.ts` (no ejecutada) | Vitest aprobado; E2E sin evidencia |

## Trazabilidad con historias y frontend

| HU | Páginas del frontend | Pruebas de frontend |
|---|---|---|
| HU1 | `features/recomendaciones/pages/RegistroRecomendacionPage.tsx` | — |
| HU2 | `features/planes/pages/PlanAccionPage.tsx`, `features/evidencias/components/EvidenceUpload.tsx` | `EvidenceUpload.test.tsx` (3) |
| HU3 | `features/evidencias/pages/ReviewEvidencePage.tsx` | `ReviewEvidencePage.test.tsx` (3) |
| HU4 | `features/dashboard/pages/ExecutiveDashboardPage.tsx`, `DashboardKPIs.tsx` | — |
| HU5 | `features/auditoria/pages/AuditPage.tsx` | — |
| HU6 | `features/administracion/pages/UserAdminPage.tsx`, `NotificationSettingsPage.tsx` | `UserAdminPage.test.tsx` (3) |
