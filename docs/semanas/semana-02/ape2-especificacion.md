# APE 2: elaboración y refinamiento de la especificación

**Práctica Nro. 002 · Proyecto:** SITRA-CGE UNL

La guía llama `specification.md` al documento de especificación. En este proyecto es
[`specs/001-seguimiento-recomendaciones/spec.md`](../../../specs/001-seguimiento-recomendaciones/spec.md),
el nombre que usa GitHub Spec Kit.

## Procedimiento

### 1. Revisar los insumos existentes

Se revisaron `docs/problem-definition.md`, `feature-map.md`, `.spec/clarify.md`,
`spec.md` y el código. Inconsistencias encontradas:

| Inconsistencia | Resolución |
|---|---|
| `spec.md` listaba 7 estados y el flujo acordado usa 5 | Corregido en `spec.md` |
| "En Mora" dejaba la recomendación sin salida | Vencimiento como indicador |
| No había contexto, actores ni contratos en `spec.md` | Secciones agregadas |
| `.spec/specify.md` y `feature-map.md` usan términos anteriores | **Pendiente:** actualizar `feature-map.md` |

### 2. Refinar problema y alcance

Sección **Contexto del problema** de `spec.md`: problema, objetivo del incremento,
actores, inclusiones y restricciones. Las exclusiones están en **Fuera de alcance** y los
supuestos en **Supuestos**.

### 3. Formular requisitos funcionales

RF-001 a RF-024, numerados y con sintaxis EARS. Se agregaron RF-023 (reapertura) y
RF-024 (archivos protegidos). Se reescribieron RF-007, RF-009, RF-010, RF-012 y RF-016.

### 4. Formular requisitos no funcionales

RNF-001 a RNF-013. Se agregaron interoperabilidad (RNF-010), usabilidad (RNF-011),
accesibilidad (RNF-012) y mantenibilidad (RNF-013).

### 5. Elaborar historias de usuario

Seis historias con el formato "Como [actor], quiero [capacidad], para [beneficio]",
cada una con prioridad y prueba independiente.

### 6. Definir criterios de aceptación

Escenarios Dado–Cuando–Entonces con flujo exitoso, validaciones y errores. Se agregaron
los del rechazo sin observaciones, la reapertura, la entrega a tiempo y los hitos con el
plazo vencido.

### 7. Ejecutar clarificación

En `spec.md` están la sesión del 2026-10-20, la sesión del 2026-11-05 y las **Preguntas
pendientes**. Las decisiones del 2026-11-05 fueron del equipo y **falta validarlas con el
docente**. Las preguntas que siguen abiertas:

- Si la CGE admite prórrogas formales de plazo.
- Si los estados y las columnas de la matriz coinciden con el Acuerdo No. 010-CG-2022.
- Qué mecanismo SSO proporcionará la DTI.
- Cómo se reasigna una recomendación si cambia la estructura orgánica.

### 8. Identificar contratos preliminares

Sección **Contratos preliminares** de `spec.md`: requisito, recurso, operación, entrada,
resultado y códigos. El contrato detallado es
[`openapi.yaml`](../../../specs/001-seguimiento-recomendaciones/contracts/openapi.yaml).

### 9. Actualizar la especificación

| Contenido pedido | Sección de `spec.md` |
|---|---|
| Contexto | Contexto del problema |
| Actores | Actores |
| Alcance | Alcance y restricciones; Fuera de alcance |
| Restricciones | Alcance y restricciones; Supuestos |
| Requisitos | Requisitos funcionales; Requisitos no funcionales |
| Historias | Escenarios de Usuario y Pruebas |
| Criterios de aceptación | Escenarios de aceptación de cada historia |
| Escenarios alternativos | Casos límite; Escenarios críticos BDD adicionales |
| Contratos preliminares | Contratos preliminares |
| Decisiones de clarificación | Clarifications; Preguntas pendientes |

### 10. Validar con el docente

Guion para la presentación:

| Pregunta | Respuesta breve |
|---|---|
| ¿Qué problema resuelve? | El seguimiento manual y disperso de las recomendaciones de la CGE, sin trazabilidad |
| ¿Para quién? | UAI, unidades ejecutoras, Rectorado, auditor CGE y DTI |
| ¿Qué incluye? | Registro, plan, evidencias, dictamen, vencimientos, tablero, matriz y auditoría |
| ¿Qué excluye? | Sincronización en tiempo real con la CGE y responsabilidades penales o judiciales |
| ¿Qué requisitos integran el incremento? | RF-001 a RF-024, excepto RF-003, que sigue pendiente |
| ¿Cómo se comprobarán? | Escenarios de aceptación, pruebas automatizadas y contrato OpenAPI |
| ¿Qué sigue pendiente? | Las cuatro preguntas de la actividad 7 |

Resultado de la validación:

| Observación del docente | Decisión | Cambio y commit |
|---|---|---|
| [Completar] | [Completar] | [Completar] |

## Producto de la práctica

| Producto | Ubicación o estado |
|---|---|
| Enlace al repositorio con la especificación | <https://github.com/RCL05/seguimiento_de_recomendaciones_CGE/blob/feature/sdd-spec-kit-structure/specs/001-seguimiento-recomendaciones/spec.md> |
| Historial de cambios | `git log -- specs/001-seguimiento-recomendaciones/spec.md` |
| Requisitos, historias y criterios refinados | `spec.md` |
| Contratos preliminares y clarificación | `spec.md` |
| Nota individual con la contribución | Cada integrante: [evidencia-individual.md](evidencia-individual.md) |

## Resultados esperados

| Resultado | Estado |
|---|---|
| Problema y alcance delimitados | Cumplido |
| Requisitos consistentes y verificables | Cumplido, salvo RNF-005, RNF-006 y RF-014, que necesitan datos de la UAI |
| Historias vinculadas con actores reales | Cumplido |
| Criterios de aceptación comprobables | Cumplido |
| Decisiones registradas y preguntas explícitas | Cumplido |
| Contratos coherentes con los requisitos | Cumplido |
| Trazabilidad inicial | Cumplido: ver la matriz del [dossier](aa2-dossier-requisitos.md#9-matriz-de-trazabilidad) |
