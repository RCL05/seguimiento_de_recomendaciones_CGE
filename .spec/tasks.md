# Backlog de Implementación — Fase 1 (Backend REST API)

**Proyecto**: Sistema de Seguimiento de Recomendaciones CGE
**Input**: `.spec/plan.md`, `.spec/specify.md`, `.spec/clarify.md`, `.specify/memory/constitution.md`
**Fecha**: 2026-10-21
**Estado**: Borrador — no iniciar tareas bloqueadas por clarificaciones pendientes

## Trazabilidad y convenciones

- **Historia**: HU-xx de `specify.md` §4.
- **Requisito**: RF/RNF de `specify.md`; reglas de `constitution.md`.
- **Plan**: sección de `.spec/plan.md` (p. ej. `plan.md §3.3`).
- **[P]**: tarea paralelizable (archivo distinto, sin dependencia).
- **[BLOQUEADA]**: no debe iniciarse hasta resolver la clarificación indicada (`clarify.md` §9).
- **DoD por tarea**: verificable y explícito en cada ítem.

> **Bloqueos vigentes** (`.spec/clarify.md` §9): CL-01 (estados), CL-05 (anulación de evidencia) y CL-07 (validez probatoria) deben validarse antes de congelar las tareas marcadas **[BLOQUEADA]**.

---

## Fase 1 — Configuración Inicial y DevOps (Setup)

**Propósito**: estructura por capas, contenedores y andamiaje transversal.
**Trace**: `plan.md §1`, `§6.3`, `§7`; Constitución §II, §XIII.

- [ ] **T001** Crear la estructura de carpetas del monolito modular (`backend/src/{api,application,domain/{recomendaciones,evidencias,auditoria,usuarios},infrastructure}` y `backend/tests/{unit,integration,contract}`).
      *Trace:* plan.md §7. *DoD:* árbol de directorios creado y versionado con archivos marcadores (`.gitkeep`).
- [ ] **T002** [P] Inicializar el proyecto backend y declarar dependencias base (framework, ORM/migraciones, test runner).
      *Trace:* plan.md §7, ADR-0003. *DoD:* el proyecto compila/arranca en vacío y `README` documenta los comandos.
- [ ] **T003** [P] Configurar linting, formateo y análisis estático.
      *Trace:* Constitución §XIII. *DoD:* comando de lint pasa sin errores sobre el esqueleto.
- [ ] **T004** Configurar `Dockerfile` del backend y `docker-compose` (API + BD + almacenamiento de evidencias).
      *Trace:* plan.md §6.3; ADR-0008. *DoD:* `docker compose up` levanta los servicios y la API responde un health check.
- [ ] **T005** [P] Configurar gestión por entornos (dev/test/prod) mediante variables de entorno y archivos de ejemplo sin secretos.
      *Trace:* Constitución §XIII; ADR-0008. *DoD:* la app lee configuración por entorno y no hay secretos versionados.
- [ ] **T006** Implementar el **Contrato Universal de Respuestas** JSON (`success`, `message`, `data`, `errors`, `meta{request_id,timestamp,version}`).
      *Trace:* plan.md §2.2; ADR-0007; Constitución §V. *DoD:* prueba unitaria verifica el esquema en respuestas 2xx y 4xx/5xx.
- [ ] **T007** Implementar middleware de manejo global de errores con categorías (Validación, Negocio, Autorización, Infraestructura) y códigos estables.
      *Trace:* plan.md §2.2; Constitución §X. *DoD:* prueba verifica que cada categoría retorna estructura y código HTTP correctos sin exponer detalles internos.
- [ ] **T008** Implementar middleware de `request_id` y logging estructurado con niveles `INFO/WARN/ERROR/AUDIT`.
      *Trace:* plan.md §2.2, §6; Constitución §X, §XIV. *DoD:* cada petición genera `request_id` propagado a los logs.
- [ ] **T009** Configurar pipeline de CI (análisis estático + pruebas + lint OpenAPI) y ramas GitFlow.
      *Trace:* plan.md §6.3; ADR-0009; Constitución §XII, §XIII. *DoD:* la pipeline corre en un PR y bloquea el merge si falla.

---

## Fase 2 — Módulo de Autenticación y Seguridad (RBAC)

