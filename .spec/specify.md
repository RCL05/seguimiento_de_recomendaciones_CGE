# Especificación Funcional y de Dominio — Sistema de Seguimiento de Recomendaciones CGE

**Incremento**: Inicial (Fase 1: Backend)
**Fecha**: 2026-10-21
**Estado**: Borrador
**Alcance**: Requisitos de negocio, historias de usuario, reglas de auditoría y modelo conceptual. Agnóstico a base de datos, lenguaje y framework.
**Base normativa**: `.specify/memory/constitution.md` v1.0.0; `docs/problem-definition.md`; `feature-map.md`.

---

## 1. Definición del Problema y Necesidad de Negocio

### 1.1 Problema de control

La Universidad Nacional de Loja (UNL) no dispone de trazabilidad ni automatización para el cumplimiento de las recomendaciones emitidas por la Contraloría General del Estado (CGE). La gestión se encuentra dispersa, lo que impide el seguimiento formal y el reporte oportuno de estados de cumplimiento, y expone a la institución a dar por cumplidas recomendaciones que normativamente siguen pendientes o rechazadas.

Fuente: `docs/problem-definition.md` §1 y §4.

### 1.2 Necesidad del usuario

- **Auditoría Interna (UAI)** necesita auditar y validar las evidencias de cumplimiento.
- **Ejecutores / Responsables de unidades** necesitan registrar avances, cargar evidencias y notificar el cumplimiento de sus tareas asignadas.
- **Máxima Autoridad (Rectorado)** necesita visualizar el estado general de la institución frente a la CGE.
- **CGE** requiere los reportes finales (matrices de cumplimiento).

Fuente: `docs/problem-definition.md` §2.

### 1.3 Requisito del sistema (qué debe hacer, sin cómo)

El sistema debe permitir: registrar recomendaciones con plazos y prioridades; modelar su ciclo de vida de estados; asignar responsables (unidades, ejecutores y validadores); registrar planes de acción y tareas; cargar y validar evidencias; y conservar un historial inmutable de cambios para auditoría y trazabilidad.

Fuente: prompt de especificación §1; `docs/problem-definition.md` §3.

### 1.4 Solución técnica (explícitamente fuera de esta especificación)

Las decisiones de arquitectura por capas, monolito modular, framework, lenguaje, motor de base de datos, OpenAPI, contenedores y CI/CD pertenecen a `plan.md` y a la Constitución (§II–VI, §XIII). Esta especificación es agnóstica a esas decisiones.

### 1.5 Delimitación de alcance

- **Dentro del alcance (Fase 1):** registro de recomendaciones y asignación de responsables; carga de evidencias PDF; flujo de aprobación y trazabilidad de cambios; consulta de estado; generación de matrices de cumplimiento.
- **Fuera del alcance:** interconexión por API en tiempo real o sincronización automática con la base de datos interna de la CGE (se limita a exportación de matrices); gestión de responsabilidades penales/judiciales; frontend web y aplicación móvil (Fases 2 y 3).

Fuente: `docs/problem-definition.md` §3; `feature-map.md` §11.

---

## 2. Actores y Roles (RBAC)

| Rol | Responsabilidad principal | Límites (lo que NO puede hacer) |
|---|---|---|
| **Administrador del Sistema** | Gestionar usuarios, roles y parámetros del sistema; mantener la configuración institucional. | No debe validar cumplimiento ni alterar estados de recomendaciones (separación de responsabilidades, §3.2). |
| **Responsable de Unidad Administrativa (Ejecutor)** | Registrar avances de las recomendaciones de su área, registrar planes de acción/tareas y cargar evidencias. | Solo gestiona recomendaciones asignadas a su área/unidad; no puede aprobar su propio cumplimiento (Constitución §VII). |
| **Validador de Cumplimiento (Control Interno / Auditoría Interna)** | Revisar evidencias y aprobar o rechazar formalmente el cumplimiento de una recomendación. | No debe registrar el avance que él mismo valida (separación de responsabilidades). |
| **Auditor CGE / Consulta** | Consultar el estado de cumplimiento y generar/exportar matrices de cumplimiento. | Acceso de solo lectura; no debe modificar estados, responsables ni evidencias. |

Los permisos exactos y combinaciones por rol **DEBEN** confirmarse con el requirente (ver §7, punto a).

Fuente: `feature-map.md` §3; `docs/problem-definition.md` §2; Constitución §VII.

---

## 3. Reglas de Negocio y Gobernanza de Auditoría

### 3.1 Ciclo de vida y matriz de transición de estados

