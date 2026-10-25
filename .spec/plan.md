# Plan de Arquitectura y Diseño Técnico — Sistema de Seguimiento de Recomendaciones CGE

**Fase**: F1 — Backend REST API
**Fecha**: 2026-10-21
**Estado**: Borrador de planificación
**Base**: `.specify/memory/constitution.md` v1.0.0 · `.spec/specify.md` · `.spec/clarify.md` · `feature-map.md`
**ADRs asociados**: `docs/adr/ADR-0001` a `ADR-0009` (ver §8)

> **Restricción de avance:** conforme a `.spec/clarify.md` §9, este plan **NO DEBE** considerarse definitivo mientras CL-01 (estados), CL-05 (anulación de evidencia) y CL-07 (validez probatoria) permanezcan sin validar. Las decisiones técnicas aquí descritas son agnósticas a esas reglas de negocio y **DEBEN** revalidarse cuando se resuelvan.

---

## 1. Arquitectura General y Patrones de Diseño

### 1.1 Arquitectura por capas (Constitución §II)

Se adopta una arquitectura en cuatro capas con dependencias dirigidas hacia el dominio (DIP):

```text
┌─────────────────────────────────────────────┐
│  Presentación / API (REST, Controllers)      │
├─────────────────────────────────────────────┤
│  Aplicación (Casos de uso / Servicios)       │
├─────────────────────────────────────────────┤
│  Dominio (Entidades, Reglas, Puertos)        │
├─────────────────────────────────────────────┤
│  Infraestructura / Persistencia (Adapters)   │
└─────────────────────────────────────────────┘
        Dependencias:  API → Aplicación → Dominio ← Infraestructura
```

- **Presentación/API:** expone REST, valida entrada, aplica el contrato universal, traduce errores. No contiene reglas de negocio.
- **Aplicación:** orquesta casos de uso y transacciones. Depende de interfaces del dominio.
- **Dominio:** entidades y reglas (ciclo de estados, separación de responsabilidades, plazos). No conoce framework ni base de datos (Constitución §II).
- **Infraestructura:** implementa puertos del dominio (repositorios, almacenamiento de archivos, auditoría). El dominio nunca la importa.

### 1.2 Monolito Modular por capacidades de negocio (Constitución §II)

Módulos delimitados, cada uno con su capa interna:

| Módulo | Responsabilidad | Feature(s) de `feature-map.md` |
|---|---|---|
| **Recomendaciones** | Registro, consulta y ciclo de vida | F-001, F-003, F-004 |
| **Responsables / Asignaciones** | Asignación de unidades y funcionarios | F-001 (subfeature) |
| **Planes de Acción / Tareas** | Tareas de cumplimiento | dentro de F-003 |
| **Evidencias** | Carga, validación y anulación de PDF | F-002 |
| **Auditoría / Trazabilidad** | Registro inmutable de cambios | F-003 (subfeature), transversal |
| **Usuarios / RBAC** | Autenticación y autorización | transversal |
| **Reportes** | Matrices de cumplimiento | F-005 |

Cada módulo **DEBE** exponer una fachada de aplicación y **NO DEBE** acceder directamente a las tablas de otro módulo; la comunicación cruzada se realiza por casos de uso o eventos de dominio.

### 1.3 Aplicación de SOLID (Constitución §III)

| Principio | Aplicación concreta |
|---|---|
| **SRP** | Un caso de uso = una responsabilidad (p. ej. `RegistrarRecomendacion`, `AprobarCumplimiento`). |
| **OCP** | Nuevas transiciones/estados se añaden como reglas extensibles sin modificar el motor de flujo existente. |
| **LSP** | Implementaciones de repositorios y almacenamiento de archivos respetan contratos del dominio. |
| **ISP** | Puertos estrechos por necesidad (p. ej. `AlmacenEvidencias` separado de `RepositorioRecomendaciones`). |
| **DIP** | El dominio define interfaces; la infraestructura las implementa. |

