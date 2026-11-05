# Registro de Clarificaciones y Preguntas de Negocio CGE

**Artefactos analizados:** `.specify/memory/constitution.md` v1.0.0 y `.spec/specify.md` (Borrador, 2026-10-21).
**Propósito:** identificar ambigüedades, inconsistencias y vacíos normativos que requieran definición formal antes de planificar la implementación (Constitución §I).
**Estado general:** las decisiones marcadas como *Pendiente de validación con el requirente/auditor institucional* **NO DEBEN** darse por resueltas. Conforme a la Constitución §I y a la jerarquía normativa, una clarificación aprobada que cambie un requisito **DEBE** reflejarse también en `specify.md` y, cuando corresponda, en `plan.md` y `tasks.md`.

> **Nota metodológica:** este documento registra las preguntas y su impacto. Las "opciones consideradas" y "recomendación del equipo" son propuestas a debate, no respuestas acordadas. No se asume ninguna respuesta normativa sin validación del requirente (restricción explícita: "No asumir respuestas a ambigüedades críticas de la normativa CGE").

---

## 0. Resumen de clarificaciones

| ID | Aspecto | Pregunta clave | Estado | Impacto principal |
|---|---|---|---|---|
| CL-01 | Ciclo de vida y estados | ¿Cuáles son los estados definitivos según la normativa CGE? | Pendiente de validación | `specify.md` §3.1, §7a; `plan.md` (modelo de dominio) |
| CL-02 | Reapertura de cerradas | ¿Se permite reabrir una recomendación `Cumplida`/archivada y bajo qué condiciones? | Pendiente de validación | `specify.md` §3.1, §7d |
| CL-03 | Reasignación entre unidades | ¿Puede un ejecutor reasignar una recomendación a otra unidad sin autorización del Validador? | Pendiente de validación | `specify.md` §2, §3.2; RNF-02 |
| CL-04 | Visibilidad del Auditor sobre borradores | ¿Qué ve el Auditor externo sobre evidencias en borrador? | Pendiente de validación | `specify.md` §2, §4 (HU-07); Constitución §VII |
| CL-05 | Manejo y anulación de evidencias | ¿La evidencia errónea se anula/oculta o queda visible como "Anulada"? | Pendiente de validación | `specify.md` §3.4, §7e; Constitución §VIII |
| CL-06 | Plazos y prórrogas | ¿Se permite solicitar prórrogas? ¿Quién aprueba y cómo afecta el estado? | Pendiente de validación | `specify.md` §3.3, §7b–c |
| CL-07 | Validez probatoria de evidencia digital | ¿Qué reglamentación rige la validez probatoria de las evidencias digitales? | Pendiente de validación | `specify.md` §5 RNF-03, §7h |

---

## 1. Ciclo de Vida y Estados Definitivos

### CL-01 — Estados exactos del ciclo de vida

**Pregunta al requirente/auditor:**
¿Cuáles son los estados exactos que puede atravesar una recomendación según la normativa CGE (Acuerdo 010-CG-2022 y reglamentación complementaria), y son exactamente los propuestos (`Pendiente`, `En Proceso`, `En Validación`, `Cumplida`, `Vencida`, `Reabierta`)?

**Ambigüedad detectada:** `specify.md` §3.1 propone seis estados y ocho transiciones, pero reconoce (`.spec/clarify.md` original §1 y `specify.md` §7a) que no están validados contra la norma. `constitution.md` menciona estados de ejemplo ("Pendiente, En Proceso, Cumplida, Vencida, Reabierta") que no incluyen `En Validación`, por lo que existe una **inconsistencia entre la Constitución y la especificación**.

**Inconsistencia adicional:** la Constitución (§VIII) menciona estados "archivada o cerrada" en el resultado esperado del prompt de clarificación, pero ni la Constitución ni `specify.md` definen un estado `Archivada`. **NEEDS CLARIFICATION:** ¿existe un estado terminal distinto de `Cumplida`?

**Opciones consideradas:**
- A) Adoptar los seis estados de `specify.md` §3.1.
- B) Ajustar la lista según la norma CGE (posible inclusión de `Archivada`/`Cerrada`).
- C) Mantener estados y confirmar transiciones una por una con la norma.

**Recomendación del equipo:** opción B, condicionada a la revisión del Acuerdo 010-CG-2022.

**Estado:** Pendiente de validación con el requirente/auditor institucional.

