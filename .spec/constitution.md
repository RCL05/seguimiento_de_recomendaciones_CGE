# Constitución del Proyecto

## Sistema de Seguimiento de Recomendaciones de la Contraloría General del Estado (CGE) en la Universidad Nacional de Loja (UNL)

Esta constitución establece los principios institucionales, éticos y técnicos que rigen el análisis, diseño, desarrollo, documentación y mantenimiento del sistema. Es de cumplimiento obligatorio para todas las personas que participen en el proyecto.

## 1. Propósito y Ámbito del Proyecto

El proyecto tiene como propósito apoyar a la Universidad Nacional de Loja en la gestión centralizada, trazabilidad y control del seguimiento de las recomendaciones emitidas por la Contraloría General del Estado. El sistema debe facilitar el registro organizado de la información pertinente, el seguimiento de su estado y la consulta de evidencias y actuaciones relacionadas, de acuerdo con los requisitos que se definan y validen institucionalmente.

El sistema es una herramienta de apoyo a la gestión y al control institucional. No reemplaza las competencias, decisiones, procedimientos ni responsabilidades de las autoridades y unidades de la UNL, ni las disposiciones aplicables de la CGE. El alcance funcional concreto se establecerá en las especificaciones del proyecto y no deberá darse por supuesto cuando no haya sido aprobado.

## 2. Principios Éticos e Institucionales de la UNL

El equipo aplicará obligatoriamente los siguientes principios en sus decisiones y actividades:

- **Solidaridad:** colaborar con respeto, compartir conocimiento y procurar que el sistema contribuya al trabajo coordinado de las unidades involucradas.
- **Transparencia:** documentar decisiones, requisitos, cambios y resultados de manera comprensible y verificable, respetando las restricciones legítimas de acceso y confidencialidad.
- **Responsabilidad:** cumplir los compromisos asumidos, proteger la información institucional y evaluar las consecuencias funcionales y técnicas de los cambios.
- **Honestidad académica:** reconocer las fuentes y contribuciones utilizadas, presentar resultados fieles a la evidencia y no atribuirse trabajo ajeno ni falsear actividades, pruebas o resultados.

Estos principios orientan tanto el comportamiento del equipo como el tratamiento de la información y la presentación de los entregables.

## 3. Normas de Convivencia y Trabajo en Equipo

- Mantener una comunicación respetuosa, oportuna y transparente. Los acuerdos, decisiones que afecten el alcance y bloqueos relevantes deben quedar registrados en los medios definidos para el proyecto.
- Colaborar mediante GitFlow, utilizando `main` para versiones estables, `develop` para integrar el trabajo en curso y ramas `feature/*` para implementar cambios acotados. Las ramas adicionales de soporte podrán utilizarse conforme a las prácticas acordadas por el equipo.
- Cada cambio debe tener un propósito identificable y mantenerse enfocado en el alcance aprobado. Los mensajes de cambios y la documentación asociada deben permitir entender su intención.
- Toda modificación destinada a integrarse en `develop` o `main` requiere un Pull Request (PR) y revisión de código por otra persona antes de fusionarse. La revisión debe comprobar, según corresponda, el cumplimiento de la especificación, la calidad, la seguridad, las pruebas y la documentación.
- No se deben fusionar cambios que tengan conflictos conocidos con los requisitos o que introduzcan fallos sin resolver. Las excepciones justificadas deben ser aprobadas por el equipo responsable y quedar documentadas.
- Recibir y ofrecer retroalimentación de forma constructiva, enfocándose en el trabajo y no en las personas.

## 4. Normas sobre el Uso Responsable de Inteligencia Artificial (IA)