**Propósito**: identidad, roles y autorización por recurso.
**Trace**: `specify.md` §2, RNF-02; `plan.md §4.1`; Constitución §VII.

- [ ] **T010** Modelar entidades `usuario`, `unidad` y `rol` (Administrador, Responsable de Unidad, Validador, Auditor) con migraciones.
      *Trace:* specify.md §2, §6; plan.md §3.1. *DoD:* migración aplica y revierte; `CHECK` de roles válido. **[BLOQUEADA por CL-08]**
- [ ] **T011** Implementar autenticación JWT (emisión, firma, expiración y validación).
      *Trace:* plan.md §4.1; ADR-0002. *DoD:* pruebas cubren token válido, expirado y manipulado.
- [ ] **T012** [P] Implementar middleware de autorización por rol a nivel de endpoint.
      *Trace:* plan.md §4.1; Constitución §VII. *DoD:* prueba de autorización rechaza rol no habilitado (403).
- [ ] **T013** Implementar autorización a nivel de recurso (pertenencia a unidad) en los casos de uso.
      *Trace:* RNF-02; plan.md §4.1. *DoD:* prueba verifica que un usuario no gestiona recomendaciones de otra unidad.
- [ ] **T014** Implementar la regla de separación de responsabilidades (quien registra avance no aprueba su cumplimiento).
      *Trace:* specify.md §3.2, CA-06.3; Constitución §VIII. *DoD:* prueba rechaza la autoaprobación.
- [ ] **T015** Implementar middleware de `request_id`/logging con usuario autenticado (actor + IP) para trazabilidad.
      *Trace:* plan.md §4.1; Constitución §VII. *DoD:* los logs `AUDIT` incluyen actor, rol, IP y `request_id`.

---

## Fase 3 — Módulo de Recomendaciones y Ciclo de Vida (Core Business)

**Propósito**: entidades del dominio, máquina de estados y casos de uso centrales.
**Trace**: `specify.md` §3, §4 (HU-01, HU-03, HU-04, HU-06); `plan.md §1, §3.3`; Constitución §II, §III, §VIII.

### Entidades y dominio

- [ ] **T016** [P] Modelar la entidad de dominio `Recomendacion` (descripción, origen, prioridad, fechas, estado) con migración.
      *Trace:* specify.md §6; plan.md §3.1. *DoD:* pruebas unitarias de validación de campos obligatorios (CA-01.2, CA-01.3). **[BLOQUEADA por CL-01]**
- [ ] **T017** [P] Modelar `responsable_asignacion` (N:M recomendación↔responsable) y `plan_accion_tarea`.
      *Trace:* specify.md §3, §6; plan.md §3.1. *DoD:* migraciones con integridad referencial estricta verificadas. **[BLOQUEADA por CL-03]**
- [ ] **T018** Implementar la **máquina de estados** con la matriz de transición de `specify.md` §3.1 y rechazo de transiciones no permitidas.
      *Trace:* specify.md §3.1; plan.md §1.3 (OCP). *DoD:* pruebas unitarias cubren cada transición válida e inválida. **[BLOQUEADA por CL-01, CL-02]**

### Casos de uso

- [ ] **T019** Implementar caso de uso **RegistrarRecomendacion** (estado inicial `Pendiente`, fecha límite obligatoria).
      *Trace:* HU-01, CA-01.1–01.3; plan.md §1.3. *DoD:* pruebas unitarias + endpoint funcional; registro en historial.
- [ ] **T020** Implementar caso de uso **AsignarResponsables** (permitir múltiples responsables sin perder los previos).
      *Trace:* HU-03, CA-03.1–03.3; plan.md §1.3. *DoD:* pruebas unitarias + endpoint; cambio registrado en historial.
- [ ] **T021** Implementar caso de uso **RegistrarAvance / NotificarCumplimiento** (`En Proceso → En Validación`).
      *Trace:* HU-04, HU-05 (paso), CA-04.1; plan.md §3.2. *DoD:* prueba verifica transición y atomicidad con evidencia.
- [ ] **T022** Implementar caso de uso **AprobarCumplimiento** / **RechazarCumplimiento** (solo Validador).
      *Trace:* HU-06, CA-06.1–06.3; plan.md §4.1. *DoD:* pruebas de autorización y transición correcta. **[BLOQUEADA por CL-01]**