**Impacto si cambia:** actualiza `specify.md` §3.1 (matriz de transición) y `constitution.md` §VIII; altera el modelo conceptual de dominio usado en `plan.md`; habilita HU-01, HU-06 y CA-06.x.

---

### CL-02 — Reapertura de recomendación cerrada o archivada

**Pregunta al requirente/auditor:**
¿Se permite reabrir una recomendación en estado `Cumplida` (o `Archivada`, si existe)? ¿Bajo qué condiciones normativas (hallazgo posterior, auditoría de seguimiento, orden de la CGE) y quién está habilitado para hacerlo?

**Ambigüedad detectada:** `specify.md` §3.1 incluye la transición `Cumplida → Reabierta` ejecutada por el Validador, pero §7d admite que no se ha definido qué evidencia o hallazgo la justifica. La Constitución §VIII no regula la reapertura.

**Opciones consideradas:**
- A) Reapertura solo por el Validador y con motivo obligatorio registrado en el historial.
- B) Reapertura restringida a orden expresa de la CGE.
- C) Prohibir la reapertura; crear una nueva recomendación vinculada.

**Recomendación del equipo:** opción A con motivo obligatorio, pendiente de confirmación normativa.

**Estado:** Pendiente de validación con el requirente/auditor institucional.

**Impacto si cambia:** modifica `specify.md` §3.1 y §7d; afecta reglas de auditoría (CA-07.x) e impacto en generación de matrices (HU-08).

---

## 2. Atribuciones y Roles

### CL-03 — Reasignación de recomendación entre unidades sin autorización del Validador

**Pregunta al requirente/auditor:**
¿Puede un Responsable de Unidad (Ejecutor) reasignar por iniciativa propia una recomendación a otra unidad administrativa, o esa reasignación requiere autorización del Validador o del Administrador?

**Ambigüedad detectada:** `specify.md` §2 limita al Ejecutor a "gestionar recomendaciones asignadas a su área", y HU-03 atribuye la asignación de responsables al Administrador / Auditoría Interna. Sin embargo, no se especifica si un ejecutor puede **transferir** una asignación existente a otra unidad. La Constitución §VII exige control de acceso a nivel de recurso, pero no cubre la transferencia.

**Opciones consideradas:**
- A) Solo el Administrador o Auditoría Interna reasigna.
- B) El Ejecutor puede solicitar reasignación, pero requiere aprobación del Validador.
- C) El Ejecutor reasigna libremente dentro de su ámbito.

**Recomendación del equipo:** opción B (solicitud + aprobación), sujeto a confirmación.

**Estado:** Pendiente de validación con el requirente/auditor institucional.

**Impacto si cambia:** actualiza `specify.md` §2 y §3.2; puede requerir una nueva historia de usuario (solicitud de reasignación) y regla en la matriz de transición.

---

### CL-04 — Visibilidad del Auditor externo sobre evidencias en borrador

**Pregunta al requirente/auditor:**
¿Qué nivel de visibilidad tiene un Auditor CGE / Consulta sobre las evidencias marcadas como **borrador de avance** (no entregas finales)?

**Ambigüedad detectada:** `specify.md` §3.4 exige distinguir borradores de entregas finales, y HU-07 da al Auditor acceso de lectura al historial. No se define si el borrador es visible al auditor antes de la validación formal, ni si su visibilidad afecta la validez probatoria. La Constitución §VIII distingue borrador de entrega final, pero no su visibilidad.

**Opciones consideradas:**
- A) El Auditor solo ve entregas finales validadas.
- B) El Auditor ve borradores y finales, con etiqueta de estado claro.
- C) Visibilidad del borrador configurable por recomendación.

**Recomendación del equipo:** opción B con etiquetado explícito, sujeto a confirmación.

**Estado:** Pendiente de validación con el requirente/auditor institucional.

**Impacto si cambia:** actualiza `specify.md` §2 y §4 (HU-07); afecta el control de acceso a nivel de recurso (RNF-02) y la lógica de auditoría.

---

## 3. Manejo y Anulación de Evidencias

### CL-05 — Anulación/ocultamiento de evidencia errónea

**Pregunta al requirente/auditor:**
Si se cargó una evidencia errónea, ¿se permite anularla u ocultarla, o debe permanecer permanentemente visible en el expediente con estado "Anulada"?

