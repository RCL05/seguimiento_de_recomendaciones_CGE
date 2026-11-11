## Procesos identificados

SITRA-CGE es un sistema de **gestión de un flujo de trabajo institucional** con actores, decisiones y plazos, por lo que BPMN aporta valor. Se modelaron los tres procesos que explican el funcionamiento del sistema:

| ID | Proceso | Disparador | Participantes | Fuente BPMN |
|---|---|---|---|---|
| P1 | Registro de informe y asignación de recomendaciones | Recepción de un informe CGE | UAI, Sistema | `DIAGRAMAS/P1_registro_asignacion.bpmn` |
| P2 | Ejecución, evidencia y dictamen | Recomendación en `PENDIENTE` o `REABIERTA` | Ejecutor, Sistema, UAI | `DIAGRAMAS/P2_ejecucion_validacion.bpmn` |
| P3 | Evaluación periódica de plazos | Temporizador (cada `SCHEDULER_INTERVAL_SECONDS`) | Programador, Sistema, SMTP | `DIAGRAMAS/P3_evaluacion_plazos.bpmn` |

Procesos **no modelados** con BPMN, por ser operaciones CRUD de un solo paso sin decisiones de negocio: administración de usuarios/unidades, preferencias de notificación y consultas (tablero, matriz, auditoría). Se describen en los capítulos de componentes y API.

Las fuentes `.bpmn` siguen BPMN 2.0 (espacio de nombres OMG `20100524`, compatible con BPMN 2.0.2), incluyen semántica y disposición gráfica (BPMN DI) y pueden editarse con [bpmn.io](https://demo.bpmn.io) o Camunda Modeler. En el portal, cada diagrama se dibuja en el navegador directamente desde su archivo `.bpmn` con el visor `bpmn-js` (se puede desplazar y ampliar).

## Ciclo de vida de una recomendación

Implementado en `backend/modules/recomendaciones/domain/state_machine.py` (`ALLOWED_TRANSITIONS`). Toda transición no listada responde **HTTP 409 `CONFLICT`**.

```{mermaid}
stateDiagram-v2
  direction LR
  [*] --> PENDIENTE: UAI registra
  PENDIENTE --> EN_PROCESO: Ejecutor registra primer hito
  REABIERTA --> EN_PROCESO: Ejecutor registra hito
  EN_PROCESO --> EN_VALIDACION: Ejecutor carga PDF válido
  EN_VALIDACION --> CUMPLIDA: UAI aprueba (revisión + evidencia validada)
  EN_VALIDACION --> EN_PROCESO: UAI rechaza con observaciones
  CUMPLIDA --> REABIERTA: UAI reabre con motivo
```

"Vencida" **no es un estado**: es un indicador calculado (`domain/vencimiento.py`) que acompaña a cualquier estado distinto de `CUMPLIDA`.

## P1 — Registro de informe y asignación

::: {#fig-bpmn-p1 .bpmn-diagram data-src="../assets/diagrams/src/P1_registro_asignacion.bpmn"}
P1 — Registro y asignación (BPMN). Fuente editable: [`P1_registro_asignacion.bpmn`](../assets/diagrams/src/P1_registro_asignacion.bpmn) (copia de `DOCUMENTACION/02_PROCESOS/DIAGRAMAS/P1_registro_asignacion.bpmn`).
:::

| Elemento | Descripción |
|---|---|
| Objetivo | Dejar constancia oficial del informe y de cada recomendación con responsable, prioridad y plazo |
| Participantes | UAI (registra), Sistema (valida, audita) |
| Entradas | Número de informe, período auditado, fecha de notificación, PDF o URL del informe; por recomendación: número, descripción, unidad, `legal_days`, `due_date`, prioridad |
| Actividades | 1) `POST /api/v1/informes`; 2) validación y unicidad de `numero_informe`; 3) `POST /api/v1/recomendaciones`; 4) validación de campos, existencia de informe y unidad, unicidad `(informe, numero_recomendacion)`; 5) auditoría |
| Decisiones | ¿Informe válido? ¿Recomendación válida? |
| Excepciones | 400 `VALIDATION_ERROR` (campos), 409 `CONFLICT` (duplicado), 409 `BUSINESS_RULE_VIOLATION` (informe o unidad inexistente, H-24), 413 (PDF del informe demasiado grande), 403 si el rol no es UAI |
| Resultado | Recomendación en `PENDIENTE` visible para la unidad responsable |
| Código | `informes_cge/application/register_informe.py`, `recomendaciones/application/create_recomendacion.py` |