- [ ] **T023** Implementar cálculo automático de estado `Vencida` y generación de alertas por fecha límite.
      *Trace:* specify.md §3.3; Constitución §VIII. *DoD:* prueba de job/tarea que marca vencidas y genera alerta. **[BLOQUEADA por CL-06]**
- [ ] **T024** Implementar control de concurrencia optimista (versión; conflicto → 409) y pesimista en transiciones críticas.
      *Trace:* plan.md §3.3; ADR-0004. *DoD:* prueba de concurrencia simulada devuelve 409.

### Pruebas del core

- [ ] **T025** [P] Pruebas unitarias de reglas de transición de estados y validaciones normativas.
      *Trace:* Constitución §IX; plan.md §5. *DoD:* cobertura de la matriz de transición al 100% de ramas.
- [ ] **T026** [P] Pruebas unitarias de la regla de separación de responsabilidades y control de acceso a recurso.
      *Trace:* Constitución §IX; RNF-02. *DoD:* casos de rechazo verificados.

---

## Fase 4 — Módulo de Evidencias y Almacenamiento

**Propósito**: carga segura, sanitización y vinculación transaccional de evidencias.
**Trace**: `specify.md` §3.4, §4 (HU-05), RNF-03; `plan.md §3.2, §3.4, §4.2`; Constitución §VI, §VII.

- [ ] **T027** [P] Modelar la entidad `Evidencia` (recomendación, ruta, tipo borrador/final, estado vigente/anulada, mime, tamaño, hash) con migración.
      *Trace:* specify.md §3.4, §6; plan.md §3.1. *DoD:* migración con integridad referencial. **[BLOQUEADA por CL-05]**
- [ ] **T028** Implementar el puerto `AlmacenEvidencias` y su adaptador de almacenamiento controlado (nombres UUID, fuera de rutas ejecutables).
      *Trace:* plan.md §3.4; ADR-0005. *DoD:* prueba guarda y recupera un archivo sin usar el nombre original.
- [ ] **T029** Implementar **CargarEvidencia** con validación de MIME real, límite de tamaño e inspección de cabecera PDF.
      *Trace:* HU-05, CA-05.1–05.3; RNF-03; plan.md §4.2. *DoD:* pruebas aceptan PDF válido y rechazan formato/tamaño inválidos. **[BLOQUEADA por CL-07]**
- [ ] **T030** Implementar distinción borrador de avance vs. entrega final (CA-05.4).
      *Trace:* HU-05, CA-05.4; Constitución §VIII. *DoD:* prueba verifica el etiquetado del carácter en el registro.
- [ ] **T031** Implementar transacción atómica **evidencia + cambio de estado** (`En Proceso → En Validación`).
      *Trace:* plan.md §3.2; Constitución §VI. *DoD:* prueba de fallo parcial no deja estado inconsistente.
- [ ] **T032** Implementar **AnularEvidencia** lógica (estado `Anulada`, conserva historial, no eliminación física).
      *Trace:* specify.md §3.4, CA-07.3; Constitución §VIII. *DoD:* prueba verifica anulación y preservación del rastro. **[BLOQUEADA por CL-05]**
- [ ] **T033** [P] Pruebas de integración de carga de archivos e integridad por hash.
      *Trace:* plan.md §5. *DoD:* pruebas verdes en entorno con almacenamiento real (contenedor).

---

## Fase 5 — Módulo de Auditoría y Trazabilidad

**Propósito**: registro inmutable y consulta de historial.
**Trace**: `specify.md` §3.4, §4 (HU-07); `plan.md §3.5`; Constitución §VII, §VIII.

- [ ] **T034** Modelar el historial `historial_cambio` en modo **append-only** (actor, rol, IP, timestamp, acción, estado anterior/nuevo, evidencia).
      *Trace:* plan.md §3.5; ADR-0006; Constitución §VII. *DoD:* migración + permisos de BD que impiden UPDATE/DELETE.
- [ ] **T035** Instrumentar todos los casos de uso para escribir el registro de auditoría correspondiente.
      *Trace:* specify.md §3.4; Constitución §VII. *DoD:* prueba verifica que cada cambio de estado/evidencia deja registro.
