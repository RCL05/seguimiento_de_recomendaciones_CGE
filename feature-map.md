# Feature Map

## 1. Propósito

Este documento identifica y organiza las capacidades funcionales del backend del Sistema de Seguimiento de Recomendaciones de la CGE con base exclusivamente en la evidencia existente del proyecto. Sirve como insumo para determinar cuántas especificaciones (`spec.md`) se justifican, qué features se priorizan y cuáles pertenecen al alcance del incremento actual versus incrementos posteriores.

Fuentes analizadas: `.specify/memory/constitution.md` (v1.0.0), `.spec/specify.md` (Borrador), `.spec/clarify.md`, `.spec/plan.md` (Borrador), `.spec/tasks.md` (45 tareas), `docs/adr/ADR-0001` a `ADR-0009`, `docs/problem-definition.md`, `docs/control-questions.md`, `README.md` y el `feature-map.md` previo. No existen todavía carpetas `specs/*/spec.md`; la especificación funcional vive en `.spec/specify.md`.

**Relación con el mapa previo:** esta versión reemplaza al mapa generado antes de que existieran `specify.md`, `plan.md`, `tasks.md` y los ADR. El proyecto ahora sí dispone de historias de usuario (HU-01 a HU-08), criterios de aceptación (CA-xx), requisitos no funcionales (RNF-01 a RNF-08) y un plan técnico con módulos y fases. El número de features pasó de 5 a 6 como resultado de dividir "reportes" de "consulta" según la evidencia actual.

## 2. Problema general

Existe falta de trazabilidad y automatización en el cumplimiento de las recomendaciones emitidas por la Contraloría General del Estado (CGE) a la Universidad Nacional de Loja (UNL). La gestión dispersa actual dificulta el seguimiento formal y el reporte oportuno de los estados de cumplimiento, y expone a la institución a dar por cumplidas recomendaciones que normativamente siguen pendientes o rechazadas.

Fuente: `docs/problem-definition.md` §1 y §4; `specify.md` §1.1.

## 3. Actores identificados

| ID | Actor | Necesidad principal | Fuente |
|---|---|---|---|
| A-01 | Auditoría Interna (UAI) / Validador de Cumplimiento | Auditar, validar y aprobar/rechazar el cumplimiento con base en evidencias | `docs/problem-definition.md` §2; `specify.md` §2, §4 |
| A-02 | Responsable de Unidad Administrativa (Ejecutor) | Registrar avances, planes/tareas y cargar evidencias de las recomendaciones de su área | `docs/problem-definition.md` §2; `specify.md` §2, §4 |
| A-03 | Máxima Autoridad (Rectorado) | Visualizar el estado general de la institución frente a la CGE | `docs/problem-definition.md` §2; `specify.md` §1.2 |
| A-04 | Contraloría General del Estado (CGE) | Recibir los reportes finales (matrices de cumplimiento) | `docs/problem-definition.md` §2; `specify.md` §1.2 |
| A-05 | Administrador del Sistema | Gestionar usuarios, roles y parámetros; mantener la configuración | `specify.md` §2 |
| A-06 | Auditor CGE / Consulta | Consultar estado e historial y generar/exportar matrices (solo lectura) | `specify.md` §2, §4 (HU-02, HU-07, HU-08) |

Nota: A-04 (CGE) es la entidad destinataria de los reportes; el rol operativo de la UNL que genera la matriz corresponde a A-06 (Auditor CGE / Consulta) según HU-08. Persiste ambigüedad sobre el rol exacto (§12).

## 4. Necesidades y capacidades