## P2 — Ejecución, evidencia y dictamen

::: {#fig-bpmn-p2 .bpmn-diagram data-src="../assets/diagrams/src/P2_ejecucion_validacion.bpmn"}
P2 — Ejecución y validación (BPMN). Fuente editable: [`P2_ejecucion_validacion.bpmn`](../assets/diagrams/src/P2_ejecucion_validacion.bpmn) (copia de `DOCUMENTACION/02_PROCESOS/DIAGRAMAS/P2_ejecucion_validacion.bpmn`).
:::

| Elemento | Descripción |
|---|---|
| Objetivo | Que la unidad demuestre el cumplimiento y que solo la UAI lo declare |
| Participantes | Ejecutor de la unidad responsable, Sistema, UAI |
| Entradas | Hito (`descripcion_hito`, `fecha_compromiso`), PDF binario (cabeceras `X-Filename`, `X-Evidence-Type`), dictamen (`evidence_id`, `approved`, `observaciones`) |
| Actividades | 1) `POST …/plan-accion`; 2) validar fecha (dentro del plazo o desde hoy si venció); 3) `POST …/evidencias` en flujo continuo; 4) validar extensión, firma `%PDF-`, tamaño ≤ 30 MB y unidad; 5) guardar archivo con nombre opaco y SHA-256; 6) `POST …/dictamenes` |
| Decisiones | ¿Fecha válida? ¿PDF válido? ¿Dictamen aprobado o rechazado? |
| Información utilizada | Estado actual, `fecha_vencimiento_legal`, unidad del actor, historial de revisión, evidencia vigente |
| Excepciones | 400 (fecha inválida, sin plan previo, no es PDF, rechazo sin observaciones), 404 (otra unidad o inexistente; se audita el intento), 409 (estado no admite la operación o doble dictamen), 413 (PDF > 30 MB), 403 (rol) |
| Concurrencia | Cada paso bloquea la recomendación con `select_for_update` dentro de `transaction.atomic` |
| Resultado | `CUMPLIDA` con dictamen aprobado y evidencia `validada=True`, o regreso a `EN_PROCESO` con observaciones |
| Código | `create_plan_accion.py`, `upload_evidencia.py`, `issue_dictamen.py` |

Variantes: la UAI puede **anular** lógicamente una evidencia (`PATCH /evidencias/{id}`, la evidencia pasa a `ANULADA` sin borrarse) y **reabrir** una recomendación cumplida (`PATCH /recomendaciones/{id}` con estado `REABIERTA` y motivo), lo que reinicia P2.

## P3 — Evaluación periódica de plazos

::: {#fig-bpmn-p3 .bpmn-diagram data-src="../assets/diagrams/src/P3_evaluacion_plazos.bpmn"}
P3 — Evaluación de plazos (BPMN). Fuente editable: [`P3_evaluacion_plazos.bpmn`](../assets/diagrams/src/P3_evaluacion_plazos.bpmn) (copia de `DOCUMENTACION/02_PROCESOS/DIAGRAMAS/P3_evaluacion_plazos.bpmn`).
:::

| Elemento | Descripción |
|---|---|
| Objetivo | Avisar antes del vencimiento y registrar una sola vez los vencimientos |
| Participantes | Programador (servicio `scheduler` de Compose o cron), Sistema, SMTP |
| Entradas | `ConfiguracionNotificacion` (umbral, canales, destinatarios), preferencias por usuario, recomendaciones y evidencias |
| Actividades | 1) `manage.py evaluar_plazos` o `POST /api/v1/evaluaciones-plazos` (solo DTI); 2) `send_deadline_alerts`; 3) `mark_overdue_recommendations`; 4) `deliver_pending_notifications`; 5) log de resumen |
| Decisiones | ¿Faltan ≤ umbral días sin evidencia presentada? ¿Está vencida sin entrega oportuna pendiente? ¿Ya se registró el vencimiento en este ciclo? |
| Excepciones | Fallo SMTP → notificación `FALLIDA`; no revierte la alerta interna ni el registro de vencimiento; se reintenta en cada ejecución hasta 3 intentos |
| Idempotencia | `Notificacion.clave_idempotencia` única y `Recomendacion.vencimiento_registrado_en` |
| Resultado | Alertas en la bandeja interna, correos entregados o fallidos, vencimientos registrados sin cambio de estado |
| Código | `notificaciones/infrastructure/scheduled_jobs.py`, `application/send_deadline_alerts.py`, `application/mark_overdue.py`, `application/service.py` |