*Sin sobreingeniería (Constitución §II/§III):* no se crean interfaces sin al menos una segunda implementación prevista o un punto claro de inversión (p. ej. almacenamiento local vs. objeto).

---

## 2. Diseño y Contrato de API REST

### 2.1 Recursos y endpoints semánticos (Constitución §IV)

Base: `/api/v1`. Endpoints propuestos (contrato OpenAPI 3.0 en §2.4):

| Método | Ruta | Propósito | Feature |
|---|---|---|---|
| `POST` | `/api/v1/recomendaciones` | Registrar recomendación | F-001 |
| `GET` | `/api/v1/recomendaciones` | Listar/filtrar/paginar | F-004 |
| `GET` | `/api/v1/recomendaciones/{id}` | Consultar detalle + estado | F-004 |
| `POST` | `/api/v1/recomendaciones/{id}/responsables` | Asignar responsables | F-001 |
| `POST` | `/api/v1/recomendaciones/{id}/tareas` | Registrar tarea | F-003 |
| `POST` | `/api/v1/recomendaciones/{id}/transiciones` | Cambiar estado (iniciar, notificar, aprobar, rechazar, reabrir) | F-003 |
| `POST` | `/api/v1/recomendaciones/{id}/evidencias` | Cargar evidencia PDF | F-002 |
| `PATCH` | `/api/v1/evidencias/{id}/anulacion` | Anular evidencia (lógica) | F-002 |
| `GET` | `/api/v1/recomendaciones/{id}/historial` | Historial inmutable | F-003 |
| `POST` | `/api/v1/reportes/matrices-cumplimiento` | Generar matriz (asíncrono) | F-005 |

*Nota:* los endpoints concretos se derivan de `specify.md` §4 (HU-01 a HU-08) y se refinam al generar el contrato OpenAPI.

### 2.2 Contrato Universal de Respuestas (Constitución §V)

Todas las respuestas usan el esquema unificado:

```json
{
  "success": true,
  "message": "Recomendación registrada",
  "data": {},
  "errors": [],
  "meta": {
    "request_id": "uuid-v4",
    "timestamp": "2026-10-21T14:30:00Z",
    "version": "v1",
    "pagination": { "page": 1, "size": 20, "total": 134 }
  }
}
```

- `request_id` se genera por petición y se propaga a los logs `AUDIT` (Constitución §X, §XIV).
- Errores: `errors` contiene objetos `{ "code", "category", "message" }` con categorías Validación/Negocio/Autorización/Infraestructura (Constitución §X).
- Códigos HTTP estándar (200, 201, 400, 401, 403, 404, 409, 422, 500).

### 2.3 Paginación, filtros y ordenamiento (Constitución §IV)

- Paginación por `page`/`size` (o cursor para listados grandes); respuesta en `meta.pagination`.
- Filtros por `estado`, `unidad`, `plazo_desde`/`plazo_hasta`, `prioridad`.
- Ordenamiento estandarizado: `sort=campo,asc|desc` con lista blanca de campos.

### 2.4 Especificación OpenAPI 3.0 (Constitución §IV)

- Contrato en `specs/001-backend-cge/contracts/openapi.yaml` (artefacto por generar en fase de diseño).
- Definiciones de esquemas, respuestas de error estándar, seguridad `bearerAuth` y ejemplos por endpoint.
- El contrato **DEBE** validarse en CI (lint OpenAPI) (Constitución §XIII).

---

## 3. Modelo de Datos e Integridad de Persistencia

> **Agnósticidad:** el esquema se describe a nivel relacional lógico. La elección del motor **DEBE** registrarse en ADR-0003 y confirmar los estados (CL-01) y reglas probatorias (CL-07) antes de congelar el modelo.

### 3.1 Esquema relacional lógico y restricciones

Entidades principales (modelo conceptual en `specify.md` §6):

