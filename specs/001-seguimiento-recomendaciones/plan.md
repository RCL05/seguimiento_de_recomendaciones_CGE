# Plan de Implementación: Seguimiento de Recomendaciones CGE

**Rama**: `001-seguimiento-recomendaciones` | **Fecha**: 2026-10-19 |
**Especificación**: [spec.md](./spec.md)

**Entrada**: Especificación funcional de `specs/001-seguimiento-recomendaciones/spec.md`

## Resumen

Se implementará SITRA-CGE UNL como un monolito modular con arquitectura limpia en
cuatro capas: Presentación/API, Aplicación, Dominio e Infraestructura. La primera
entrega cubrirá identidad y RBAC, informes y recomendaciones, planes de acción,
evidencias PDF con SHA-256, dictámenes UAI, auditoría, alertas, tablero y matriz de
cumplimiento.

El stack elegido para el proyecto es Python 3.10 como mínimo validado y 3.12 como
objetivo de despliegue, Django REST Framework y PostgreSQL para backend, React con
TypeScript y Vite para frontend, Docker Compose para desarrollo, pytest/Vitest/
Playwright para pruebas y OpenAPI 3.1 para el contrato.
Las integraciones institucionales (SSO, SMTP y almacenamiento de archivos) se
mantendrán detrás de adaptadores configurables.

## Contexto Técnico

**Lenguaje/Versión**: Python 3.10 como mínimo compatible y Python 3.12 como runtime
objetivo; TypeScript para frontend

**Dependencias principales**: Django 5.2, Django REST Framework, Psycopg, pytest,
pytest-django, React, Vite, Vitest, React Testing Library y Playwright

**Almacenamiento**: PostgreSQL para datos transaccionales y almacenamiento de archivos
PDF separado mediante un puerto de almacenamiento; no se almacenarán binarios grandes
directamente en las tablas sin decisión aprobada

**Pruebas**: pytest para backend, Vitest y React Testing Library para frontend,
Playwright para flujos completos, además de contrato API, autorización, integridad
de archivos, concurrencia y tareas programadas

**Plataforma objetivo**: servidor Linux institucional o plataforma equivalente que
soporte el runtime aprobado, PostgreSQL, HTTPS, tareas programadas y SMTP

**Tipo de proyecto**: servicio web institucional con API REST y cliente web

**Objetivos de rendimiento**: 95% de consultas ordinarias del tablero en menos de
3 segundos y 95% de exportaciones de matriz CSV en menos de 5 segundos, medidos
con una carga de referencia de 1.000 recomendaciones, 200 usuarios y 20 consultas
concurrentes.

**Restricciones**: HTTPS, respuestas con envoltura universal, autorización en servidor,
auditoría de operaciones mutativas, PDFs validados, SHA-256, transacciones atómicas,
bloqueo de la recomendación durante cambios críticos y ausencia de secretos en Git

**Escala/Alcance**: cinco perfiles institucionales, dependencias jerárquicas,
informes CGE, recomendaciones, hitos, evidencias, dictámenes, alertas y reportes.
La carga de referencia inicial es 1.000 recomendaciones, 200 usuarios y 20
consultas concurrentes; los límites de producción se revisarán con DTI.

## Verificación de la Constitución

*GATE: aprobado antes de investigación y reevaluado después del diseño.*

- **SDD y trazabilidad**: aprobado; cada decisión, requisito, contrato y prueba se
  enlaza con la especificación y los artefactos de diseño.
- **Arquitectura limpia y SOLID**: aprobado; el dominio no depende de Django, ORM,
  PostgreSQL ni servicios externos.
- **Seguridad y mínimo privilegio**: aprobado; RBAC y autorización a nivel de objeto
  se ejecutan en cada operación.
- **Integridad y auditoría**: aprobado; las evidencias tienen hash verificable y las
  mutaciones producen auditoría protegida.
- **Concurrencia**: aprobado; las transiciones y dictámenes usan transacción y
  bloqueo de la recomendación.
- **API y errores**: aprobado; se conserva la envoltura universal y el catálogo de
  errores de la constitución.
