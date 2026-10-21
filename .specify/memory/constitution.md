# Constitución del Proyecto — Sistema de Seguimiento de Recomendaciones de la Contraloría General del Estado (CGE)

Esta Constitución establece los principios normativos, criterios de calidad, restricciones arquitectónicas y reglas de gobernanza que **DEBEN** cumplirse durante las tres fases del Sistema de Seguimiento de Recomendaciones de la CGE. Es única y transversal a F1 (Backend y API REST), F2 (Frontend web) y F3 (Aplicación móvil). Toda persona que participe en el proyecto **DEBE** acatar este documento.

Las obligaciones se expresan con los términos formales **DEBE** (obligatorio), **NO DEBE** (prohibido) y **DEBERÍA** (recomendado, sujeto a justificación registrada).

**Nota de fuentes:** el prompt de generación solicitó revisar `references/backend/Guia_Didactica_Arquitectura_Backend_SOLID.pdf` y la documentación `docs/01-proyecto/…`, `docs/02-analisis/…`, `docs/03-requisitos/…`. Ninguno de esos archivos existe en el repositorio a la fecha de esta versión. Se registran como ausencias en la sección "Fuentes no disponibles" y esta Constitución se construyó con las fuentes disponibles: `.spec/constitution.md`, `.spec/clarify.md`, `.spec/plan.md`, `.spec/tasks.md`, `README.md`, `docs/problem-definition.md`, `docs/control-questions.md` y `feature-map.md`.

---

## I. Desarrollo Guiado por Especificaciones (SDD) — PRINCIPIO RECTOR

Toda funcionalidad **DEBE** originarse en una especificación antes de escribirse código.

- **DEBE** diferenciarse explícitamente el problema de control, las necesidades de los usuarios, los requisitos del sistema y la solución técnica. No **SE DEBE** presentar una solución técnica como si fuera un requisito de negocio.
- **DEBEN** definirse historias de usuario, reglas de negocio de auditoría y criterios de aceptación comprobables antes de planificar la implementación.
- Las ambigüedades críticas (por ejemplo, quién valida formalmente una recomendación) **DEBEN** clarificarse antes de planificar. No **SE DEBE** implementar requisitos sustantivos basándose solo en supuestos.
- **DEBE** mantenerse trazabilidad entre requisitos, diseño, tareas, código y evidencia de pruebas.
- **DEBE** utilizarse el flujo de Spec Kit: `constitution → specify → clarify → plan → tasks → implement → converge`.
- Toda decisión asistida por IA **DEBE** ser revisada y aprobada por una persona antes de incorporarse.

*Justificación:* el proyecto adoptó SDD para evitar que el sistema dé por "cumplida" una recomendación normativamente rechazada o pendiente, riesgo crítico identificado en `docs/problem-definition.md` §4.

## II. Arquitectura Modular y Separación de Responsabilidades

- **DEBE** aplicarse una arquitectura por capas: Presentación/API, Aplicación, Dominio, Infraestructura/Persistencia.
- Cada capa **DEBE** tener límites claros y **NO DEBE** acceder directamente a responsabilidades de otra capa.
- La lógica del dominio **NO DEBE** depender del framework ni de la base de datos.
- El sistema **DEBE** organizarse por capacidades de negocio (por ejemplo: módulo de Recomendaciones, módulo de Evidencias, módulo de Auditoría/Trazabilidad, módulo de Responsables).
- **DEBE** adoptarse el Monolito Modular como punto de partida técnico, privilegiando alta cohesión y bajo acoplamiento.
- **NO SE DEBE** introducir sobreingeniería (interfaces, clases o indirecciones) sin justificación arquitectónica documentada.

*Justificación:* la separación de capas y módulos protege la independencia del dominio de auditoría y facilita las tres fases del sistema.

## III. Principios SOLID

- **DEBEN** aplicarse estrictamente SRP, OCP, LSP, ISP y DIP en el diseño de servicios y casos de uso.
- Cada caso de uso **DEBE** tener una única responsabilidad de negocio identificable (SRP).
- Las dependencias **DEBEN** invertirse hacia abstracciones del dominio (DIP), no hacia detalles de infraestructura.
- **NO SE DEBE** crear interfaces o clases innecesarias sin justificación arquitectónica.