| ID | Actor | Necesidad | Capacidad funcional | Fuente |
|---|---|---|---|---|
| N-01 | A-01 UAI | Registrar de forma formal y centralizada las recomendaciones de la CGE con plazo y prioridad | Registro de recomendaciones | `docs/problem-definition.md` §3; `specify.md` §3, HU-01 |
| N-02 | A-01 UAI / A-05 Administrador | Asignar responsables (unidades/funcionarios) a cada recomendación | Asignación de responsables | `specify.md` §4 (HU-03) |
| N-03 | A-02 Ejecutores | Registrar avances y planes de acción/tareas de cumplimiento | Registro de planes/tareas y avances | `specify.md` §4 (HU-04, HU-05 paso) |
| N-04 | A-02 Ejecutores | Cargar evidencias en PDF que respalden el avance o cumplimiento | Carga de evidencias | `docs/problem-definition.md` §3; `specify.md` §4 (HU-05) |
| N-05 | A-02 Ejecutores | Notificar que una tarea asignada está cumplida | Notificación de cumplimiento (transición de estado) | `specify.md` §3.1, §4 (HU-05/06) |
| N-06 | A-01 UAI | Validar/aprobar o rechazar el cumplimiento conforme a evidencias y normativa | Validación y aprobación de cumplimiento | `docs/problem-definition.md` §2; `specify.md` §3.2, HU-06 |
| N-07 | A-03 Rectorado / A-06 Auditor | Conocer el estado de cumplimiento de las recomendaciones | Consulta del estado de cumplimiento | `specify.md` §4 (HU-02) |
| N-08 | A-03 Rectorado | Visualizar el estado general de la institución frente a la CGE | Visión institucional consolidada | `docs/problem-definition.md` §2 |
| N-09 | A-04 CGE / A-06 Auditor | Generar y exportar matrices de cumplimiento | Generación de matrices/reportes | `docs/problem-definition.md` §2; `specify.md` §4 (HU-08) |
| N-10 | Institución UNL / A-01 UAI | Trazabilidad inmutable de cambios de estado y evidencia | Registro y consulta de historial de auditoría | `specify.md` §3.4, §4 (HU-07); Constitución §VII |
| N-11 | A-01 UAI / A-02 Ejecutores | Conocer y controlar fechas límite y vencimientos | Gestión de plazos y alertas de vencimiento | `specify.md` §3.3; Constitución §VIII |
| N-12 | Todos los roles | Acceso diferenciado según rol y pertenencia al recurso | Control de acceso (RBAC) | `specify.md` §2, RNF-02; Constitución §VII |

## 5. Features candidatas

| ID | Feature candidata | Actor principal | Necesidad atendida | Valor independiente | Criterios propios | Puede probarse de forma independiente | Tamaño manejable | Decisión |
|---|---|---|---|---|---|---|---|---|
| C-01 | Registro de recomendaciones CGE | A-01 UAI / A-05 Admin | N-01 | Sí | Sí (CA-01.1–01.3) | Sí | Sí | Feature |
| C-02 | Asignación de responsables | A-01 UAI / A-05 Admin | N-02 | Parcial (requiere recomendación registrada) | Sí (CA-03.1–03.3) | Sí | Pequeño | Subfeature |
| C-03 | Registro de planes de acción / tareas y avances | A-02 Ejecutor | N-03 | Sí | Sí (CA-04.1–04.2) | Sí | Sí | Feature |
| C-04 | Carga de evidencias en PDF | A-02 Ejecutor | N-04 | Sí | Sí (CA-05.1–05.4) | Sí | Sí | Feature |
| C-05 | Flujo de estados y validación de cumplimiento | A-01 UAI / A-02 Ejecutor | N-05, N-06 | Sí | Sí (CA-06.1–06.3) | Sí | Sí | Feature |
| C-06 | Gestión de plazos y alertas de vencimiento | A-01 UAI / A-02 Ejecutor | N-11 | Sí | Parcial (umbrales sin definir) | Sí | Medio | Pendiente de clarificación |
| C-07 | Registro y consulta de historial inmutable (auditoría) | A-01 UAI / A-06 Auditor | N-10 | Sí (funcional en el proyecto) | Sí (CA-07.1–07.3) | Sí | Sí | Feature |
| C-08 | Consulta del estado de cumplimiento | A-06 Auditor / A-03 Rectorado | N-07 | Sí | Sí (CA-02.1–02.2) | Sí | Sí | Feature |
| C-09 | Visión institucional consolidada | A-03 Rectorado | N-08 | Parcial (depende de consulta) | No explícitos | Sí | Pequeño | Integrar con otra feature |
| C-10 | Generación de matrices de cumplimiento | A-04 CGE / A-06 Auditor | N-09 | Sí | Sí (CA-08.1–08.2) | Sí | Sí | Feature |
| C-11 | Control de acceso por rol (RBAC) | Todos los roles | N-12 | Sí | Parcial (permisos sin confirmar) | Sí | Medio | No corresponde a feature |
| C-12 | Autenticación de usuarios (JWT) | Todos los roles | N-12 | Sí | No (decisión técnica) | Sí | Medio | No corresponde a feature |