Estados: `Pendiente`, `En Proceso`, `En Validación`, `Cumplida`, `Vencida`, `Reabierta`.

| Estado origen | Acción / evento | Rol habilitado | Estado destino |
|---|---|---|---|
| Pendiente | Registrar inicio de ejecución | Responsable de Unidad | En Proceso |
| En Proceso | Registrar avance y notificar cumplimiento | Responsable de Unidad | En Validación |
| En Validación | Aprobar cumplimiento | Validador | Cumplida |
| En Validación | Rechazar cumplimiento | Validador | En Proceso |
| Pendiente / En Proceso / En Validación | Vencer plazo sin cumplimiento | Sistema (automático) | Vencida |
| Vencida | Reanudar ejecución | Responsable de Unidad | En Proceso |
| Cumplida | Reabrir por hallazgo normativo | Validador | Reabierta |
| Reabierta | Registrar inicio de nueva ejecución | Responsable de Unidad | En Proceso |

Toda transición no listada **DEBE** rechazarse. Los estados y transiciones definitivos **DEBEN** validarse contra la normativa CGE antes de implementar (ver §7, punto a). Fuente: prompt de especificación §3; `.spec/clarify.md` §1.

### 3.2 Regla de separación de responsabilidades

Ninguna recomendación **DEBE** pasar a `Cumplida` sin aprobación formal del Validador. El actor que registra el avance (Responsable de Unidad) **NO DEBE** ser el mismo que aprueba el cumplimiento. Fuente: Constitución §VIII; prompt §3.

### 3.3 Gestión de plazos y alertas de vencimiento

- Cada recomendación **DEBE** tener una fecha límite de atención.
- El sistema **DEBE** calcular automáticamente el estado `Vencida` al superarse la fecha límite sin cumplimiento aprobado.
- El sistema **DEBE** generar alertas de vencimiento previo y de vencimiento efectivo.
- Los umbrales y la periodicidad de las alertas **DEBEN** confirmarse con el requirente (ver §7, punto b).

Fuente: Constitución §VIII; prompt §3.

### 3.4 Historial inmutable y preservación de evidencias

- Todo cambio de estado, asignación o carga de evidencia **DEBE** registrarse en un historial inmutable con: actor, fecha/hora, estado anterior, estado nuevo y evidencia asociada.
- El retiro o anulación de una evidencia **DEBE** ser controlado y **DEBE** conservar el historial (no eliminación física sin rastro).
- **DEBE** distinguirse entre borradores de avance y entregas finales de evidencias.
- Los registros de auditoría **NO DEBEN** modificarse ni eliminarse una vez creados.

Fuente: Constitución §VII y §VIII; prompt §3.

---

## 4. Historias de Usuario y Criterios de Aceptación

### Módulo: Recomendaciones

**HU-01 (P1) — Registro de recomendaciones**
*Como Administrador del Sistema / Auditoría Interna, quiero registrar una recomendación con su plazo y prioridad, para iniciar su seguimiento formal.*

- **CA-01.1** — Dado que soy un usuario autorizado, cuando registro una recomendación con datos obligatorios válidos, entonces el sistema la crea en estado `Pendiente` y la incluye en el historial.
- **CA-01.2** — Dado que ingreso una recomendación con datos obligatorios incompletos, cuando intento guardarla, entonces el sistema rechaza la operación e informa qué datos faltan.
- **CA-01.3** — Dado que registro una recomendación, cuando omito la fecha límite, entonces el sistema impide el guardado, porque el plazo es obligatorio.

**HU-02 (P2) — Consulta del estado de cumplimiento**
*Como Auditor CGE / Consulta, quiero consultar el estado de las recomendaciones, para conocer el avance institucional frente a la CGE.*

- **CA-02.1** — Dado que soy un usuario con acceso de lectura, cuando consulto una recomendación, entonces el sistema muestra su estado actual y su historial de cambios.
- **CA-02.2** — Dado que existen recomendaciones en distintos estados, cuando filtro por estado, unidad o plazo, entonces el sistema devuelve solo las recomendaciones que cumplen el criterio.

### Módulo: Asignación de Responsables

**HU-03 (P1) — Asignación de responsables**
*Como Administrador del Sistema / Auditoría Interna, quiero asignar responsables a una recomendación, para que exista una unidad ejecutora responsable de su atención.*