**Ambigüedad detectada:** `specify.md` §3.4 y Constitución §VIII exigen que la anulación sea "controlada" y "conserve obligatoriamente el historial", lo que sugiere que **no se elimina físicamente**. Pero no se define: (a) quién puede anular; (b) si la evidencia anulada permanece visible en el expediente con etiqueta "Anulada" o se oculta; (c) si el ocultamiento contradice la exigencia de preservación del historial.

**Inconsistencia potencial:** "ocultar" (sugerido por el prompt) y "conservar el historial obligatoriamente" (Constitución §VIII) podrían entrar en tensión si ocultar impidiera la consulta probatoria.

**Opciones consideradas:**
- A) Anulación lógica: la evidencia queda visible con estado `Anulada`, motivo y actor, nunca se elimina.
- B) Ocultamiento de la vista activa pero siempre recuperable desde el historial de auditoría.
- C) Eliminación física permitida (contradice la Constitución §VIII).

**Recomendación del equipo:** opción A (anulación lógica visible con historial), que respeta la Constitución; la opción C **NO DEBE** adoptarse.

**Estado:** Pendiente de validación con el requirente/auditor institucional.

**Impacto si cambia:** actualiza `specify.md` §3.4 y §7e; define una regla de anulación y afecta CA-07.3.

---

## 4. Plazos y Prórrogas

### CL-06 — Solicitudes de prórroga de plazos

**Pregunta al requirente/auditor:**
¿El sistema debe permitir registrar solicitudes de prórroga de plazos? En caso afirmativo, ¿quién las aprueba (Validador, Auditoría Interna, CGE) y cómo impacta la prórroga en el estado y en las alertas de vencimiento de la recomendación?

**Ambigüedad detectada:** `specify.md` §3.3 define cálculo automático de `Vencida` y alertas, pero no contempla prórrogas. La Constitución §VIII solo menciona control de fechas límite y alertas, sin prórrogas. Este es un vacío funcional completo: la funcionalidad de prórroga no está en `feature-map.md` ni en `specify.md`.

**Opciones consideradas:**
- A) Prórroga con solicitud del Ejecutor y aprobación del Validador; extiende fecha límite y reprograma alertas.
- B) Prórroga solo aprobada por la CGE (fuera del sistema, solo se registra).
- C) No admitir prórrogas en Fase 1; registrar como pendiente para incremento posterior.

**Recomendación del equipo:** opción C para Fase 1 (fuera de alcance actual, sin evidencia de requisito), salvo que el requirente confirme urgencia.

**Estado:** Pendiente de validación con el requirente/auditor institucional.

**Impacto si se aprueba A o B:** añade una nueva capacidad funcional (feature de prórrogas), nuevas historias de usuario y reglas de transición; actualiza `feature-map.md`, `specify.md` §3.3 y afecta el cálculo de `Vencida`.

**Preguntas derivadas (de `specify.md` §7b–c):**
- ¿Qué umbrales y periodicidad tienen las alertas de vencimiento y por qué canal se entregan?
- ¿El vencimiento aplica también a recomendaciones en `En Validación`?

**Estado de las derivadas:** Pendientes de validación.

---

## 5. Normativa Aplicable

### CL-07 — Validez probatoria de la evidencia digital

**Pregunta al requirente/auditor:**
¿Qué reglamentación específica rige la validez probatoria de las evidencias digitales (PDF) cargadas en el sistema? ¿Deben cumplir requisitos adicionales (firma electrónica, certificación, metadatos específicos, plazos de conservación) para ser admisibles como prueba?

**Ambigüedad detectada:** `specify.md` §5 (RNF-03) y Constitución §VII exigen sanitización y validación técnica de archivos, pero **no** se ha confirmado la base normativa que determina cuándo una evidencia digital es probatoriamente válida. El tema del proyecto (¿qué evidencias pueden adjuntarse?) sigue sin resolución normativa.

**Opciones consideradas:**
- A) Solo se exige formato PDF y validaciones de seguridad técnicas.
- B) Requisitos adicionales (firma electrónica / certificación / metadatos) según reglamento de archivo institucional.
- C) Requisitos definidos por la CGE para la validez probatoria ante auditoría.

**Recomendación del equipo:** opción C es la más segura; **DEBE** confirmarse contra el reglamento aplicable antes de especificar el módulo de evidencias.

**Estado:** Pendiente de validación con el requirente/auditor institucional.