Justificación de decisiones:

- **C-02:** `specify.md` §4 (HU-03) y `plan.md` §1.2 la tratan como parte del registro/gestión de la recomendación; su tamaño aislado no justifica una feature propia. Se integra en F-001.
- **C-06:** `specify.md` §3.3 define la capacidad funcional y HU-01 exige fecha límite, pero los umbrales/periodicidad de alertas están sin definir (`.spec/clarify.md` CL-06 y `specify.md` §7b-c). El proyecto además no incluye "prórrogas" en el alcance (CL-06). Decisión: Feature condicionada a clarificación; no se descarta porque la Constitución §VIII y `specify.md` §3.3 la exigen explícitamente.
- **C-07:** el proyecto trata la trazabilidad como **capacidad funcional** (HU-07, CA-07.1–07.3, endpoint de historial en `plan.md` §2.1, ADR-0006), no solo como requisito no funcional. Por eso sí se convierte en feature (excepción legítima a la regla 7).
- **C-09:** "visión institucional consolidada" (N-08) no tiene criterios de aceptación propios en `specify.md` y es la dimensión de lectura agregada de F-004; se integra en ella.
- **C-11 / C-12:** RBAC y autenticación JWT son requisitos de seguridad (RNF-02; Constitución §VII) y una decisión técnica (ADR-0002), respectivamente. No se convierten en features por la regla 7.

## 6. Features consolidadas

### F-001 — Registro y gestión de recomendaciones CGE

**Actor principal:**
A-01 Auditoría Interna (UAI); A-05 Administrador del Sistema.

**Actores secundarios:**
A-02 Ejecutores (receptores de asignación).

**Objetivo:**
Registrar de forma formal y centralizada cada recomendación emitida por la CGE, con su plazo y prioridad, y asignar sus responsables.

**Necesidad que resuelve:**
N-01, N-02.

**Descripción funcional:**
Alta de recomendaciones con información institucional, plazo obligatorio y prioridad, y asignación de uno o más responsables (unidades/funcionarios) como base del seguimiento posterior.

**Incluye:**
- Registro de recomendaciones con plazo y prioridad (HU-01).
- Validación de datos obligatorios y de fecha límite (CA-01.2, CA-01.3).
- Asignación de responsables, permitiendo múltiples sin perder los previos (subfeature C-02, HU-03).

**No incluye:**
- Carga de evidencias (F-003).
- Transiciones de estado y validación de cumplimiento (F-004).
- Consulta y reportes (F-005, F-006).
- Sincronización automática por API con la CGE (fuera de alcance, `docs/problem-definition.md` §3).
- Prórrogas de plazo (pendiente de clarificación, CL-06).

**Requisitos relacionados:**
- RNF-02 (acceso por recurso), RNF-04/RNF-05 (contrato y errores), RNF-08 (paginación).

**Historias relacionadas:**
- HU-01 (Registro de recomendaciones), HU-03 (Asignación de responsables).

**Criterios de aceptación relacionados:**
- CA-01.1, CA-01.2, CA-01.3, CA-03.1, CA-03.2, CA-03.3.