- **CA-03.1** — Dado que existe una recomendación registrada, cuando asigno una unidad responsable, entonces el sistema vincula la unidad y registra el cambio en el historial.
- **CA-03.2** — Dado que una recomendación ya tiene responsables, cuando intento asignar un responsable, entonces el sistema permite agregar responsables adicionales sin perder los anteriores.
- **CA-03.3** — Dado que no existe la recomendación, cuando intento asignar un responsable, entonces el sistema rechaza la operación.

### Módulo: Planes de Acción / Tareas

**HU-04 (P2) — Registro de planes de acción y tareas**
*Como Responsable de Unidad, quiero registrar planes de acción y tareas de cumplimiento, para organizar el trabajo necesario para atender la recomendación.*

- **CA-04.1** — Dado que tengo una recomendación asignada a mi unidad, cuando registro una tarea con su descripción, entonces el sistema la asocia a la recomendación y la registra en el historial.
- **CA-04.2** — Dado que una tarea pertenece a otra unidad, cuando intento gestionarla, entonces el sistema rechaza la operación por control de acceso a nivel de recurso.

### Módulo: Carga de Evidencias

**HU-05 (P1) — Carga de evidencias**
*Como Responsable de Unidad, quiero cargar evidencias en PDF, para respaldar el avance o cumplimiento de la recomendación.*

- **CA-05.1** — Dado que tengo una recomendación asignada, cuando cargo un archivo PDF válido, entonces el sistema asocia la evidencia a la recomendación y la registra en el historial.
- **CA-05.2** — Dado que intento cargar un archivo con formato no permitido, cuando envío la evidencia, entonces el sistema la rechaza e informa el formato admitido.
- **CA-05.3** — Dado que intento cargar un archivo que supera el tamaño máximo permitido, cuando envío la evidencia, entonces el sistema la rechaza e informa el límite.
- **CA-05.4** — Dado que una evidencia es un borrador de avance, cuando la marco como entrega final, entonces el sistema distingue su carácter en el registro.

**HU-06 (P1) — Validación del cumplimiento**
*Como Validador de Cumplimiento, quiero revisar las evidencias y aprobar o rechazar el cumplimiento, para garantizar que solo se cierre lo que está probado y normativamente cumplido.*

- **CA-06.1** — Dado que una recomendación está en `En Validación` con evidencias cargadas, cuando apruebo el cumplimiento, entonces el sistema cambia el estado a `Cumplida` y registra al validador en el historial.
- **CA-06.2** — Dado que una recomendación está en `En Validación`, cuando rechazo el cumplimiento, entonces el sistema cambia el estado a `En Proceso` y registra el motivo en el historial.
- **CA-06.3** — Dado que soy el Responsable de Unidad que registró el avance, cuando intento aprobar el cumplimiento, entonces el sistema rechaza la operación por separación de responsabilidades.

### Módulo: Auditoría

**HU-07 (P1) — Trazabilidad y auditoría**
*Como Auditoría Interna / Auditor CGE, quiero consultar el historial inmutable de cambios, para verificar quién hizo qué y cuándo.*

- **CA-07.1** — Dado que ocurrió un cambio de estado o una carga de evidencia, cuando consulto el historial, entonces el sistema muestra actor, fecha/hora, estado anterior, estado nuevo y evidencia asociada.
- **CA-07.2** — Dado que existe un registro de auditoría, cuando intento modificarlo o eliminarlo, entonces el sistema lo impide.
- **CA-07.3** — Dado que una evidencia fue anulada, cuando consulto el historial, entonces el sistema conserva el rastro de la anulación y de la evidencia original.

### Módulo: Reportes / Matrices de Cumplimiento

**HU-08 (P2) — Generación de matrices de cumplimiento**
*Como Auditor CGE / Consulta, quiero generar y exportar matrices de cumplimiento, para reportar el estado institucional a la CGE.*

- **CA-08.1** — Dado que existen recomendaciones con responsables y estados consolidados, cuando genero la matriz de cumplimiento, entonces el sistema la produce con la información registrada.
- **CA-08.2** — Dado que genero una matriz, cuando la exporto, entonces el sistema entrega el reporte en un formato utilizable sin sincronización automática con la CGE.

### Casos límite

- ¿Qué ocurre cuando el plazo de una recomendación vence mientras está en `En Validación`? (§7, punto c)
- ¿Qué ocurre cuando se intenta reabrir una recomendación ya `Cumplida` sin hallazgo que lo justifique? (§7, punto d)
- ¿Qué ocurre cuando dos usuarios actualizan la misma recomendación de forma simultánea? (Constitución §VI — debe resolverse con control de concurrencia).

---

## 5. Requisitos No Funcionales y de Seguridad