**Impacto si cambia:** actualiza `specify.md` §5 (RNF-03) y §7h; puede introducir requisitos no funcionales adicionales (firma electrónica, sellos de tiempo) y afecta el diseño del módulo de evidencias.

---

## 6. Normativa CGE Consultada (a la fecha)

- Acuerdo 010-CG-2022 (referido en `docs/problem-definition.md` §4 como base de alineación del flujo de estados) — **contenido no incorporado al repositorio**; pendiente de recopilación.
- Reglamentos de auditoría interna y seguimiento de recomendaciones institucionales (referidos en `.spec/clarify.md` original §2) — **no disponibles** de forma completa.

**Acción requerida:** incorporar los textos normativos al repositorio (por ejemplo, en `docs/`) para poder trazar cada regla de negocio a su fuente normativa.

---

## 7. Otras ambigüedades heredadas de la Constitución y la Especificación

Estas provienen de `constitution.md` "Preguntas pendientes de clarificación" y `specify.md` §7, y se conservan para no perder trazabilidad:

| ID | Pregunta | Origen | Estado |
|---|---|---|---|
| CL-08 | ¿Qué acciones y atribuciones concretas tiene cada rol (Administrador, Responsable de Unidad, Validador, Auditor)? | Constitución §Preguntas | Pendiente |
| CL-09 | ¿El acervo probatorio es totalmente inmutable o admite anulación con historial conservado? | Constitución §Preguntas; relacionada con CL-05 | Pendiente |
| CL-10 | ¿Qué políticas institucionales aplican a retención, consulta y eliminación de evidencias? | Constitución §Preguntas | Pendiente |
| CL-11 | ¿Quién es el requirente formal que aprueba esta Constitución y sus enmiendas? | Constitución §Preguntas | Pendiente |
| CL-12 | ¿Qué formato de exportación debe tener la matriz de cumplimiento requerida por la CGE? | `specify.md` §7f | Pendiente |
| CL-13 | ¿El registro inicial de recomendaciones lo realiza solo Auditoría Interna o también otras áreas receptoras directas de la CGE? | `specify.md` §7g | Pendiente |

---

## 8. Decisiones adoptadas (a confirmar)

Hasta la fecha de este registro **no se ha validado formalmente ninguna decisión con el requirente/auditor institucional**. Las recomendaciones del equipo en §1–§5 son propuestas a debate, no acuerdos. Ninguna clarificación **DEBE** considerarse resuelta hasta su validación y firma, conforme a la Constitución §I y §Jerarquía Normativa.

| ID | Decisión propuesta | Validada | Fecha | Responsable de validación |
|---|---|---|---|---|
| CL-01 | Ajustar estados según Acuerdo 010-CG-2022 | No | — | Requirente / Auditor institucional |
| CL-02 | Reapertura por el Validador con motivo obligatorio | No | — | Requirente / Auditor institucional |
| CL-03 | Reasignación por solicitud + aprobación | No | — | Requirente / Auditor institucional |
| CL-04 | Auditor ve borradores y finales con etiqueta | No | — | Requirente / Auditor institucional |
| CL-05 | Anulación lógica visible con historial | No | — | Requirente / Auditor institucional |
| CL-06 | Prórrogas fuera de Fase 1 (salvo confirmación) | No | — | Requirente / Auditor institucional |
| CL-07 | Requisitos de validez probatoria por confirmar | No | — | Requirente / Auditor institucional |

---

## 9. Impacto en la Especificación (`specify.md`)

Cuando se validen las clarificaciones, **DEBEN** actualizarse los siguientes artefactos (Constitución §Jerarquía Normativa):

- **CL-01 / CL-02:** `specify.md` §3.1 (matriz de transición) y §7a, §7d; posible actualización de `constitution.md` §VIII.
- **CL-03:** `specify.md` §2, §3.2; posible nueva historia de usuario.
- **CL-04:** `specify.md` §2, §4 (HU-07); RNF-02.
- **CL-05:** `specify.md` §3.4, §7e; CA-07.3.
- **CL-06:** `specify.md` §3.3; posibles nuevas features en `feature-map.md`; RNF de alertas.
- **CL-07:** `specify.md` §5 (RNF-03); posibles RNF adicionales.
- **CL-08 a CL-13:** ajustes puntuales en las secciones correspondientes.

Ninguna especificación **DEBE** pasar de estado Borrador a Especificada mientras CL-01, CL-05 y CL-07 permanezcan sin validar, por ser las de mayor impacto normativo.
