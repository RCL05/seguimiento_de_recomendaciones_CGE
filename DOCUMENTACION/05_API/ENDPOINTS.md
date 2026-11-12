## Catálogo de operaciones

Generado a partir de `backend/contracts/openapi.yaml` (31 operaciones) y contrastado con las vistas y casos de uso. La columna *Roles* refleja **lo que el código hace**, no solo lo que declara el contrato. Todas las rutas llevan el prefijo `/api/v1` salvo `/health/`.

| Método | Ruta | operationId | Roles (verificado) | Códigos documentados |
|---|---|---|---|---|
| GET | `/health/` | `verificarSalud` | Público | 200 |
| POST | `/sesiones` | `iniciarSesionSso` | Público | 200, 400, 401 |
| GET | `/unidades` | `listarUnidades` | UAI, DTI | 200, 401, 403 |
| POST | `/unidades` | `registrarUnidad` | DTI | 201, 400, 401, 403 |
| GET | `/usuarios` | `listarUsuarios` | DTI | 200, 401, 403 |
| PATCH | `/usuarios/{usuario_id}` | `actualizarUsuario` | DTI | 200, 400, 401, 403, 404 |
| GET | `/informes` | `listarInformes` | UAI, RECTORADO, CGE_AUDITOR | 200, 400, 401, 403 |
| POST | `/informes` | `registrarInforme` | UAI | 201, 400, 401, 403, 409, 413 |
| GET | `/informes/{informe_id}` | `consultarInforme` | UAI, RECTORADO, CGE_AUDITOR | 200, 401, 403, 404 |
| GET | `/informes/{informe_id}/documento` | `descargarDocumentoInforme` | UAI, RECTORADO, CGE_AUDITOR | 200, 401, 403, 404 |
| GET | `/recomendaciones` | `listarRecomendaciones` | EJECUTOR (solo su unidad), UAI, RECTORADO, CGE_AUDITOR | 200, 400, 401, 403 |
| POST | `/recomendaciones` | `registrarRecomendacion` | UAI | 201, 400, 401, 403, 409 |
| GET | `/recomendaciones/{recommendation_id}` | `consultarRecomendacion` | EJECUTOR (su unidad; si no, 404), UAI, RECTORADO, CGE_AUDITOR | 200, 401, 403, 404 |
| PATCH | `/recomendaciones/{recommendation_id}` | `modificarRecomendacion` | UAI | 200, 400, 401, 403, 404, 409 |
| GET | `/recomendaciones/{recommendation_id}/hitos` | `listarHitos` | Mismos que `consultarRecomendacion` (EJECUTOR de su unidad, UAI, RECTORADO, CGE_AUDITOR) | 200, 401, 403, 404 |
| POST | `/recomendaciones/{recommendation_id}/hitos` | `registrarHito` | EJECUTOR (su unidad) | 201, 400, 401, 403, 404, 409 |
| POST | `/recomendaciones/{recommendation_id}/evidencias` | `cargarEvidencia` | EJECUTOR (su unidad) | 201, 400, 401, 403, 404, 409, 413 |
| POST | `/recomendaciones/{recommendation_id}/dictamenes` | `emitirDictamen` | UAI | 201 (`Location` al dictamen), 400, 401, 403, 404, 409 |
| GET | `/recomendaciones/{recommendation_id}/dictamenes/{dictamen_id}` | `consultarDictamen` | Mismos que `consultarRecomendacion` (EJECUTOR de su unidad; si no, 404) | 200, 401, 403, 404 |
| PATCH | `/evidencias/{evidence_id}` | `anularEvidencia` | UAI | 200, 400, 401, 403, 404, 409 |
| GET | `/evidencias/{evidence_id}/archivo` | `descargarEvidencia` | UAI; EJECUTOR de la misma unidad (no anuladas) | 200, 400, 401, 403, 404 |
| GET | `/evidencias/{evidence_id}/integridad` | `verificarIntegridadEvidencia` | UAI, CGE_AUDITOR | 200, 401, 403, 404 |
| GET | `/notificaciones` | `consultarBandeja` | Cualquier autenticado (solo sus notificaciones) | 200, 401 |
| GET | `/notificaciones/preferencias` | `consultarPreferencias` | Propio usuario; DTI para otros (`usuario_id`) | 200, 401, 403, 404 |
| PUT | `/notificaciones/preferencias` | `actualizarPreferencias` | Propio usuario; DTI para otros | 200, 400, 401, 403, 404 |
| GET | `/notificaciones/configuracion` | `consultarConfiguracionNotificaciones` | DTI | 200, 401, 403 |
| PUT | `/notificaciones/configuracion` | `actualizarConfiguracionNotificaciones` | DTI | 200, 400, 401, 403 |
| GET | `/dashboard/kpis` | `consultarKpisDashboard` | **Cualquier autenticado** (sin restricción de rol; el EJECUTOR solo ve los datos de su unidad; H-14 parcial) | 200, 401, 403 |
| GET | `/reportes/tablero` | `consultarTablero` | RECTORADO, UAI, CGE_AUDITOR | 200, 401, 403 |
| GET | `/reportes/matriz-cge` | `exportarMatrizCge` | UAI, RECTORADO, CGE_AUDITOR | 200 (`text/csv`), 401, 403 |
| GET | `/auditoria` | `consultarAuditoria` | UAI, CGE_AUDITOR | 200, 400, 401, 403 |