*Justificación:* SOLID sostiene la mantenibilidad y la testeabilidad exigidas por la naturaleza de control y auditoría del sistema.

## IV. Diseño y Estandarización de API REST (F1)

- Los endpoints **DEBEN** ser semánticos y consistentes respecto a los recursos (por ejemplo, `/api/v1/recomendaciones`, `/api/v1/evidencias`).
- Los contratos **DEBEN** documentarse mediante OpenAPI.
- Los listados **DEBEN** soportar paginación, filtrado (por estado, unidad, plazo) y ordenamiento estandarizado.
- Las operaciones críticas **DEBEN** ser idempotentes cuando corresponda.
- El mismo API backend **DEBE** reutilizarse tanto para el Frontend Web (F2) como para la App Móvil (F3). **NO SE DEBE** duplicar lógica de dominio en los clientes.

*Justificación:* un contrato REST uniforme y documentado garantiza interoperabilidad entre las tres fases.

## V. Contrato Universal de Respuestas

Todas las respuestas de la API **DEBEN** seguir el esquema JSON unificado:

```json
{
  "success": true,
  "message": "string",
  "data": {},
  "errors": null,
  "meta": {
    "request_id": "string",
    "timestamp": "string",
    "version": "string"
  }
}
```

- **DEBEN** usarse códigos HTTP estándar y códigos de error internos estables.
- **NO SE DEBE** exponer detalles internos de infraestructura en las respuestas al cliente.

*Justificación:* un contrato universal simplifica el consumo por web y móvil y estandariza el manejo de errores.

## VI. Persistencia, Integridad y Gestión de Archivos

- **DEBE** garantizarse integridad referencial estricta entre recomendaciones, responsables, acciones y archivos adjuntos.
- Los cambios de estado que involucren carga de evidencia **DEBEN** ejecutarse en transacciones atómicas.
- **DEBE** aplicarse control de concurrencia para evitar actualizaciones sobrepuestas sobre una recomendación.
- **DEBE** definirse una estrategia clara de almacenamiento seguro de los archivos físicos de evidencia y de su metadata asociada.

*Justificación:* la evidencia respalda decisiones de cumplimiento; su integridad y atomicidad son indispensables para la validez de la auditoría.

## VII. Seguridad, Privacidad y Auditoría

- **DEBE** implementarse autenticación segura y autorización basada en roles (RBAC): Administrador, Responsable de Unidad, Validador, Auditor.
- **DEBE** aplicarse control de acceso a nivel de recurso: un usuario **NO DEBE** gestionar recomendaciones ajenas a su área.
- **DEBE** mantenerse un registro inmutable de auditoría que indique quién cambió el estado, cuándo, desde qué IP y qué evidencia adjuntó.
- Los archivos/evidencias subidos **DEBEN** pasar por sanitización y validación estricta (tipo, tamaño, contenido).
- **DEBE** cumplirse el estándar OWASP Top 10.
- **NO SE DEBEN** registrar ni exponer secretos, credenciales o datos personales innecesarios.

*Justificación:* el sistema es una herramienta de control institucional; su credibilidad depende de la seguridad y la trazabilidad verificable.

## VIII. Gobernanza de Recomendaciones y Evidencias (Reglas de Negocio)

- Ninguna recomendación **DEBE** marcarse como "Cumplida" sin la aprobación formal del validador. **DEBE** existir separación clara entre el registro de avance y la validación formal de cumplimiento.
- **DEBE** controlarse las fechas límite y **DEBEN** generarse alertas automatizadas por vencimiento.
- El retiro o anulación de una evidencia **DEBE** ser controlado y **DEBE** conservar obligatoriamente el historial.
- **DEBE** distinguirse claramente entre borradores de avance y entregas finales de evidencias.
- El flujo de estados **DEBE** alinearse con la normativa de la CGE aplicable (referencia inicial: Acuerdo 010-CG-2022).