**Dependencias:**
- Ninguna feature previa; es base del flujo. Depende de CL-01 (estados) para el estado inicial y de CL-08 (atribuciones por rol) para quién registra.

**Riesgos o restricciones:**
- Datos a registrar deben alinearse con la normativa CGE (Acuerdo 010-CG-2022, `docs/problem-definition.md` §4), no traducida a campos aún.

**Prioridad:** Alta

**Estado:** Especificada (pendiente de clarificación CL-01/CL-08)

### F-002 — Registro de planes de acción, tareas y avances

**Actor principal:**
A-02 Responsable de Unidad (Ejecutor).

**Actores secundarios:**
A-01 UAI (consulta el avance).

**Objetivo:**
Permitir que los ejecutores registren planes de acción, tareas de cumplimiento y avances de las recomendaciones asignadas a su unidad.

**Necesidad que resuelve:**
N-03.

**Descripción funcional:**
Registro de tareas asociadas a una recomendación y de los avances que preparan la notificación de cumplimiento.

**Incluye:**
- Registro de tareas de cumplimiento asociadas a una recomendación (HU-04).
- Control de acceso por recurso (una tarea de otra unidad no se gestiona, CA-04.2).
- Registro del avance en el historial (base de la transición a `En Validación`).

**No incluye:**
- Carga de archivos de evidencia (F-003).
- Decisión de aprobación/rechazo (F-004).
- Gestión de plazos y alertas (C-06, pendiente de clarificación).

**Requisitos relacionados:**
- RNF-02 (acceso por recurso), RNF-06 (integridad transaccional).

**Historias relacionadas:**
- HU-04 (Registro de planes de acción y tareas).

**Criterios de aceptación relacionados:**
- CA-04.1, CA-04.2.

**Dependencias:**
- F-001 (la tarea se asocia a una recomendación registrada y asignada).

**Riesgos o restricciones:**
- La relación exacta tarea↔avance↔transición de estado depende de CL-01 (estados).

**Prioridad:** Media

**Estado:** Especificada (pendiente de clarificación CL-01)

### F-003 — Gestión de evidencias de cumplimiento (PDF)

**Actor principal:**
A-02 Responsable de Unidad (Ejecutor).

**Actores secundarios:**
A-01 UAI (revisa las evidencias en F-004); A-06 Auditor (consulta, según CL-04).

**Objetivo:**
Permitir que los ejecutores carguen evidencias en PDF que respalden el avance o cumplimiento.

**Necesidad que resuelve:**
N-04.

**Descripción funcional:**
Carga de evidencias PDF asociadas a una recomendación, con validación de tipo/tamaño y distinción entre borrador de avance y entrega final.

**Incluye:**
- Carga de archivos PDF (HU-05).
- Validación de formato y tamaño (CA-05.2, CA-05.3).
- Distinción borrador vs. entrega final (CA-05.4).
- Anulación lógica de evidencia con conservación de historial (CA-07.3).

**No incluye:**
- Aprobar o rechazar el cumplimiento (F-004).
- Formatos distintos a PDF (la evidencia solo menciona PDF).
- Políticas de retención/eliminación (pendientes de requisitos institucionales, CL-10).
- Requisitos de validez probatoria (pendientes de CL-07).

**Requisitos relacionados:**
- RNF-03 (sanitización y límites de archivos), RNF-06 (atomicidad evidencia+estado).

**Historias relacionadas:**
- HU-05 (Carga de evidencias).

**Criterios de aceptación relacionados:**
- CA-05.1, CA-05.2, CA-05.3, CA-05.4, CA-07.3.

**Dependencias:**
- F-001 (asociación a una recomendación registrada).
- CL-05 (anulación) y CL-07 (validez probatoria) para congelar el diseño.

**Riesgos o restricciones:**
- Riesgo de seguridad de datos en PDF cargados (`docs/problem-definition.md` §4); validez probatoria sin confirmar (CL-07).

**Prioridad:** Media

