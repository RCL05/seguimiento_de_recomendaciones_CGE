## Mecanismos implementados

| Mecanismo | Implementación verificada | Uso operativo |
|---|---|---|
| Health check | `GET /health/` → `{"success": true, "data": {"status": "ok"}}`, sin autenticación | Sonda de Compose (`healthcheck` del servicio `backend`) y de balanceadores |
| Correlación de peticiones | `meta.request_id` en cada respuesta; acepta `X-Request-ID` entrante; se guarda en `AuditLog.request_id` | Relacionar una queja de usuario con el evento de auditoría |
| Auditoría | `AuditLog` inmutable con actor, IP, módulo, acción, entidad, estados y resultado; consulta en `GET /api/v1/auditoria` y en la SPA (`/auditoria`) | Investigación de incidentes y rendición de cuentas |
| Accesos denegados | Evento `ACCESS_DENIED` al intentar acceder a recursos de otra unidad | Detección de abuso |
| Manejo de excepciones | `handle_exception` + `ApiErrorEnvelopeMiddleware`: errores 4xx/5xx con envoltura y sin trazas | El cliente recibe un código estable; el detalle queda en el servidor |
| Logging | `logging.getLogger(__name__)` en jobs (`scheduled_jobs`, `send_deadline_alerts`, `mark_overdue`) y en el manejador de excepciones | Resumen de cada evaluación de plazos |
| Job de plazos | `manage.py evaluar_plazos` imprime un JSON con `evaluated_at`, `alertas_vencimiento`, `mora`, `status` | Verificar ejecución del programador |
| Estado de notificaciones | `Notificacion.estado` (`PENDIENTE`/`ENVIADA`/`FALLIDA`) e `intentos` | Detectar problemas de SMTP |
| Integridad de evidencias | `GET /api/v1/evidencias/{id}/integridad` | Verificación periódica o por auditoría |

## Mecanismos no implementados (recomendaciones)

| Necesidad | Situación | Recomendación |
|---|---|---|
| Métricas y monitoreo | No hay métricas ni APM | Exponer métricas (p. ej. `django-prometheus`) y alertar sobre 5xx, `ACCESS_DENIED` y `FALLIDA` |
| Logging centralizado | `LOGGING` escribe a consola con nivel configurable; no hay agregador | Enviar los logs a un colector con `request_id` |
| Respaldos | No hay scripts ni política | `pg_dump` diario cifrado + copia del volumen `backend_media`; prueba de restauración trimestral |
| Verificación masiva de integridad | Solo por evidencia | Comando de gestión que recorra todas las evidencias y reporte discrepancias |
| Rotación de secretos | No documentada en código | Procedimiento con la DTI; la rotación de `JWT_SIGNING_KEY` invalida sesiones activas (1 h) |

## Diagnóstico rápido

| Pregunta | Cómo responderla |
|---|---|
| ¿La API está viva? | `curl http://<host>:8000/health/` |
| ¿Por qué falló una operación? | Buscar el `meta.request_id` de la respuesta en `GET /api/v1/auditoria` o en los logs |
| ¿Se ejecutó el job? | Logs del servicio `scheduler` (`docker compose logs scheduler`) o salida JSON del comando |
| ¿Se entregan los correos? | Contar `notificaciones` con estado `FALLIDA` |
| ¿Una evidencia fue alterada? | `GET /api/v1/evidencias/{id}/integridad` → `integra` |

## Mantenimiento

### Flujo para cambios funcionales (definido en `docs/README.md`)

1. Actualizar la especificación (`specs/001-…/spec.md`).
2. Actualizar la tarea (`tasks.md`).
3. Implementar código y pruebas.
4. Actualizar la trazabilidad.
5. Actualizar la documentación afectada (este portal: el archivo fuente en `DOCUMENTACION/`).

### Tareas periódicas

| Tarea | Comando |
|---|---|
| Aplicar migraciones | `python manage.py migrate` (con respaldo previo) |
| Detectar migraciones pendientes | `python manage.py makemigrations --check --dry-run` |
| Regenerar el contrato tras cambiar endpoints | `python manage.py spectacular --file contracts/openapi.yaml` y copiar a `specs/…/contracts/` |
| Actualizar dependencias | Revisar `requirements.txt` y `package.json`; ejecutar la suite completa |
| Auditar dependencias | `pip-audit`, `npm audit` (no configurados en CI) |
| Reconstruir el portal | `quarto render docs` (automático en GitHub Actions) |

### Reglas de operación

- No modificar ni borrar registros de `audit_logs` ni archivos de `MEDIA_ROOT` directamente.
- Las evidencias se anulan, no se eliminan.
- Respaldar base de datos y archivos **juntos**: los hashes de `evidencias` solo son verificables con el archivo correspondiente.