- **Decisiones pendientes**: proveedor de SSO, almacenamiento de archivos, SMTP y
despliegue requieren aprobación explícita, registrada en ADR. El stack base queda
adoptado para el desarrollo académico.

No existen violaciones que requieran una excepción constitucional.

## Estructura del Proyecto

### Documentación de esta funcionalidad

```text
specs/001-seguimiento-recomendaciones/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
├── checklists/
│   └── requirements.md
└── tasks.md                 # Lo generará /speckit-tasks
```

### Código fuente objetivo

```text
backend/
├── config/                  # Configuración, URLs y composición de dependencias
├── core/
│   ├── api/                 # Envoltura universal y filtros de excepciones
│   ├── audit/               # Auditoría y correlación request_id
│   ├── auth/                # Puertos de identidad y autorización
│   └── shared/              # Tipos y utilidades transversales
├── modules/
│   ├── usuarios/
│   │   ├── presentation/
│   │   ├── application/
│   │   ├── domain/
│   │   └── infrastructure/
│   ├── informes_cge/
│   ├── recomendaciones/
│   ├── evidencias/
│   ├── notificaciones/
│   └── reportes/
└── tests/
    ├── unit/
    ├── integration/
    ├── contract/
    ├── security/
    └── concurrency/
```

**Decisión de estructura**: se selecciona un único backend modular. Los modelos
Django se registran en cada módulo para descubrimiento del framework; los
repositorios y adaptadores permanecen en infraestructura. Cada módulo
expone casos de uso y puertos; ningún módulo importa repositorios ORM de otro módulo.
La forma exacta de registrar módulos en Django se resolverá sin mover las fronteras
de dominio.

## Fase 0: Investigación y Decisiones

Las decisiones consolidadas se encuentran en [research.md](./research.md). En resumen:

1. Django REST Framework + PostgreSQL es la decisión adoptada por alineación con el
   prompt, el modelo relacional y las transacciones requeridas. Python 3.10 es el
   mínimo validado; Python 3.12 es el objetivo de despliegue.
2. Los detalles de SSO, SMTP, almacenamiento de PDF y despliegue se abstraen mediante
   puertos y quedan sujetos a aprobación.
3. `SELECT FOR UPDATE` se aplica a la fila de recomendación dentro de la transacción
   de transición, dictamen y ajuste de plazo.
4. SHA-256 se usa para detectar cambios de contenido; autenticidad y protección de
   registros dependen además de permisos, almacenamiento y auditoría.

## Fase 1: Diseño

### Modelo de datos

El modelo normalizado, restricciones y transiciones están en
[data-model.md](./data-model.md). Las entidades principales son Usuario, Rol,
Dependencia, Informe CGE, Recomendación, Hito, Evidencia, Dictamen, Auditoría,
Notificación y Matriz de Cumplimiento.

### Contratos

El contrato OpenAPI 3.1 está en [contracts/openapi.yaml](./contracts/openapi.yaml).
Define el prefijo `/api/v1/`, la envoltura universal, códigos de error, autorización,
operaciones principales, paginación, carga PDF y exportación de matriz CSV UTF-8.

### Validación operativa

Los escenarios ejecutables y prerrequisitos están en [quickstart.md](./quickstart.md).
Incluyen creación de recomendación, bloqueo del salto a `Cumplida`, defensa BOLA,
integridad PDF, auditoría, alertas y concurrencia.

## Decisiones de Arquitectura

### ADR-001: Monolito modular con cuatro capas

- **Estado**: Propuesto.
- **Contexto**: el sistema necesita evolucionar con límites institucionales claros y
  sin distribuir prematuramente operaciones transaccionales.
- **Decisión**: separar Presentación/API, Aplicación, Dominio e Infraestructura dentro
  de un único despliegue modular.
- **Consecuencias**: simplifica transacciones y despliegue; exige disciplina de
  dependencias y pruebas de límites entre módulos.

### ADR-002: SHA-256 para verificación de integridad