*Justificación:* es el riesgo crítico del proyecto (`docs/problem-definition.md` §4); estas reglas son el núcleo normativo del seguimiento CGE.

## IX. Calidad y Pruebas Automatizadas

- **DEBEN** existir pruebas unitarias para reglas de negocio y flujos de estado.
- **DEBEN** existir pruebas de integración para API, persistencia y carga de archivos.
- **DEBEN** existir pruebas de autorización que verifiquen que usuarios no autorizados no alteran estados.
- **DEBE** cumplirse una Condición de Terminado (Definition of Done) antes de fusionar código.
- Los resultados de pruebas reportados **DEBEN** corresponder a pruebas efectivamente ejecutadas.

*Justificación:* la calidad verificable es condición para la confianza institucional en el seguimiento.

## X. Gestión de Errores y Diagnóstico

- Los errores **DEBEN** categorizarse como: Validación, Negocio, Autorización e Infraestructura.
- Cada petición **DEBE** tracearse mediante un `request_id` único presente en los logs.
- **NO SE DEBEN** exponer detalles sensibles de infraestructura en mensajes al cliente.

*Justificación:* un diagnóstico uniforme agiliza la operación y evita filtraciones de información.

## XI. Modelado y Documentación

- **DEBEN** elaborarse diagramas C4 (Contexto, Contenedores, Componentes) para la arquitectura general.
- **DEBEN** elaborarse diagramas BPMN/UML que modelen el ciclo de vida y los estados de las recomendaciones.
- Las decisiones arquitectónicas clave **DEBEN** registrarse como ADR en formato Markdown.
- La documentación y los artefactos SDD **DEBEN** actualizarse cuando un cambio modifique comportamiento, arquitectura, requisitos o procedimientos.

*Justificación:* el flujo de estados es el reto central del proyecto; modelarlo explícitamente reduce el riesgo de lógica de negocio.

## XII. Versionamiento y Colaboración

- **DEBE** aplicarse el modelo GitFlow: `main`, `develop`, `feature/*`, `release/*`, `hotfix/*`.
- Todo cambio destinado a `develop` o `main` **DEBE** pasar por un Pull Request con revisión de otra persona y validaciones automatizadas.
- Los commits **DEBEN** ser claros y estar vinculados a tareas e historias de usuario de Spec Kit.
- **NO SE DEBEN** fusionar cambios con conflictos conocidos o fallos sin resolver.

*Justificación:* la colaboración disciplinada sostiene la trazabilidad exigida por SDD.

## XIII. DevOps y Automatización

- **DEBE** configurarse Integración Continua (CI) con análisis estático y ejecución de pruebas.
- La configuración **DEBE** parametrizarse por entorno (desarrollo, pruebas, producción).
- **DEBEN** usarse contenedores Docker para entornos de desarrollo reproducibles.

*Justificación:* entornos reproducibles y CI reducen errores de despliegue entre las fases F1–F3.

## XIV. Observabilidad y Operación

- **DEBE** usarse logging estructurado con niveles de severidad: `INFO`, `WARN`, `ERROR`, `AUDIT`.
- **DEBEN** existir verificaciones de estado de salud (health checks) del sistema.
- **DEBEN** definirse procedimientos de respaldo y recuperación de la base de datos y de los archivos de evidencia.

*Justificación:* la operación continua del sistema de control requiere visibilidad y recuperabilidad.

## XV. Rendimiento y Escalabilidad

- Los listados masivos de recomendaciones **DEBEN** usar paginación y **DEBERÍAN** usar carga diferida.
- La generación de reportes y las descargas de evidencias pesadas **DEBEN** procesarse de forma asíncrona.

*Justificación:* evita degradación del servicio a medida que crece el volumen de recomendaciones y evidencias.

## XVI. Evolución de las Tres Fases

- **F1:** API backend robusto, probado e independiente. **NO DEBE** contener lógica de presentación.
- **F2:** Web consumidora del API, con tableros de control y gestión documental.
- **F3:** Móvil para visualización rápida y captura de evidencias en campo. **NO DEBE** duplicar la lógica del backend.