**Estado:** Especificada (pendiente de clarificación CL-05/CL-07)

### F-004 — Flujo de estados y validación de cumplimiento

**Actor principal:**
A-01 UAI (Validador de Cumplimiento).

**Actores secundarios:**
A-02 Ejecutores (notifican el cumplimiento).

**Objetivo:**
Gestionar el ciclo de vida de la recomendación y formalizar la validación (aprobación/rechazo) de su cumplimiento.

**Necesidad que resuelve:**
N-05, N-06.

**Descripción funcional:**
La recomendación avanza por estados definidos; el ejecutor notifica el cumplimiento y el validador aprueba o rechaza conforme a las evidencias y la normativa. Rige la separación de responsabilidades.

**Incluye:**
- Matriz de transición de estados (HU-06, CA-06.1–06.3).
- Notificación de cumplimiento por el ejecutor (N-05).
- Separación de responsabilidades: quien registra el avance no aprueba su cumplimiento (CA-06.3).
- Aprobación → `Cumplida` y rechazo → `En Proceso` (CA-06.1, CA-06.2).

**No incluye:**
- Definición normativa definitiva de los estados (CL-01).
- Reapertura de recomendaciones sin condición normativa (CL-02).
- Gestión de plazos/vencimiento (C-06).
- Auditoría completa de todas las operaciones (F-005 cubre el historial funcional).

**Requisitos relacionados:**
- RNF-02 (acceso por recurso), RNF-06 (atomicidad), RNF-07 (idempotencia).

**Historias relacionadas:**
- HU-06 (Validación del cumplimiento).

**Criterios de aceptación relacionados:**
- CA-06.1, CA-06.2, CA-06.3.

**Dependencias:**
- F-001 (transiciones sobre recomendaciones registradas).
- F-003 (revisión de evidencias cargadas).
- **Bloqueada por CL-01 y CL-02** (estados y reapertura).

**Riesgos o restricciones:**
- Riesgo crítico del proyecto: modelado incorrecto del flujo de estados (`docs/problem-definition.md` §4; `docs/control-questions.md` §5); estados sin definir (CL-01).

**Prioridad:** Alta

**Estado:** Especificada (pendiente de clarificación CL-01/CL-02)

### F-005 — Registro y consulta de historial inmutable (auditoría)

**Actor principal:**
A-01 UAI; A-06 Auditor CGE / Consulta.

**Actores secundarios:**
A-02 Ejecutores (originan cambios registrados).

**Objetivo:**
Registrar de forma inmutable y permitir consultar quién hizo qué cambio, cuándo, desde qué IP y con qué evidencia.

**Necesidad que resuelve:**
N-10.

**Descripción funcional:**
Registro append-only de cada cambio de estado, asignación y carga de evidencia; consulta del historial por rol autorizado.

**Incluye:**
- Registro inmutable de cambios (actor, fecha/hora, estado anterior/nuevo, evidencia) (HU-07, CA-07.1).
- Impedimento de modificación/eliminación de registros (CA-07.2).
- Conservación del rastro de evidencias anuladas (CA-07.3).

**No incluye:**
- La definición de qué operaciones adicionales deben auditarse fuera del alcance funcional (CL-08 "qué cambios deben registrarse").
- Retención/archivado a largo plazo (CL-10).

**Requisitos relacionados:**
- RNF-01 (trazabilidad inmutable), RNF-02 (acceso por recurso).

**Historias relacionadas:**
- HU-07 (Trazabilidad y auditoría).

**Criterios de aceptación relacionados:**
- CA-07.1, CA-07.2, CA-07.3.

**Dependencias:**
- F-001 (cambios sobre recomendaciones).
- F-004 (cambios de estado a registrar).
- F-003 (cargas de evidencia a registrar).

**Riesgos o restricciones:**
- Crecimiento continuo del historial; respaldo/retención sin definir (CL-10).

**Prioridad:** Alta

**Estado:** Especificada

### F-006 — Consulta del estado de cumplimiento y matrices de cumplimiento