| Entidad | Claves/atributos lógicos | Integridad |
|---|---|---|
| `recomendacion` | id, descripcion, origen, prioridad, fecha_emision, fecha_limite, estado | PK; `estado` con CHECK de valores permitidos |
| `unidad` | id, nombre | PK, unicidad de nombre |
| `usuario` | id, nombre, rol, unidad_id | FK a `unidad`; rol con CHECK |
| `responsable_asignacion` | recomendacion_id, unidad_id/usuario_id | FK a `recomendacion`, `unidad`; N:M recomendación↔responsable |
| `plan_accion_tarea` | id, recomendacion_id, descripcion, responsable_id | FK a `recomendacion` |
| `evidencia` | id, recomendacion_id, ruta_almacen, tipo (borrador/final), estado (vigente/anulada), mime, tamano, hash | FK a `recomendacion` |
| `historial_cambio` | id, recomendacion_id, actor_id, estado_anterior, estado_nuevo, evidencia_id, ip, timestamp | FK; **append-only** |
| `alerta_vencimiento` | id, recomendacion_id, tipo, fecha | FK a `recomendacion` |

- **Integridad referencial estricta** (Constitución §VI): `ON DELETE RESTRICT` para recomendaciones con evidencias/historial; prohibida la eliminación en cascada del historial.
- Restricciones `CHECK` para estados y roles, alineadas con CL-01/CL-08 una vez validadas.

### 3.2 Transacciones atómicas (Constitución §VI)

Operación compuesta **"carga de evidencia + cambio de estado"** (`En Proceso → En Validación`) **DEBE** ejecutarse en una única transacción: o se persisten ambos (evidencia + historial + estado) o ninguno.

### 3.3 Control de concurrencia (Constitución §VI)

- **Optimista** (por defecto) para actualización de recomendaciones: columna de versión; conflicto → HTTP `409`.
- **Pesimista** (bloqueo de fila) reservado para transiciones críticas de estado que compiten por la misma recomendación.
- Decisión registrada en ADR-0004.

### 3.4 Almacenamiento seguro de archivos (Constitución §VI)

- Metadatos (mime, tamaño, hash, ruta) en base de datos; archivo físico en almacenamiento controlado (volumen local en F1, con puerto para sustituir por almacenamiento de objetos).
- Nombres de archivo generados internamente (UUID); nunca se usa el nombre original como ruta.
- Integridad verificada por hash del contenido.
- Decisión registrada en ADR-0005.

### 3.5 Registro inmutable de auditoría (Constitución §VII)

- `historial_cambio` es **append-only**: sin `UPDATE` ni `DELETE` a nivel de aplicación y de permisos de BD.
- Cada registro incluye actor, rol, IP, timestamp, acción, estado anterior/nuevo y evidencia asociada.
- Protegido contra alteración (usuario de BD sin permisos de modificación sobre esa tabla).
- Decisión registrada en ADR-0006.

---

## 4. Seguridad y Privacidad

### 4.1 Autenticación JWT y RBAC (Constitución §VII)

- Autenticación mediante JWT firmado; el token transporta identidad, rol y unidad.
- Autorización en dos niveles:
  1. **Endpoint:** solo roles habilitados (p. ej. aprobar cumplimiento solo `Validador`).
  2. **Recurso:** un usuario **NO DEBE** gestionar recomendaciones ajenas a su área (RNF-02); se evalúa pertenencia por `unidad_id`.
- Separación de responsabilidades: el actor que registra avance **NO DEBE** aprobar su propio cumplimiento (Constitución §VIII).
- Decisión registrada en ADR-0002.

### 4.2 Sanitización y validación de archivos (Constitución §VII, RNF-03)

- Verificación real de MIME (no solo extensión), límite de tamaño, inspección de cabecera PDF.
- Rechazo de archivos con scripts embebidos o estructuras sospechosas; almacenamiento fuera de rutas ejecutables.
- El archivo nunca se ejecuta ni se interpreta; sola descarga autenticada.
- Límites concretos **NEEDS CLARIFICATION** dependientes de CL-07 (política institucional).

