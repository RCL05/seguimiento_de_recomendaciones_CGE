## Inventario de pruebas del backend

Obtenido con `python -m pytest --collect-only -q` (2026-11-11): **231 pruebas** en 37 archivos (incluye casos parametrizados). Las *fixtures* compartidas viven en `tests/factories.py`.

| Categoría | Archivo | Pruebas | Qué verifica |
|---|---|---|---|
| API | `tests/api/test_contrato_acd3.py` | 10 | Ajustes ACD 3: `/sesiones`, `hitos`, 400 con `errors.fields`, evidencia sin plan 409, dictamen con `Location` consultable, `evaluaciones-plazos` retirado |
| API | `tests/api/test_endpoints_base.py` | 15 | Informes (201 + `Location`, paginación, 409), validación 400, 401 con `WWW-Authenticate`, dictamen, hitos, anulación, integridad, tablero, matriz, rol DTI, Swagger |
| API | `tests/api/test_http_api.py` | 8 | Salud, login SSO → JWT, 401 sin token, tablero de Rectorado, envoltura, rutas, evidencia requiere plan, catálogo de unidades |
| API | `tests/api/test_http_semantics.py` | 15 | 201 + `Location`, JSON mal formado, 405 + `Allow`, 405 antes que 401, `limit` inválido, CORS |
| Concurrencia | `tests/concurrency/test_recommendation_locking.py` | 1 | Dictamen con `select_for_update` |
| Contrato | `tests/contract/test_api_contract.py` | 5 | Envoltura, contrato = código, rutas documentadas, bearer + 401 |
| Integración | `tests/integration/evidencias/test_dictamen_flow.py` | 1 | Cumplida requiere revisión y evidencia validada |
| Integración | `tests/integration/evidencias/test_integrity_flow.py` | 2 | Hash coincide / alterado; contenido vacío |
| Integración | `tests/integration/evidencias/test_upload_flow.py` | 1 | Carga válida, inválida y transición |
| Integración | `tests/integration/notificaciones/test_delivery_retries.py` | 3 | Reintento hasta 3 intentos, agotamiento y no reenvío de `ENVIADA` |
| Integración | `tests/integration/notificaciones/test_scheduled_flows.py` | 1 | SMTP fallido no revierte |
| Integración | `tests/integration/notificaciones/test_scheduled_job.py` | 3 | Composición del job, salida JSON del comando y ejecución real idempotente |
| Integración | `tests/integration/notificaciones/test_settings_flow.py` | 5 | Configuración DTI, preferencias propias, auditoría, idempotencia |
| Integración | `tests/integration/notificaciones/test_vencimientos.py` | 7 | Vencimiento como indicador, entregas a tiempo/tardías, filtro, migración 0007, reapertura |
| Integración | `tests/integration/recomendaciones/test_reassignment.py` | 6 | Reasignación UAI vía PATCH con motivo e historial; 403, 400, 404; PATCH exclusivo y ruta `reasignacion` eliminada |
| Integración | `tests/integration/recomendaciones/test_registration.py` | 1 | Registro, duplicados, estado inicial |
| Integración | `tests/integration/reportes/test_kpis.py` | 1 | Agregación de KPIs |
| Integración | `tests/integration/reportes/test_report_performance.py` | 4 | Tablero < 3 s y matriz < 5 s con todas las filas; consultas sin crecimiento N+1 (H-19 resuelto) |
| Integración | `tests/integration/test_foundation.py` | 7 | Envoltura, catálogo de errores (parametrizado), autorización por rol y unidad |
| Integración | `tests/integration/test_persistence_models.py` | 1 | Unicidad de número por informe |
| Integración | `tests/integration/test_quickstart.py` | 4 | Flujo principal con auditoría, rechazo y corrección, BOLA, matriz por rol |
| Integración | `tests/integration/usuarios/test_admin_flow.py` | 3 | Claims de introspección, tokens de desarrollo, rechazo fuera de `DEBUG` |
| Integración | `tests/integration/usuarios/test_identity_configuration_flow.py` | 1 | Flujo de identidad y configuración |
| Seguridad | `tests/security/test_archivos_y_reapertura.py` | 6 | Media no publicada, documento protegido, reapertura |
| Seguridad | `tests/security/test_audit_and_reports.py` | 6 | Auditoría sin métodos de escritura (post/put/patch/delete), consulta sin alteración y filtro por entidad |
| Seguridad | `tests/security/test_audit_immutability.py` | 3 | Sin update/delete por QuerySet ni re-save |
| Seguridad | `tests/security/test_evidence_object_authorization.py` | 2 | BOLA/IDOR 404 + auditoría; inexistente 404 |
| Seguridad | `tests/security/test_hallazgos_semana4.py` | 7 | SEC-01…SEC-04 (anulación y dictámenes), login auditado y limitado, KPIs por unidad |
| Seguridad | `tests/security/test_secret_and_log_safety.py` | 5 | Redacción, logs, rechazo de secretos, sin eco |
| Unitaria | `tests/unit/evidencias/test_upload_rules.py` | 9 | Extensiones inválidas, contenido disfrazado de PDF, límite acumulado en trozos, hash SHA-256 y BOLA auditada |
| Unitaria | `tests/unit/notificaciones/test_deadlines.py` | 17 | Umbrales parametrizados (15/10/1/0 y 16 días), reglas de vencimiento por estado, idempotencia, preferencias y umbral configurable |
| Unitaria | `tests/unit/notificaciones/test_settings_rules.py` | 6 | Umbral, destinatarios, segregación, preferencias, canales |
| Unitaria | `tests/unit/recomendaciones/test_creation_rules.py` | 7 | Estado inicial y auditoría, plazo no positivo, unicidad por informe, informe/unidad inexistentes sin crear nada |
| Unitaria | `tests/unit/recomendaciones/test_state_machine_spec.py` | 19 | Estados y transiciones exactos, cumplida, vencimiento, fechas de hito |
| Unitaria | `tests/unit/test_mvp.py` | 5 | PDF y hash, transición a revisión, salto ilegal, carga en otra unidad, envoltura |
| Unitaria | `tests/unit/usuarios/test_identity_rules.py` | 32 | RBAC parametrizado por rol y endpoint, auditoría solo UAI/CGE, token de cuenta desactivada o con rol cambiado |
| Unitaria | `tests/unit/usuarios/test_sso_jwt.py` | 2 | Emisión y rechazo de JWT |

## Inventario de pruebas del frontend

| Archivo | Pruebas | Qué verifica |
|---|---|---|
| `src/App.test.tsx` | 3 | Tablero ejecutivo para Rectorado, KPIs para el resto, página de entrada por rol |
| `src/features/evidencias/components/EvidenceUpload.test.tsx` | 3 | Rechazo de no-PDF y de archivos > 30 MB; muestra el hash tras una carga exitosa |
| `src/features/evidencias/pages/ReviewEvidencePage.test.tsx` | 3 | Dictamen de aprobación y rechazo con observaciones |
| `src/features/administracion/pages/UserAdminPage.test.tsx` | 3 | Lista cuentas y unidades, envía solo cambios de rol/unidad, registra una unidad |
| `tests/e2e/recommendation-flow.spec.ts` (Playwright) | 1 | "Recorre las vistas de cada rol sin errores" con API simulada (`mockApi`) |

## Comandos

```bash
# Backend (desde backend/, con .venv activo)
python manage.py check
python -m pytest -q

# Frontend (desde frontend/)
npm test
npm run lint
npm run build
npx playwright install chromium   # una vez
npm run test:e2e
```