**Actor principal:**
A-06 Auditor CGE / Consulta; A-03 Máxima Autoridad (Rectorado).

**Actores secundarios:**
A-04 CGE (destinataria del reporte).

**Objetivo:**
Permitir consultar el estado de cumplimiento (individual e institucional) y generar/exportar las matrices de cumplimiento requeridas por la CGE.

**Necesidad que resuelve:**
N-07, N-08, N-09.

**Descripción funcional:**
Consulta del estado de las recomendaciones con filtros, visión consolidada institucional y generación/exportación de matrices de cumplimiento.

**Incluye:**
- Consulta del estado e historial de una recomendación (HU-02, CA-02.1).
- Filtrado por estado/unidad/plazo (CA-02.2).
- Visión institucional consolidada (N-08, integrada de C-09).
- Generación y exportación de matrices de cumplimiento (HU-08, CA-08.1, CA-08.2).

**No incluye:**
- Modificación de estados, responsables o evidencias (solo lectura, `specify.md` §2).
- Sincronización automática con la CGE (fuera de alcance, `docs/problem-definition.md` §3).
- Formato exacto de exportación (CL-12).

**Requisitos relacionados:**
- RNF-02 (acceso por recurso), RNF-08 (paginación y filtrado).

**Historias relacionadas:**
- HU-02 (Consulta del estado), HU-08 (Generación de matrices).

**Criterios de aceptación relacionados:**
- CA-02.1, CA-02.2, CA-08.1, CA-08.2.

**Dependencias:**
- F-001 (datos registrados).
- F-004 (estados consolidados).
- F-005 (historial para CA-02.1).

**Riesgos o restricciones:**
- El formato y periodicidad de las matrices dependen de la CGE (CL-12).

**Prioridad:** Media

**Estado:** Especificada (parcialmente; pendiente CL-12)

## 7. Matriz general de features

| ID | Feature | Actor principal | Objetivo | Prioridad | Dependencias | Estado | Especificación |
|---|---|---|---|---|---|---|---|
| F-001 | Registro y gestión de recomendaciones CGE | A-01 UAI / A-05 Admin | Registrar recomendaciones y asignar responsables | Alta | — | Especificada | `specs/001-registro-recomendaciones/spec.md` |
| F-002 | Registro de planes de acción, tareas y avances | A-02 Ejecutor | Organizar el trabajo de cumplimiento | Media | F-001 | Especificada | `specs/002-planes-accion-tareas/spec.md` |
| F-003 | Gestión de evidencias de cumplimiento (PDF) | A-02 Ejecutor | Cargar evidencias PDF que respalden el avance | Media | F-001 | Especificada | `specs/003-gestion-evidencias/spec.md` |
| F-004 | Flujo de estados y validación de cumplimiento | A-01 UAI | Gestionar ciclo de vida y validar cumplimiento | Alta | F-001, F-003 | Especificada (bloqueada por CL-01/02) | `specs/004-flujo-validacion/spec.md` |
| F-005 | Registro y consulta de historial inmutable (auditoría) | A-01 UAI / A-06 Auditor | Trazabilidad inmutable de cambios | Alta | F-001, F-003, F-004 | Especificada | `specs/005-historial-auditoria/spec.md` |
| F-006 | Consulta del estado y matrices de cumplimiento | A-06 Auditor / A-03 Rectorado | Consultar estado y reportar a la CGE | Media | F-001, F-004, F-005 | Especificada (parcial) | `specs/006-consulta-reportes/spec.md` |

## 8. Relación entre features

```text
F-001 Registro y gestión de recomendaciones CGE
        ↓
   ┌────┴───────────────┐
   ↓                    ↓
F-002 Planes, tareas   F-003 Gestión de evidencias (PDF)
y avances                ↓
   └────────┬───────────┘
            ↓
F-004 Flujo de estados y validación de cumplimiento
            ↓
F-005 Registro y consulta de historial inmutable (auditoría)
            ↓
F-006 Consulta del estado y matrices de cumplimiento
```