Todas las operaciones protegidas documentan además `500` y el esquema `bearerAuth` (verificado por `test_operaciones_protegidas_declaran_bearer_y_401`).

## Solicitudes principales

| Operación | Cuerpo / parámetros | Validaciones |
|---|---|---|
| `iniciarSesionSso` | `{"credential": "…"}` | Credencial no vacía; identidad activa con rol válido |
| `registrarInforme` | `numero_informe` (≤ 100), `periodo_auditado` (≤ 100), `fecha_notificacion` (fecha), `pdf_informe_url` (URL opcional) o `pdf_informe` (archivo, `multipart/form-data`) | Número único; PDF ≤ 30 MB |
| `registrarRecomendacion` | `report_id` (UUID), `number` (≤ 50), `description`, `unit_id` (código de unidad), `legal_days` (≥ 1), `due_date` (fecha), `priority` (`ALTA`/`MEDIA`/`BAJA`, por defecto `MEDIA`) | Informe y unidad existentes (si no, 400 con `errors.fields.report_id` o `unit_id`); `(informe, número)` único (si no, 409) |
| `listarRecomendaciones` | `page`, `page_size`, `state`, `unit_id`, `priority`, `due_date`, `due_before`, `due_after`, `vencida` | Ejecutor limitado a su unidad |
| `modificarRecomendacion` (reapertura) | `{"estado": "REABIERTA", "motivo": "…"}` (motivo ≤ 1000) | Solo desde `CUMPLIDA` |
| `modificarRecomendacion` (reasignación) | `{"unit_id": "DEP-B", "motivo": "…"}` (motivo ≤ 1000) | La unidad existe y es distinta de la actual; el estado no cambia |
| `registrarHito` | `descripcion_hito`, `fecha_compromiso` | Estado `PENDIENTE`, `REABIERTA` o `EN_PROCESO`; fecha según RN-07 |
| `cargarEvidencia` | Cuerpo binario PDF; cabeceras `X-Filename` (obligatoria) y `X-Evidence-Type` (`BORRADOR`/`FINAL`) | Estado `EN_PROCESO` (cualquier otro, incluido `PENDIENTE` sin plan, responde 409); extensión `.pdf`; firma `%PDF-`; `Content-Length` y tamaño real ≤ 30 MB |
| `emitirDictamen` | `evidence_id` (UUID), `approved` (bool), `observaciones` | Estado `EN_VALIDACION`; evidencia vigente de la recomendación; observaciones obligatorias si `approved=false` |
| `anularEvidencia` | `estado` (`ANULADA`), `motivo` (≤ 500) | Solo UAI |
| `descargarEvidencia` | `disposition` = `inline` (defecto) o `attachment` | Autorización por rol y unidad |
| `actualizarConfiguracionNotificaciones` | `umbral_dias`, `notificaciones_activas`, `canal_interno_activo`, `canal_email_activo`, `destinatarios_vencimiento[]`, `destinatarios_mora[]` (todos opcionales) | Umbral 1–90; destinatarios ∈ roles; rechaza claves con aspecto de secreto |
| `actualizarPreferencias` | `usuario_id` (opcional), `preferencias[]` con `tipo_alerta`, `notificar_interno`, `notificar_email`, `activo` | `tipo_alerta` ∈ {`ALERTA_VENCIMIENTO`, `EN_MORA`} |
| `consultarAuditoria` | `entity`, `entity_id`, `limit` | `limit` inválido → 400 |

## Respuestas principales

| Operación | `data` |
|---|---|
| `iniciarSesionSso` | `access_token`, `token_type: "Bearer"`, `expires_in: 3600`, `user_id`, `email`, `display_name`, `role`, `unit_id` |
| Recomendación | `id`, `report_id`, `number`, `description`, `unit_id`, `legal_days`, `due_date`, `priority`, `state`, `vencida`, `overdue_registered_at` (+ `evidencias` en el detalle) |
| Evidencia | `id`, `recommendation_id`, `filename`, `mime_type`, `size_bytes`, `sha256`, `uploaded_at`, `validated`, `type`, `status`, `file_url` |
| Integridad | `evidence_id`, `integra` (bool) |
| Tablero | `total`, `cumplimiento_porcentaje`, `semaforo_riesgo` (`VERDE`/`AMARILLO`/`ROJO`), `en_mora`, `en_revision_interna`, `por_estado`, `unidades_en_mora[]`, `fecha_corte` |
| KPIs | `total_recomendaciones`, `recomendaciones_por_estado` (4 estados, sin `REABIERTA`), `tasa_cumplimiento_porcentaje`, `recomendaciones_vencidas_o_en_mora`, … |
| Evaluación de plazos | `evaluated_at`, `alertas_vencimiento {scheduled, skipped, delivered}`, `mora {…}`, `status: "ok"` |
| Matriz | CSV con BOM: `numero_informe, numero_recomendacion, descripcion, unidad_responsable, prioridad, estado, plazo_legal_dias, fecha_vencimiento_legal, vencida (SI/NO), vencimiento_registrado_en` |

El esquema completo de cada respuesta (76 componentes) está en el contrato y en Swagger UI.
