## Dos tipos de decisiones

1. **Decisiones históricas verificadas** (ADR-0001…ADR-0011): tomadas por el equipo y registradas en `docs/adr/`. Su texto completo no se reescribe; aquí se resumen y se **contrastan con el código**.
2. **Recomendaciones de la auditoría** (ADR-R01…): propuestas formuladas durante esta documentación. Su estado es *Propuesto* y no han sido aceptadas por el equipo.

## Decisiones históricas

| ADR | Decisión | Estado declarado | Contraste con la implementación (2026-11-11) |
|---|---|---|---|
| [ADR-0001](https://github.com/RCL05/seguimiento_de_recomendaciones_CGE/blob/main/docs/adr/ADR-0001-arquitectura-capas-monolito-modular.md) | Cuatro capas + monolito modular | Aceptado | **Cumplido**: `presentation/application/domain/infrastructure` por módulo. Desviaciones menores en *Arquitectura general* |
| [ADR-0002](https://github.com/RCL05/seguimiento_de_recomendaciones_CGE/blob/main/docs/adr/ADR-0002-autenticacion-jwt-rbac.md) | JWT con identidad, rol y unidad; RBAC por endpoint y por recurso | Aceptado | **Cumplido**: `JWTBearerAuthentication`, `require_roles`, autorización de objeto en casos de uso |
| [ADR-0003](https://github.com/RCL05/seguimiento_de_recomendaciones_CGE/blob/main/docs/adr/ADR-0003-motor-base-datos-relacional.md) | Base de datos relacional; motor por confirmar | Propuesto | **Implementado de hecho**: SQLite (dev) y PostgreSQL 16 (Compose). El estado del ADR no se actualizó (H-23) |
| [ADR-0004](https://github.com/RCL05/seguimiento_de_recomendaciones_CGE/blob/main/docs/adr/ADR-0004-control-concurrencia.md) | Optimista (columna de versión) por defecto + pesimista en transiciones críticas | Aceptado | **Parcial**: solo bloqueo pesimista (`select_for_update`); no existe columna de versión (H-02) |
| [ADR-0005](https://github.com/RCL05/seguimiento_de_recomendaciones_CGE/blob/main/docs/adr/ADR-0005-almacenamiento-evidencias.md) | Metadatos en BD, archivo en almacenamiento controlado tras un puerto | Aceptado | **Cumplido** con volumen local; el adaptador de objetos (S3) no existe (H-04) |
| [ADR-0006](https://github.com/RCL05/seguimiento_de_recomendaciones_CGE/blob/main/docs/adr/ADR-0006-historial-auditoria-inmutable.md) | Bitácora append-only; revocar UPDATE/DELETE en BD | Aceptado | **Parcial**: inmutabilidad en el ORM (`save`, `delete`, QuerySet); no hay revocación de permisos en la base de datos |
| [ADR-0007](https://github.com/RCL05/seguimiento_de_recomendaciones_CGE/blob/main/docs/adr/ADR-0007-contrato-universal-respuestas.md) | Envoltura `success/message/data/errors/meta` | Aceptado | **Cumplido** y verificado por pruebas de contrato |
| [ADR-0008](https://github.com/RCL05/seguimiento_de_recomendaciones_CGE/blob/main/docs/adr/ADR-0008-docker-configuracion-entornos.md) | Docker + Compose; configuración por variables | Aceptado | **Cumplido** para desarrollo; Gunicorn en el contenedor, falta proxy TLS (H-22) |
| [ADR-0009](https://github.com/RCL05/seguimiento_de_recomendaciones_CGE/blob/main/docs/adr/ADR-0009-ci-gitflow.md) | GitFlow + CI con análisis, pruebas y verificación del contrato | Aceptado | **Cumplido**: ramas `main`, `develop`, `feature/*`; `ci.yml` ejecuta check, pytest (incluye contrato), lint, Vitest y build |
| [ADR-0010](https://github.com/RCL05/seguimiento_de_recomendaciones_CGE/blob/main/docs/adr/ADR-0010-django-admin-mvp-fase1.md) | Django Admin como MVP interno (excepción arquitectónica) | Aceptado | **Superado**: la API REST y la SPA ya existen; `admin.py` se conserva en `usuarios`, `recomendaciones` y `core/audit` |
| [ADR-0011](https://github.com/RCL05/seguimiento_de_recomendaciones_CGE/blob/main/docs/adr/ADR-0011-evidencias-pdf-supuestos.md) | Evidencias solo PDF, firma `%PDF-`, tipo BORRADOR/FINAL, anulación lógica, SHA-256, nombre UUID | Aceptado (supuestos) | **Cumplido** salvo el tamaño: el ADR fija 10 MB y la clarificación del 2026-10-20 y el código usan **30 MB** |

### Decisiones posteriores registradas fuera de ADR

Las clarificaciones del 2026-11-05 en `spec.md` constituyen decisiones de diseño que no tienen ADR propio:

| Decisión | Implementación |
|---|---|
| "Vencida" es indicador calculado, no estado | `domain/vencimiento.py`, migración `0007_vencimiento_como_indicador` |
| Catálogo simplificado a 5 estados | `Recomendacion.Estado`, migración `0004_alter_recomendacion_estado` |
| Reapertura solo por UAI con motivo | `reabrir_recomendacion.py` |
| Con plazo vencido, hitos desde hoy sin modificar el plazo legal | `fecha_compromiso_valida` |

## Recomendaciones de la auditoría

### ADR-R01 — Formalizar el bloqueo pesimista como mecanismo único de concurrencia

- **Estado**: Propuesto.
- **Contexto**: ADR-0004 prescribe control optimista, pero el código solo usa `select_for_update`.
- **Problema**: la documentación promete un comportamiento (409 por versión) que no existe.
- **Opciones**: (a) añadir campo `version` y verificarlo en `PATCH`; (b) aceptar el bloqueo pesimista como único mecanismo.
- **Decisión propuesta**: (b), ya que todas las mutaciones de estado pasan por casos de uso transaccionales y la prueba `test_concurrencia_dictamen_con_select_for_update` lo cubre.
- **Consecuencias**: actualizar ADR-0004 y `docs/architecture/sitra-cge.md`; en SQLite el bloqueo de fila no existe (se serializa a nivel de base de datos), por lo que la prueba de concurrencia debe ejecutarse también contra PostgreSQL.

### ADR-R02 — Inmutabilidad de la bitácora a nivel de base de datos

- **Estado**: Propuesto.
- **Contexto**: ADR-0006 exige revocar `UPDATE/DELETE`; hoy solo el ORM lo impide.
- **Problema**: una sentencia SQL directa o `QuerySet.raw` podría alterar `audit_logs`.
- **Opciones**: (a) `REVOKE UPDATE, DELETE ON audit_logs` para el usuario de aplicación en PostgreSQL; (b) disparador que rechace la operación; (c) mantener solo el ORM.
- **Decisión propuesta**: (a) + (b) en PostgreSQL mediante una migración condicionada al motor.
- **Consecuencias**: el despliegue debe usar un usuario distinto del propietario de las tablas.

### ADR-R03 — Perfil de despliegue productivo

- **Estado**: Aceptado parcialmente.
- **Contexto**: el `Dockerfile` usaba `runserver` y `DEBUG` era `true` por defecto (H-10, H-22).
- **Opciones**: (a) Gunicorn/Uvicorn detrás de Nginx con TLS; (b) plataforma gestionada.
- **Decisión**: (a). El contenedor ya usa Gunicorn y `DEBUG` es `false` por defecto con hosts locales; falta el proxy TLS, el build estático del frontend y `manage.py check --deploy` en CI.
- **Consecuencias**: completar el perfil de producción con proxy y Compose separado.

### ADR-R04 — Reintento acotado de notificaciones por correo

- **Estado**: Aceptado e implementado.
- **Contexto**: RNF-007 exige reintento; las notificaciones `FALLIDA` no volvían a procesarse (H-05).
- **Decisión**: reintentar en cada ejecución del programador las `PENDIENTE` o `FALLIDA` con `intentos < 3`, conservando la idempotencia por `clave_idempotencia`.
- **Consecuencias**: `deliver_pending_notifications` reintenta hasta 3 intentos; cubierto por `test_delivery_retries.py`.