## 9. Priorización

| Feature | Valor | Dependencia | Riesgo | Complejidad | Prioridad | Justificación |
|---|---|---|---|---|---|---|
| F-001 | Alto | Baja (base) | Medio | Medio | Alta | Base de todo el flujo; cubierta por Fase 3 del backlog (`tasks.md`). |
| F-002 | Medio | Media (F-001) | Bajo | Bajo | Media | Necesaria para organizar el cumplimiento; depende del registro. |
| F-003 | Alto | Media (F-001) | Medio | Medio | Media | Núcleo probatorio; riesgo de seguridad y de validez (CL-07). |
| F-004 | Alto | Alta (F-001, F-003) | Alto | Alto | Alta | Corazón del seguimiento y riesgo crítico del proyecto; bloqueada por CL-01/02. |
| F-005 | Alto | Alta (F-001/03/04) | Medio | Medio | Alta | La trazabilidad es capacidad funcional explícita (HU-07) y requisito institucional. |
| F-006 | Medio | Alta (F-001/04/05) | Bajo | Medio | Media | Cierra el ciclo hacia la CGE; depende de estados e historial consolidados. |

## 10. Especificaciones propuestas

Se justifican **6 especificaciones**. A diferencia del mapa previo (5), la evidencia actual separa las "tareas/avances" (F-002) de las "evidencias" (F-003) y agrupa la "consulta" con los "reportes/matrices" (F-006), siguiendo los módulos de `plan.md` §1.2 y las HU de `specify.md` §4.

| Nro. | Feature | Ruta propuesta | Justificación |
|---|---|---|---|
| 1 | F-001 Registro y gestión de recomendaciones CGE | `specs/001-registro-recomendaciones/spec.md` | Objetivo autónomo y base de las demás; HU-01 y HU-03. |
| 2 | F-002 Planes de acción, tareas y avances | `specs/002-planes-accion-tareas/spec.md` | Actor distinto (ejecutor) y objetivo propio (organizar el cumplimiento); HU-04. |
| 3 | F-003 Gestión de evidencias (PDF) | `specs/003-gestion-evidencias/spec.md` | Reglas de seguridad propias y validación independiente; HU-05. |
| 4 | F-004 Flujo de estados y validación | `specs/004-flujo-validacion/spec.md` | Actor principal distinto (validador) y riesgo crítico; HU-06. |
| 5 | F-005 Historial inmutable (auditoría) | `specs/005-historial-auditoria/spec.md` | Capacidad funcional de trazabilidad con criterios propios; HU-07. |
| 6 | F-006 Consulta del estado y matrices de cumplimiento | `specs/006-consulta-reportes/spec.md` | Salida hacia la CGE y consulta institucional; HU-02 y HU-08. Puede compartir especificación internamente si el equipo lo prefiere, por su naturaleza de lectura. |

## 11. Alcance del incremento actual

### Features que se trabajarán en el incremento actual (Fase 1 — Backend)

Según `.spec/specify.md` §1.5 (todas dentro del alcance de Fase 1) y `.spec/tasks.md` (45 tareas organizadas en 6 fases):

- F-001 — Registro y gestión de recomendaciones CGE.
- F-002 — Registro de planes de acción, tareas y avances.
- F-003 — Gestión de evidencias de cumplimiento (PDF).
- F-004 — Flujo de estados y validación de cumplimiento.
- F-005 — Registro y consulta de historial inmutable (auditoría).
- F-006 — Consulta del estado y matrices de cumplimiento.

### Features previstas para incrementos posteriores

- No hay features del backend fuera de la Fase 1 en la evidencia actual. Las fases F2 (Web) y F3 (Móvil) son **clientes** del mismo API (`constitution.md` §XVI), no nuevas capacidades del backend.

### Features pendientes de clarificación