- Se permite utilizar herramientas de IA, como Copilot, ChatGPT o Gemini, como asistencia para el desarrollo, análisis, pruebas y documentación, siempre que su uso respete las políticas institucionales y de privacidad aplicables.
- En cada entregable en el que se haya utilizado IA, se deben declarar las herramientas empleadas y describir de forma veraz el tipo de asistencia recibida. La declaración no sustituye la responsabilidad de quien presenta el entregable.
- Está prohibido inventar, alterar o presentar como reales código, fuentes, pruebas ejecutadas, resultados, aprobaciones, decisiones institucionales o cualquier otro antecedente. No se deben presentar como hechos las respuestas no verificadas de una herramienta de IA.
- Toda salida generada o modificada con IA debe ser revisada por una persona antes de incorporarse al proyecto. La revisión debe verificar exactitud, pertinencia, seguridad, licencias y conformidad con los requisitos.
- No se debe introducir información institucional confidencial, datos personales, credenciales ni otra información sensible en servicios de IA sin autorización expresa y sin que el uso cumpla las políticas aplicables.

## 5. Metodología SDD (Spec-Driven Development)

El desarrollo se guiará por especificaciones claras, revisables y mantenidas en el directorio `.spec/`. Los cambios funcionales o técnicos deben tener una justificación trazable a los artefactos de SDD; no se implementarán requisitos sustantivos basándose únicamente en supuestos o conversaciones no registradas.

Los artefactos del proyecto se mantienen con la siguiente jerarquía y propósito:

1. **`constitution.md`:** establece los principios y reglas permanentes del proyecto. Los demás artefactos y las decisiones de implementación deben respetarla.
2. **`specify.md`:** define el problema, los usuarios, el alcance, los requisitos y los criterios de aceptación. Debe ser coherente con la constitución.
3. **`clarify.md`:** registra preguntas, ambigüedades, respuestas y decisiones que precisen o corrijan la especificación. Las decisiones acordadas deben reflejarse también en los artefactos afectados.
4. **`plan.md`:** describe la solución propuesta, la arquitectura, las tecnologías y la estrategia de implementación en respuesta a la especificación validada.
5. **`tasks.md`:** descompone el plan en tareas concretas, verificables y ordenadas, conservando su trazabilidad hacia la especificación.

La jerarquía expresa precedencia normativa y de requisitos; la aclaración es un mecanismo para resolver incertidumbres, no una autorización para contradecir silenciosamente la constitución. Si una aclaración aprobada cambia un requisito, se actualizará la especificación y, cuando corresponda, el plan y las tareas. Los cambios de alcance o las excepciones a esta constitución deben ser explícitos, justificados y aprobados por las personas responsables del proyecto.

## 6. Principios de Calidad y Arquitectura de Software

- Diseñar con separación de responsabilidades y límites claros entre presentación, lógica de negocio y acceso a datos, conforme a la arquitectura definida en `plan.md`.
- Mantener código legible, coherente con las convenciones del repositorio, modular y fácil de probar y mantener. Evitar duplicación y complejidad que no aporte valor al alcance aprobado.
- Preservar la trazabilidad entre requisitos, tareas, cambios, pruebas y resultados. Las decisiones técnicas relevantes y las limitaciones conocidas deben documentarse.
- Proteger la confidencialidad, integridad y disponibilidad de la información mediante controles de acceso acordes con los roles aprobados, validación de entradas y manejo explícito de errores. No registrar secretos ni datos sensibles innecesarios.
- Tratar la carga de evidencias PDF como una operación sensible: validar el tipo y tamaño permitidos, aplicar controles de acceso, evitar la ejecución o interpretación insegura de archivos y asociar cada evidencia con el registro y los metadatos pertinentes. Los criterios concretos de retención, consulta y eliminación deberán ajustarse a las políticas institucionales y requisitos aprobados.
- Mantener una auditoría de las operaciones relevantes sobre recomendaciones y evidencias, incluyendo quién realizó la acción y cuándo, de acuerdo con los requisitos definidos. Los registros de auditoría deben protegerse contra alteraciones no autorizadas y no almacenar información sensible innecesaria.
- Verificar los cambios mediante pruebas proporcionales al riesgo y a los criterios de aceptación. Los resultados reportados deben corresponder a pruebas efectivamente ejecutadas, y los defectos conocidos deben comunicarse con claridad.
- Actualizar la documentación y los artefactos SDD cuando un cambio modifique el comportamiento, la arquitectura, los requisitos o los procedimientos del sistema.
