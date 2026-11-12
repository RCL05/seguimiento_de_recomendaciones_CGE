## Problema

El seguimiento de las recomendaciones de la CGE en la UNL era **manual y disperso** (`docs/problem-definition.md`, `spec.md`). Esto dificulta responder con certeza a cuatro preguntas:

1. ¿Qué recomendaciones siguen pendientes?
2. ¿Qué unidad es responsable de cada una y cuál es su plazo legal?
3. ¿Qué evidencia existe y si es íntegra?
4. ¿La UAI aprobó formalmente su cumplimiento?

## Riesgo crítico

El riesgo principal identificado por el equipo es de **lógica de negocio y cumplimiento normativo**: que el sistema dé por *cumplida* una recomendación que normativamente sigue pendiente o rechazada. Si el flujo de estados no se alinea con la validación de la UAI y con el Acuerdo No. 010-CG-2022 de la CGE, la información institucional reportada sería incorrecta.

Riesgos adicionales declarados: adopción del sistema por las unidades y seguridad de los documentos PDF cargados.

## Justificación

| Necesidad | Respuesta del sistema | Evidencia en código |
|---|---|---|
| Registro formal con responsable y plazo | Informes y recomendaciones con unidad responsable, prioridad, plazo y fecha de vencimiento calculada | `create_recomendacion.py` |
| Evitar cumplimientos sin sustento | Máquina de estados que solo permite `CUMPLIDA` con revisión interna y evidencia validada por la UAI | `domain/state_machine.py` |
| Integridad de la evidencia | PDF con huella SHA-256 y verificación posterior | `verify_integrity.py` |
| Trazabilidad para auditoría externa | Bitácora inmutable de toda operación mutativa | `core/audit/models.py` |
| Supervisión oportuna | Alertas de vencimiento, indicador de vencida y tablero con semáforo | `send_deadline_alerts.py`, `get_dashboard.py` |
| Reporte a la CGE | Matriz de cumplimiento en CSV UTF-8 | `export_matriz.py` |
| Segregación de funciones | RBAC con cinco roles y aislamiento por unidad | `core/auth/permissions.py`, casos de uso |

## Restricciones del problema

- La interpretación legal corresponde a la UNL y a la CGE; el sistema no sustituye el dictamen de la UAI.
- No existe integración con los sistemas de la CGE: el intercambio se limita a la exportación de la matriz.
- Fechas de negocio en `America/Guayaquil`; auditoría en UTC.