- [ ] **T036** Implementar endpoint **GET `/api/v1/recomendaciones/{id}/historial`** (solo lectura, rol Auditor/Validador).
      *Trace:* HU-07, CA-07.1; plan.md §2.1. *DoD:* prueba de autorización + integración retorna el historial completo.
- [ ] **T037** [P] Pruebas de inmutabilidad del historial (imposibilidad de modificar/eliminar registros).
      *Trace:* HU-07, CA-07.2; Constitución §VII. *DoD:* intento de UPDATE/DELETE falla en capa BD y aplicación.

---

## Fase 6 — API REST, OpenAPI y Pruebas de Integración

**Propósito**: exposición de endpoints, contrato y verificación de DoD global.
**Trace**: `plan.md §2.1, §2.4, §5`; Constitución §IV, §IX.

- [ ] **T038** [P] Exponer endpoints de Recomendaciones (`POST/GET /api/v1/recomendaciones`, `GET /{id}`, `/responsables`, `/tareas`, `/transiciones`).
      *Trace:* HU-01, HU-03, HU-04, HU-06; plan.md §2.1. *DoD:* todos responden con el Contrato Universal y validan entrada.
- [ ] **T039** [P] Exponer endpoints de Evidencias (`POST /recomendaciones/{id}/evidencias`, `PATCH /evidencias/{id}/anulacion`).
      *Trace:* HU-05; plan.md §2.1. *DoD:* respuestas conformes al contrato y errores categorizados.
- [ ] **T040** Exponer endpoint de Reportes/matriz de cumplimiento (procesamiento asíncrono).
      *Trace:* HU-08; plan.md §2.1, §XV. *DoD:* generación asíncrona con estado consultable.
- [ ] **T041** Implementar paginación, filtros por estado/unidad/plazo y ordenamiento con lista blanca.
      *Trace:* RNF-08; plan.md §2.3; Constitución §IV. *DoD:* pruebas verifican `meta.pagination` y orden seguro.
- [ ] **T042** Generar el contrato **OpenAPI 3.0** en `backend/contracts/openapi.yaml` con esquemas, errores y seguridad `bearerAuth`.
      *Trace:* plan.md §2.4; Constitución §IV. *DoD:* lint OpenAPI pasa en CI y coincide con los endpoints implementados.
- [ ] **T043** [P] Pruebas de contrato (OpenAPI vs. implementación) para todas las respuestas.
      *Trace:* plan.md §5. *DoD:* ninguna respuesta viola el contrato.
- [ ] **T044** [P] Pruebas de integración de los flujos completos (registrar → asignar → avance → evidencia → validar → historial).
      *Trace:* specify.md §4; plan.md §5. *DoD:* flujo end-to-end verde en CI.
- [ ] **T045** Verificación global de la **Definition of Done** (pruebas verdes, análisis estático, lint OpenAPI, PR revisado).
      *Trace:* Constitución §IX; plan.md §5. *DoD:* checklist DoD completa y documentada en el PR de release de F1.

---

## Dependencias y orden de ejecución

- **Fase 1 (Setup)** no tiene dependencias; base para todo.
- **Fase 2 (RBAC)** depende de Fase 1; habilita autorización en el resto.
- **Fase 3 (Core)** depende de Fase 2; es el MVP funcional.
- **Fase 4 (Evidencias)** depende de Fase 3 (T021, T031).
- **Fase 5 (Auditoría)** depende de Fase 3 y 4 (instrumentar casos de uso).
- **Fase 6 (API/OpenAPI)** depende de Fases 3–5.

### Bloqueos por clarificación (`clarify.md` §9)

| Clarificación | Bloquea tareas |
|---|---|
| CL-01 (estados) | T016, T018, T022 |
| CL-02 (reapertura) | T018 |
| CL-03 (reasignación) | T017 |
| CL-05 (anulación de evidencia) | T027, T032 |
| CL-06 (prórrogas) | T023 |
| CL-07 (validez probatoria) | T029 |
| CL-08 (atribuciones por rol) | T010 |

## Estrategia incremental (MVP)

1. Fases 1–2 completas → infraestructura y seguridad listas.
2. Fase 3 → MVP: registrar, asignar y gestionar estados de recomendaciones.
3. Fase 4 → evidencias.
4. Fase 5 → auditoría.
5. Fase 6 → contrato y validación integral de F1.