*Justificación:* la separación por fases permite evolucionar los clientes sin reescribir el núcleo de dominio.

## XVII. Uso Responsable de Inteligencia Artificial

- **DEBE** existir revisión humana obligatoria de todo código o documentación generada con IA antes de incorporarse.
- En cada entregable asistido por IA **DEBEN** declararse las herramientas utilizadas y el tipo de asistencia recibida.
- **NO SE DEBEN** inventar registros, pruebas, aprobaciones de auditoría, fuentes ni resultados.
- **NO SE DEBE** introducir información institucional confidencial, datos personales ni credenciales en servicios de IA sin autorización expresa.

*Justificación:* preserva la honestidad académica y la validez probatoria del sistema.

---

## Jerarquía Normativa y Gobernanza

La jerarquía de precedencia es:

**Constitución > Especificaciones (`specify`) > Planes (`plan`) > Tareas (`tasks`).**

- `constitution.md` **DEBE** ser respetada por todos los demás artefactos y por las decisiones de implementación.
- `clarify.md` **NO** autoriza a contradecir silenciosamente la Constitución; si una aclaración aprobada cambia un requisito, **DEBE** actualizarse la especificación y, cuando corresponda, el plan y las tareas.
- Toda excepción arquitectónica **DEBE** ser explícita, justificada y aprobada, y **DEBE** quedar registrada.
- Toda enmienda a esta Constitución **DEBE** documentarse, aprobarse por las personas responsables y acompañarse de un plan de migración cuando corresponda.
- La Constitución **DEBE** versionarse con versionamiento semántico (`MAJOR.MINOR.PATCH`). Un cambio incompatible o de principio **DEBE** incrementar `MAJOR`; una adición de principio o sección **DEBE** incrementar `MINOR`; una aclaración o redacción **DEBE** incrementar `PATCH`.
- Todo Pull Request **DEBE** verificar el cumplimiento de esta Constitución. La complejidad introducida **DEBE** justificarse.

## Fuentes no disponibles (registro de ausencias)

Al generar esta versión no existían en el repositorio las siguientes fuentes solicitadas por el prompt, por lo que su contenido no pudo aplicarse explícitamente y **DEBE** revisarse cuando se incorporen:

- `references/backend/Guia_Didactica_Arquitectura_Backend_SOLID.pdf`
- `docs/01-proyecto/descripcion-proyecto.md`
- `docs/02-analisis/identificacion-actores.md`
- `docs/02-analisis/mapa-actores.md`
- `docs/02-analisis/fundamentos-sdd.md`
- `docs/02-analisis/preguntas-clarificacion.md`
- `docs/03-requisitos/requisitos-iniciales.md`

Fuentes efectivamente utilizadas: `.spec/constitution.md`, `.spec/clarify.md`, `.spec/plan.md`, `.spec/tasks.md`, `README.md`, `docs/problem-definition.md`, `docs/control-questions.md`, `feature-map.md`.

## Preguntas pendientes de clarificación

- ¿Cuáles son los estados definitivos del ciclo de vida de una recomendación? El prompt sugiere "Pendiente, En Proceso, Cumplida, Vencida, Reabierta", pero `.spec/clarify.md` §1 lo deja abierto y **DEBE** confirmarse con la normativa CGE.
- ¿Qué acciones concretas y con qué atribuciones tiene cada rol (Administrador, Responsable de Unidad, Validador, Auditor)? El detalle de permisos **DEBE** precisarse antes de F1.
- ¿El acervo probatorio es completamente inmutable o se admite anulación con historial conservado? El principio VIII admite anulación controlada; **DEBE** confirmarse contra la normativa.
- ¿Qué normativa específica de la CGE (además del Acuerdo 010-CG-2022) rige los estados, plazos y validaciones? **DEBE** recopilarse antes de especificar.
- ¿Qué políticas institucionales aplican a la retención, consulta y eliminación de evidencias?
- ¿Quién es el requirente formal que aprueba esta Constitución y las futuras enmiendas?

**Version**: 1.0.0 | **Ratified**: 2026-10-21 | **Last Amended**: 2026-10-21