### 4.3 OWASP Top 10 (Constitución §VII)

Controles mapeados: inyección (consultas parametrizadas/ORM con bind), autenticación rota (JWT + expiración + refresh), control de acceso (RBAC a nivel de recurso), configuración segura, exposición de datos (no exponer detalles internos), y logging de fallos de seguridad en nivel `AUDIT`.

---

## 5. Estrategia de Pruebas y Calidad (Constitución §IX)

| Nivel | Alcance | Ejemplos |
|---|---|---|
| **Unitarias** | Reglas de negocio y transiciones de estado | Toda transición no permitida se rechaza; `Cumplida` sin validador se rechaza; cálculo de `Vencida`. |
| **Integración** | API REST, persistencia y carga de archivos | Ciclo completo registrar→notificar→validar; atomicidad evidencia+estado; carga e integridad PDF. |
| **Autorización** | Verificar que usuarios no autorizados no alteran estados | Ejecutor intentando aprobar; usuario de otra área intentando gestionar. |
| **Contrato** | OpenAPI vs. implementación | Esquema de respuesta universal y códigos de error estables. |

- **Definition of Done** (Constitución §IX): pruebas verdes, análisis estático y lint OpenAPI en CI, PR revisado.
- Los casos de prueba **DEBEN** derivarse de los criterios Dado/Cuando/Entonces de `specify.md` §4.

---

## 6. Modelado C4, BPMN y DevOps

### 6.1 Diagramas C4 (Constitución §XI)

Artefactos por generar (Markdown + Mermaid) en `specs/001-backend-cge/`:

- **C4 Nivel 1 — Contexto:** Sistema CGE, actores (UAI, Ejecutores, Rectorado, CGE) y sistemas externos (exportación hacia CGE).
- **C4 Nivel 2 — Contenedores:** API Backend, Base de datos, Almacenamiento de evidencias, Frontend (F2, futuro), Móvil (F3, futuro).
- **C4 Nivel 3 — Componentes:** módulos Recomendaciones, Evidencias, Auditoría, Usuarios/RBAC, Reportes.

### 6.2 Modelo BPMN del ciclo de vida (Constitución §XI)

Modelo BPMN que representa los estados y transiciones de `specify.md` §3.1, con compuertas de decisión en la validación (aprobar/rechazar) y el vencimiento automático. **DEBE** esperar a CL-01/CL-02 antes de considerarse definitivo.

### 6.3 Docker y GitFlow (Constitución §XIII, §XII)

- **Docker:** `Dockerfile` para el backend y `docker-compose` para desarrollo (API + BD + almacenamiento), configuración parametrizada por entorno (ADR-0008).
- **GitFlow:** `main`, `develop`, `feature/*`, `release/*`, `hotfix/*`; PR obligatorio con revisión y CI verde antes de fusionar a `develop`/`main`.
- **CI:** análisis estático, pruebas y lint OpenAPI; gates por rama (ADR-0009).

---

## 7. Estructura del Repositorio (propuesta)

```text
backend/
├── src/
│   ├── api/                  # Capa Presentación/API
│   ├── application/          # Casos de uso
│   ├── domain/               # Entidades, reglas y puertos
│   │   ├── recomendaciones/
│   │   ├── evidencias/
│   │   ├── auditoria/
│   │   └── usuarios/
│   └── infrastructure/       # Persistencia, almacenamiento, JWT
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── contracts/
│   └── openapi.yaml
└── Dockerfile

docs/
├── adr/                      # ADRs (ver §8)
└── diagrams/                 # C4 (Mermaid) y BPMN

docker-compose.yml
```

**Structure Decision:** proyecto único backend con monolito modular; el frontend (F2) y móvil (F3) se incorporarán como módulos de cliente en fases posteriores consumiendo el mismo API (Constitución §IV, §XVI).

---

## 8. Registros de Decisiones Arquitectónicas (ADRs)

