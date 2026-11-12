## Objetivo general

Proveer a la UNL una plataforma que registre las recomendaciones de la CGE con responsable y plazo, respalde su cumplimiento con evidencias PDF íntegras, lo valide mediante dictamen de la UAI y mantenga una trazabilidad consultable y exportable (`spec.md`, objetivo del incremento Unidad 1).

## Objetivos específicos

| ID | Objetivo | Requisitos | Estado |
|---|---|---|---|
| OE-1 | Registrar informes CGE y recomendaciones asignadas a una unidad con plazo legal | RF-005, RF-006 | Implementado y probado |
| OE-2 | Permitir a las unidades planificar hitos y cargar evidencias PDF verificables | RF-007, RF-008 | Implementado y probado |
| OE-3 | Garantizar que solo la UAI declare el cumplimiento, con evidencia validada | RF-009, RF-010, RF-023 | Implementado y probado |
| OE-4 | Alertar vencimientos próximos y registrar vencimientos sin alterar el estado | RF-011, RF-012, RF-021 | Implementado; reintento SMTP acotado (máx. 3 intentos) |
| OE-5 | Ofrecer al Rectorado un tablero de riesgo y unidades en mora | RF-013 | Implementado; rendimiento medido con pruebas automatizadas |
| OE-6 | Exportar la matriz de cumplimiento y consultar la auditoría | RF-014, RF-017, RF-018 | Implementado; conformidad normativa por validar (H-09) |
| OE-7 | Administrar identidad, roles, unidades y notificaciones | RF-001, RF-002, RF-004 | Implementado; SSO productivo por definir |

## Alcance

**Incluido** (verificado en el código):

- Informes CGE con documento oficial (PDF o URL).
- Recomendaciones con prioridad (`ALTA`, `MEDIA`, `BAJA`), plazo en días y fecha de vencimiento legal.
- Plan de acción con N hitos.
- Evidencias PDF (borrador/final), anulación lógica, descarga autorizada y verificación de integridad.
- Dictamen UAI (aprobado/rechazado con observaciones) y reapertura con motivo.
- Indicador de vencimiento, alertas internas y por correo, comando programado.
- KPIs, tablero ejecutivo con semáforo, matriz CSV.
- Bitácora de auditoría inmutable y su consulta.
- Administración de usuarios, roles, unidades, preferencias y configuración de notificaciones.

**Fuera de alcance** (`spec.md`):

- Sincronización en tiempo real con sistemas de la CGE.
- Gestión de responsabilidades penales o judiciales.
- Interpretación automática de normas o sustitución del dictamen UAI.
- Exportación oficial en Excel o PDF (solo CSV hasta contar con plantilla institucional).
- Aplicación móvil (fase F3 mencionada en ADR-0001, no iniciada).

## Limitaciones conocidas

| Limitación | Referencia |
|---|---|
| El mecanismo SSO de producción no está definido por la DTI | `spec.md`, preguntas pendientes |
| Sin escaneo antimalware de PDF | H-03 |
| Almacenamiento de archivos solo local (sin S3) | H-04 |
| Sin proxy TLS ni automatización completa de despliegue | H-22 |