- **RNF-01 (Trazabilidad inmutable):** Toda petición que modifique un recurso **DEBE** registrar actor, fecha/hora, IP de origen y cambio realizado, en un registro inmutable.
- **RNF-02 (Control de acceso a nivel de recurso):** Un usuario **NO DEBE** gestionar recomendaciones ajenas a su área. Toda operación se autoriza por rol y por pertenencia al recurso.
- **RNF-03 (Sanitización y límites de archivos):** Los archivos de evidencia **DEBEN** validarse por tipo (PDF), tamaño máximo y contenido; **NO DEBEN** interpretarse ni ejecutarse de forma insegura.
- **RNF-04 (Contrato de respuesta uniforme):** Todas las operaciones **DEBEN** responder con el contrato universal definido en la Constitución §V, incluyendo `request_id`.
- **RNF-05 (Gestión de errores):** Los errores **DEBEN** categorizarse en Validación, Negocio, Autorización e Infraestructura, sin exponer detalles internos al cliente.
- **RNF-06 (Integridad transaccional):** Los cambios de estado que involucren carga de evidencia **DEBEN** ser atómicos.
- **RNF-07 (Idempotencia):** Las operaciones críticas **DEBEN** ser idempotentes cuando corresponda, para evitar duplicar cambios de estado o evidencias.
- **RNF-08 (Paginación y filtrado):** Los listados masivos **DEBEN** soportar paginación, filtrado por estado/unidad/plazo y ordenamiento estandarizado.

Fuente: prompt §5; Constitución §V, §VI, §VII, §IX, §X.

---

## 6. Modelo Conceptual (entidades, sin implementación)

- **Recomendación:** recomendación emitida por la CGE. Atributos conceptuales: identificador, descripción, origen, prioridad, fecha de emisión, fecha límite, estado actual. Se relaciona con responsables, tareas, evidencias e historial.
- **Responsable / Unidad:** unidad administrativa o funcionario ejecutor responsable de atender una recomendación. Relación: una recomendación puede tener uno o más responsables.
- **Validador:** usuario con atribución de aprobar o rechazar el cumplimiento. Relación: valida recomendaciones; separado del actor que registra el avance.
- **Plan de Acción / Tarea:** unidad de trabajo asociada a una recomendación para su cumplimiento. Relación: una recomendación puede tener varias tareas.
- **Evidencia:** archivo PDF que respalda un avance o una entrega final, asociado a una recomendación. Atributos: tipo (borrador/entrega final), estado (vigente/anulada), metadata.
- **Cambio de Estado (Historial):** registro inmutable de una transición: actor, fecha/hora, estado anterior, estado nuevo, evidencia asociada.
- **Alerta de Vencimiento:** aviso generado por el sistema ante proximidad o superación de la fecha límite.
- **Matriz de Cumplimiento:** reporte consolidado de estados y responsables para la CGE.

---

## 7. Puntos a Clarificar (restricciones respetadas — sin asumir respuestas)

- **a.** ¿Cuáles son los estados y transiciones definitivos del ciclo de vida, y qué acción normativa habilita la reapertura de una recomendación `Cumplida`? (`.spec/clarify.md` §1; normativa CGE pendiente).
- **b.** ¿Qué umbrales y periodicidad deben tener las alertas de vencimiento, y por qué canal se entregan?
- **c.** ¿El vencimiento debe aplicarse también a recomendaciones en `En Validación` o solo a las que no han sido notificadas como cumplidas?
- **d.** ¿Qué evidencia o hallazgo normativo es obligatorio para reabrir una recomendación?
- **e.** ¿El acervo probatorio es totalmente inmutable o se admite anulación con historial conservado? (la Constitución admite anulación controlada).
- **f.** ¿Qué formato de exportación debe tener la matriz de cumplimiento requerida por la CGE?
- **g.** ¿El registro inicial de recomendaciones lo realiza únicamente Auditoría Interna o también otras áreas receptoras directas de la CGE?
- **h.** ¿Qué normativa específica de la CGE (además del Acuerdo 010-CG-2022) rige estados, plazos y validaciones?

## 8. Supuestos

- Los usuarios del sistema cuentan con autenticación institucional previa al uso (mecanismo definido en `plan.md`).
- La normativa CGE se traducirá a reglas concretas antes de la implementación del flujo de estados.
- Las evidencias se gestionan exclusivamente en formato PDF en la Fase 1.
- Las notificaciones se limitan a alertas internas del sistema; no se asume integración con correo o mensajería.