Los ADRs se crean en `docs/adr/`:

| ADR | Decisión | Relación |
|---|---|---|
| ADR-0001 | Arquitectura por capas con Monolito Modular | Constitución §II |
| ADR-0002 | Autenticación JWT + RBAC a nivel de endpoint y recurso | Constitución §VII |
| ADR-0003 | Motor de base de datos relacional (pendiente de selección) | Constitución §VI |
| ADR-0004 | Control de concurrencia optimista por defecto, pesimista en transiciones | Constitución §VI |
| ADR-0005 | Almacenamiento de evidencias: metadata en BD, archivo en almacenamiento controlado | Constitución §VI |
| ADR-0006 | Historial de auditoría append-only e inmutable | Constitución §VII |
| ADR-0007 | Contrato Universal de Respuestas JSON | Constitución §V |
| ADR-0008 | Contenedorización con Docker y configuración por entorno | Constitución §XIII |
| ADR-0009 | CI/CD y ramas GitFlow | Constitución §XII–XIII |

---

## 9. Constitution Check

*GATE: verificación de cumplimiento de la Constitución.*

| Principio | Cumple | Observaciones |
|---|---|---|
| §I SDD | Sí | Plan derivado de specify/clarify; pendientes CL-01/05/07 marcados. |
| §II Capas/Modular | Sí | §1.1 y §1.2. |
| §III SOLID | Sí | §1.3. |
| §IV API REST | Sí | §2.1–2.4. |
| §V Contrato respuestas | Sí | §2.2. |
| §VI Persistencia | Sí | §3.1–3.5. |
| §VII Seguridad/Auditoría | Sí | §4; límites de archivo pendientes de CL-07. |
| §VIII Gobernanza | Sí | Modelado en §3.1/§6.2, sujeto a CL-01/05. |
| §IX Calidad/Pruebas | Sí | §5. |
| §X Errores | Sí | §2.2. |
| §XI Modelado | Sí | §6.1–6.2. |
| §XII Colaboración | Sí | §6.3. |
| §XIII DevOps | Sí | §6.3. |
| §XIV Observabilidad | Sí | §2.2 (`request_id`), `AUDIT`. |
| §XV Rendimiento | Sí | §2.3, reportes asíncronos §2.1. |
| §XVI Fases | Sí | §7. |
| §XVII IA | Sí | Sin datos confidenciales; revisión humana pendiente. |

**Conflictos:** ninguno. **Complejidad adicional justificada:** puerto de almacenamiento de archivos (ADR-0005) por la previsión de migrar de local a objeto.

---

## 10. Preguntas pendientes que bloquean el plan definitivo

Heredadas de `.spec/clarify.md` §9:

- **CL-01** (estados definitivos) — bloquea el congelamiento de la matriz de transición y el modelo `recomendacion.estado`.
- **CL-05** (anulación de evidencia) — bloquea el diseño final de `evidencia.estado`.
- **CL-07** (validez probatoria) — bloquea los límites y requisitos de validación de archivos (§4.2).
- **CL-03/CL-04** (reasignación y visibilidad) — afectan reglas RBAC concretas.
- **CL-06** (prórrogas) — si se aprueban, añade capacidad y tabla de prórrogas.

---

## 11. Fases de implementación (propuesta)

| Fase | Entregable | Dependencia |
|---|---|---|
| F1-M1 | Estructura de proyecto, Docker, CI, contrato universal | ADR-0001, 0007, 0008, 0009 |
| F1-M2 | Módulo Usuarios/RBAC y autenticación JWT | ADR-0002 |
| F1-M3 | Módulo Recomendaciones (registro + asignación + consulta) | CL-01 |
| F1-M4 | Módulo Evidencias (carga + anulación) | CL-05, CL-07 |
| F1-M5 | Flujo de estados + Módulo Auditoría | CL-01, CL-02 |
| F1-M6 | Reportes/matrices de cumplimiento | F1-M3, F1-M5 |