- **Estado**: Aprobado por la constitución, pendiente de controles operativos.
- **Contexto**: las evidencias PDF deben permitir detectar modificaciones.
- **Decisión**: calcular SHA-256 al cargar y conservarlo junto con metadatos y auditoría.
- **Consecuencias**: permite verificación reproducible; no prueba autenticidad por sí
  solo ni protege contra alteraciones administrativas de la base de datos.

### ADR-003: Bloqueo pesimista en cambios críticos

- **Estado**: Propuesto.
- **Contexto**: dos solicitudes simultáneas pueden producir estados contradictorios.
- **Decisión**: ejecutar transacciones atómicas y bloquear la recomendación con
  `SELECT ... FOR UPDATE` durante transición, dictamen y ajuste de plazo.
- **Consecuencias**: evita actualizaciones perdidas; requiere límites de tiempo,
  reintentos controlados y pruebas de contención.

### ADR-004: Envoltura universal y errores estandarizados

- **Estado**: Aprobado por la especificación.
- **Contexto**: clientes y auditoría necesitan respuestas previsibles y correlación.
- **Decisión**: todas las respuestas JSON usan `success`, `message`, `data`, `errors`
  y `meta`; los fallos se clasifican mediante el catálogo institucional y se
  correlacionan con `request_id`.
- **Consecuencias**: facilita clientes y observabilidad; las excepciones `204`, `304`
  y `HEAD` deben documentarse explícitamente.

## Matriz de Trazabilidad de Diseño

| Requisito | Componente | Datos | Contrato | Prueba |
| --- | --- | --- | --- | --- |
| RF-001–004 | Usuarios/Auth, configuración | usuarios, unidades | `/auth/login-sso` | integración, RBAC |
| RF-005–006 | Informes y recomendaciones | informes_cge, recomendaciones | `POST /informes`, `POST /recomendaciones` | unidad, integración |
| RF-007 | Plan de acción | planes_accion | `POST /recomendaciones/{id}/plan-accion` | unidad, integración |
| RF-008, RF-020 | Evidencias y transacciones | evidencias | `POST /recomendaciones/{id}/evidencias` | unidad, integridad, concurrencia |
| RF-009–010 | Máquina de estados, dictamen | recomendaciones, dictamenes_uai | `PATCH /recomendaciones/{id}/dictamen` | dominio, integración |
| RF-011–012, RF-021 | Política de plazos, notificaciones | notificaciones, recomendaciones | tarea interna | jobs, reintentos |
| RF-013 | Reportes y tablero | recomendaciones, unidades | consulta de tablero | integración, rendimiento |
| RF-014, RF-018 | Reportes y auditoría | matriz, audit_logs | `POST /reportes/matriz-cge` | contrato, exportación CSV, RBAC |
| RF-015–016 | Core API y errores | request_id, audit_logs | todos los endpoints | contrato, errores |
| RF-017 | Auditoría | audit_logs | interceptor mutativo | integración, seguridad |
| RF-019 | Autorización de objeto | recomendaciones, unidades | consultas y cargas | BOLA/IDOR |
| RNF-001–004 | Core, Evidencias, DB | evidencias, audit_logs | todos | integridad, seguridad |
| RNF-005–006 | Reportes | índices y consultas | tablero y matriz CSV | rendimiento con carga de referencia |
| RNF-007–008 | Notificaciones y Core | notificaciones, logs | respuestas y tareas | resiliencia, privacidad |
| RNF-009 | SDD | artefactos Spec Kit | requisitos y pruebas | revisión de trazabilidad |

## Seguimiento de la Implementación

`/speckit-tasks` debe convertir este plan en tareas ordenadas por dependencia. Las
tareas deben preservar las fronteras de módulos, generar pruebas antes de cerrar cada
caso de uso y enlazar RF/RNF con código, prueba y documentación.

## Complejidad

No se registran violaciones constitucionales. El patrón de repositorios, puertos,
adaptadores y bloqueo pesimista se justifica por los requisitos explícitos de
independencia del dominio, auditoría y consistencia concurrente.