- **C-06 — Gestión de plazos y alertas de vencimiento:** exigida por `specify.md` §3.3 y Constitución §VIII, pero sin umbrales definidos (CL-06); prórrogas explícitamente pendientes.
- **C-09 — Visión institucional consolidada:** integrada en F-006 por falta de criterios propios; se confirmará si requiere tratamiento aparte.

## 12. Preguntas pendientes

- ¿Cuáles son los estados y transiciones definitivos del ciclo de vida? (CL-01; bloquea F-004 y el estado inicial de F-001).
- ¿Se permite reabrir una recomendación `Cumplida`/archivada y bajo qué condiciones? (CL-02; bloquea F-004).
- ¿Puede un ejecutor reasignar una recomendación a otra unidad sin autorización del Validador? (CL-03; afecta F-001).
- ¿Qué nivel de visibilidad tiene el Auditor sobre evidencias en estado de borrador? (CL-04; afecta F-003/F-006).
- ¿La evidencia errónea se anula/oculta o permanece visible como "Anulada"? (CL-05; bloquea F-003).
- ¿El sistema permite solicitudes de prórroga de plazos? ¿Quién las aprueba? (CL-06; decide si C-06 es una feature).
- ¿Qué normativa rige la validez probatoria de las evidencias digitales? (CL-07; bloquea F-003).
- ¿Qué acciones y atribuciones concretas tiene cada rol (Administrador, Responsable, Validador, Auditor)? (CL-08; afecta todas las features).
- ¿Qué operaciones adicionales deben quedar registradas para auditoría? (afecta el alcance de F-005).
- ¿Qué políticas de retención, consulta y eliminación de evidencias aplican? (CL-10; afecta F-003/F-005).
- ¿Qué formato de exportación debe tener la matriz de cumplimiento? (CL-12; afecta F-006).
- ¿El registro inicial de recomendaciones lo realiza solo Auditoría Interna o también otras áreas receptoras de la CGE? (afecta F-001).
- ¿El rol que genera operativamente las matrices es el Auditor CGE/Consulta (A-06) u otro de la UNL? (afecta F-006).

## 13. Trazabilidad

| Feature | Actor | Necesidad | Requisito | Historia | Criterio de aceptación | Fuente |
|---|---|---|---|---|---|---|
| F-001 | A-01 UAI / A-05 Admin | N-01, N-02 | RNF-02, RNF-04, RNF-05, RNF-08 | HU-01, HU-03 | CA-01.1–01.3, CA-03.1–03.3 | `specify.md` §3–4; `docs/problem-definition.md` §3 |
| F-002 | A-02 Ejecutor | N-03 | RNF-02, RNF-06 | HU-04 | CA-04.1, CA-04.2 | `specify.md` §4 |
| F-003 | A-02 Ejecutor | N-04 | RNF-03, RNF-06 | HU-05 | CA-05.1–05.4, CA-07.3 | `specify.md` §3.4, §4; Constitución §VI–VII |
| F-004 | A-01 UAI / A-02 Ejecutor | N-05, N-06 | RNF-02, RNF-06, RNF-07 | HU-06 | CA-06.1–06.3 | `specify.md` §3.1–3.2, §4; `docs/problem-definition.md` §4 |
| F-005 | A-01 UAI / A-06 Auditor | N-10 | RNF-01, RNF-02 | HU-07 | CA-07.1–07.3 | `specify.md` §3.4, §4; Constitución §VII; ADR-0006 |
| F-006 | A-06 Auditor / A-03 Rectorado | N-07, N-08, N-09 | RNF-02, RNF-08 | HU-02, HU-08 | CA-02.1–02.2, CA-08.1–08.2 | `specify.md` §4; `docs/problem-definition.md` §2–3 |

Nota: la trazabilidad ahora conecta cada feature con requisitos (RNF), historias (HU) y criterios (CA) formalizados en `.spec/specify.md`, además de la Constitución y los ADR. Los requisitos funcionales (RF) siguen sin numeración explícita; se usan las HU/CA como unidad funcional.
