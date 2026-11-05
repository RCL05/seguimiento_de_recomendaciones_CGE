<!--
Informe de impacto de sincronización
- Cambio de versión: 1.0.1 -> 1.1.0
- Principios modificados: se amplían los principios de especificaciones, arquitectura,
  seguridad, calidad y trazabilidad para incorporar el texto adjunto.
- Secciones agregadas: Contexto y Propósito del Proyecto; Módulos y Estructura del
  Monolito Modular; Comunicación con APIs y Contrato Universal; Organización
  Centralizada de Errores; Sintaxis de Requisitos y Criterios de Aceptación;
  Versionado y Convenciones Git; Gestión de Contexto en SDD.
- Secciones eliminadas: ninguna.
- Pendientes: verificar la vigencia y
  aplicabilidad del marco legal; confirmar Django, PostgreSQL, ORM, SSO institucional,
  estructura definitiva del repositorio y proveedor SMTP antes de hacerlos obligatorios.
-->

# Constitución de SITRA-CGE UNL

## Principios Fundamentales

### I. Propósito Institucional, Legal y Auditable
SITRA-CGE UNL es el Sistema de Trazabilidad y Seguimiento de Recomendaciones de la
Contraloría General del Estado para la Universidad Nacional de Loja. El sistema DEBE
reemplazar la gestión manual y dispersa mediante un flujo de cumplimiento oportuno,
verificable, auditable y trazable.

El diseño DEBE considerar el artículo 92 de la Ley Orgánica de la Contraloría General
del Estado (LOCGE) y el Acuerdo No. 010-CG-2022 de la CGE, incluyendo acciones,
cronogramas y medios de verificación. La aplicabilidad, vigencia e interpretación
jurídica de estas normas DEBEN verificarse con las instancias competentes antes de
codificar obligaciones legales definitivas.

El sistema DEBE permitir el seguimiento completo de una recomendación, la consulta
auditable de la información en un máximo de tres clics cuando la interfaz lo permita
y la eliminación de registros manuales dispersos sin evidencia verificable.

### II. Desarrollo Dirigido por Especificaciones
Toda capacidad DEBE especificarse antes de implementarse. Una especificación DEBE
contener contexto, requisitos funcionales y no funcionales, restricciones, escenarios
de aceptación y criterios de verificación. Cada implementación y prueba DEBE poder
trazarse hasta un requisito, una decisión arquitectónica o una obligación legal
verificada.

El flujo obligatorio de trabajo es:

`specify -> clarify -> plan -> analyze -> implement -> converge`

La versión instalada de Spec Kit y sus comandos disponibles DEBEN inspeccionarse antes
de utilizarse; NO DEBEN inventarse comandos ni asumirse artefactos no presentes en el
repositorio.

### III. Arquitectura Limpia y Principios SOLID
El sistema DEBE organizarse como un monolito modular evolutivo, salvo que una decisión
arquitectónica aprobada registre una alternativa. La arquitectura DEBE separar
estrictamente estas cuatro capas:

- **Presentación/API:** recibe HTTP, valida entradas mediante DTOs o serializadores,
  autentica y autoriza y aplica el contrato universal de respuestas. NO DEBE contener
  reglas de negocio ni consultas SQL directas.
- **Aplicación/Casos de Uso:** coordina flujos transaccionales, servicios,
  autorizaciones y puertos. DEBE depender de abstracciones y NO DEBE acoplarse a
  detalles de HTTP, frameworks, ORM o base de datos.
- **Dominio:** contiene entidades puras, objetos de valor, invariantes, políticas y
  máquinas de estado. DEBE ser independiente de bases de datos, frameworks y
  tecnologías de infraestructura.
- **Infraestructura:** implementa adaptadores de persistencia, almacenamiento de
  archivos, SMTP, tareas programadas y servicios externos.

SOLID es obligatorio:

- **SRP:** cada módulo o servicio DEBE responder a un solo actor o responsabilidad de
  negocio;
- **OCP:** las variaciones DEBEN resolverse mediante estrategias e interfaces sin
  alterar innecesariamente las reglas estables del dominio;
- **LSP:** las implementaciones DEBEN ser sustituibles sin efectos secundarios
  incompatibles;
- **ISP:** los protocolos e interfaces DEBEN ser pequeños y específicos; y
- **DIP:** aplicación y dominio DEBEN depender de abstracciones, no de implementaciones
  concretas.

### IV. Integridad del Estado, las Evidencias y la Trazabilidad
El ciclo de vida de las recomendaciones DEBE representarse mediante una máquina de
estados explícita con los estados **Pendiente**, **En Planificación**, **En
Ejecución**, **En Revisión Interna**, **Cumplida**, **Rechazada/Corrección** y **En
Mora**. Cada transición DEBE definir precondiciones, roles autorizados, eventos
registrables y respuesta ante fallos.

Una recomendación NO DEBE pasar a **Cumplida** sin haber pasado por **En Revisión
Interna** y sin contar con al menos una evidencia PDF validada por la Unidad de
Auditoría Interna (UAI). Una evidencia rechazada DEBE activar el flujo de corrección
y conservar la trazabilidad de sus revisiones. Las transiciones inválidas DEBEN
rechazarse con HTTP 409 y NO DEBEN producir cambios parciales.

Cada PDF DEBE validarse por tipo MIME real, extensión, contenido y tamaño máximo
configurado. El sistema DEBE calcular y persistir un hash SHA-256 junto con los
metadatos necesarios para verificar la integridad. DEBE detectar discrepancias entre
el archivo almacenado y el hash registrado. El hash por sí solo NO DEBE considerarse
prueba de autenticidad ni protección contra alteraciones de la base de datos; también
son obligatorios el control de acceso, almacenamiento protegido, auditoría y
detección de cambios.

Toda operación mutativa DEBE generar un registro de auditoría, incluyendo creación,
actualización, eliminación lógica, asignaciones, cambios de estado, carga y
validación de evidencias y modificación de plazos. Cada registro DEBE incluir, como
mínimo, `usuario_id`, `fecha_hora`, `ip_origen` cuando esté disponible, `request_id`,
entidad e identificador afectados, operación, estado anterior, estado nuevo y
resultado. Los cambios de negocio y su auditoría DEBEN ser transaccionales cuando sea
necesario para evitar inconsistencias. Los registros DEBEN estar protegidos contra
modificaciones y eliminaciones no autorizadas.

### V. Seguridad, Mínimo Privilegio y Defensa en Profundidad
La autenticación DEBE integrarse con el mecanismo institucional aprobado, como SSO
mediante LDAP/CAS, o utilizar sesiones HttpOnly o tokens Bearer con rotación y
caducidad estrictas cuando esa sea la decisión aprobada.

La autorización DEBE combinar RBAC con autorización a nivel de objeto para prevenir
BOLA/IDOR, incluido OWASP API1:2023. Un Ejecutor de Unidad DEBE consultar, modificar
y cargar evidencias únicamente de recomendaciones asignadas expresamente a su propia
dependencia. La autorización DEBE ejecutarse en el servidor para cada operación y
recurso; los controles de la interfaz NO constituyen una frontera de seguridad.

El modelo DEBE contemplar, como mínimo, administración del sistema, ejecución por
dependencia, revisión de evidencias y supervisión o auditoría institucional,
ajustados a los roles reales del proyecto. Cada endpoint DEBE validar entradas,
proteger sesiones o tokens, manejar archivos de forma segura y registrar eventos de
seguridad.

NO DEBEN almacenarse credenciales, claves, tokens ni contraseñas en Git. Los archivos
`.env` con secretos DEBEN excluirse mediante `.gitignore`; los despliegues DEBEN usar
variables de entorno o un gestor seguro de secretos. Los logs NO DEBEN registrar
contraseñas, tokens, datos personales sensibles ni consultas SQL directas.

### VI. Calidad Verificable, Concurrencia y Confiabilidad Operativa
Cada regla de dominio, caso de uso y transición relevante DEBE contar con pruebas
automatizadas. DEBEN cubrirse pruebas unitarias de dominio, integración con
persistencia y servicios externos, API, autorización por rol y dependencia,
integridad de archivos, concurrencia y tareas programadas.

Los casos positivos y negativos DEBEN incluir datos inválidos, permisos insuficientes,
recursos inexistentes, conflictos HTTP 409, fallos de correo, reintentos, evidencias
rechazadas o alteradas, notificaciones duplicadas y operaciones concurrentes.

Los cambios de estado, reservas de plazos y cargas de evidencias DEBEN ejecutarse en
transacciones atómicas. Cuando el ORM y la base de datos seleccionados lo soporten,
las operaciones críticas DEBEN usar bloqueos pesimistas de fila, como
`select_for_update`, o un control de concurrencia equivalente. La implementación DEBE
prevenir condiciones de carrera, actualizaciones perdidas y transiciones
contradictorias.

Las tareas programadas DEBEN evaluar los plazos y enviar alertas SMTP cuando falten
15 días o menos para el vencimiento y no exista evidencia presentada que cumpla las
condiciones configuradas. “Presentada” DEBE definirse separadamente de “validada”.
El cambio a **En Mora** DEBE ocurrir solo cuando se cumplan las condiciones
temporales y de negocio. Las tareas DEBEN ser idempotentes, observables, tolerantes a
reintentos y resistentes a notificaciones duplicadas; además, DEBEN registrar
ejecuciones y errores y definir explícitamente zona horaria, frecuencia y escalamiento.

## Contexto, Módulos y Restricciones Técnicas

### Estructura del Monolito Modular
Los límites lógicos de los módulos DEBEN ser claros y verificables en el árbol del
repositorio. La estructura objetivo es:

```text
backend/
├── config/                  # Configuración global, URLs y settings
├── core/                    # Respuestas, excepciones, middleware y auditoría
├── apps/
│   ├── usuarios/            # Identidad, RBAC y estructura orgánica UNL
│   ├── informes_cge/        # Registro de exámenes especiales de la CGE
│   ├── recomendaciones/     # Estados, plazos y asignaciones
│   └── evidencias/          # PDFs y hashes SHA-256
├── docs/                    # C4, OpenAPI y portal Quarto
└── tests/                   # Pruebas unitarias, integración, contrato y seguridad
```

Esta estructura es una guía arquitectónica y DEBE ajustarse a la tecnología
confirmada sin perder sus límites. Los módulos DEBEN comunicarse únicamente mediante
contratos de servicio de la capa de aplicación o eventos internos. Un módulo NO DEBE
acceder directamente al ORM o a la base de datos de otro módulo.

El alcance inicial incluye registrar recomendaciones y responsables, registrar
informes o exámenes especiales de la CGE, gestionar cronogramas, cargar evidencias
PDF, aprobar evidencias, mantener trazabilidad y exportar matrices de cumplimiento.
Quedan fuera la sincronización en tiempo real con la base de datos de la CGE y la
gestión de responsabilidades penales o judiciales.

El lenguaje, framework, base de datos, almacenamiento, despliegue, SSO y proveedor
SMTP DEBEN registrarse en una decisión arquitectónica antes de fijarse como
configuración definitiva. PostgreSQL, Django, un ORM, `transaction.atomic` y
`select_for_update` son opciones previstas por el texto fuente; solo son obligaciones
operativas cuando el equipo confirme esas tecnologías.

### Comunicación con APIs y Contrato Universal
La API DEBE seguir un estilo REST bajo el prefijo `/api/v1/`. DEBEN utilizarse
semánticamente `GET`, `POST`, `PUT`, `PATCH` y `DELETE`. El uso de `QUERY` para
búsquedas con cuerpo JSON NO DEBE introducirse sin una decisión documentada sobre
compatibilidad, intermediarios y clientes.

La especificación OpenAPI 3.1.x DEBE ser el contrato verificable de la API cuando el
artefacto sea adoptado por el proyecto. DEBE mantenerse sincronizada con la
implementación mediante pruebas automáticas.

Toda respuesta JSON DEBE usar esta envoltura:

```json
{
  "success": true,
  "message": "Mensaje claro y descriptivo para el cliente",
  "data": {},
  "errors": null,
  "meta": {
    "request_id": "UUID-v4",
    "timestamp": "ISO-8601 UTC",
    "version": "v1",
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total_items": 100,
      "total_pages": 10
    }
  }
}
```

Una respuesta con `success=true` DEBE tener `errors=null`. Una respuesta con
`success=false` DEBE tener `data=null` y un código HTTP 4xx o 5xx. Las excepciones
legítimas son `204 No Content`, `304 Not Modified` y peticiones `HEAD`.

La API DEBE usar estos códigos:

| Código | Significado |
| --- | --- |
| 200 | Operación exitosa |
| 201 | Recurso creado |
| 400 | Solicitud mal formada o validación fallida |
| 401 | Usuario no autenticado |
| 403 | Usuario sin permisos suficientes |
| 404 | Recurso inexistente o no visible por política de divulgación |
| 409 | Conflicto de negocio o transición inválida |
| 500 | Error interno no controlado |

### Organización Centralizada de Errores
El sistema DEBE diferenciar errores esperados de dominio de fallos técnicos no
previstos de infraestructura. El catálogo institucional DEBE usar identificadores
`UPPER_SNAKE_CASE`:

- `VALIDATION_ERROR` (400): campos, formatos o tipos inválidos;
- `AUTHENTICATION_REQUIRED` (401): token o sesión ausente o expirada;
- `PERMISSION_DENIED` (403): permisos insuficientes sobre el recurso;
- `RESOURCE_NOT_FOUND` (404): entidad inexistente o no visible;
- `BUSINESS_RULE_VIOLATION` o `CONFLICT` (409): regla o transición incumplida; y
- `INTERNAL_ERROR` (500): fallo inesperado del servidor o base de datos.

Un manejador global DEBE traducir las excepciones al contrato universal y, cuando el
contrato sea adoptado, alinearlas con RFC 9457 Problem Details. Todo fallo DEBE
registrarse con `request_id` para correlacionar observabilidad. Los errores 500 NO
DEBEN exponer stack traces, SQL ni detalles técnicos al cliente.

## Requisitos, Versionado y Flujo de Trabajo

### Sintaxis EARS y Criterios BDD
Los requisitos DEBEN usar la sintaxis EARS:

- **Ubicuo:** “El sistema DEBE [acción]”.
- **Dirigido por eventos:** “Cuando [evento], el sistema DEBE [acción]”.
- **Dirigido por estados:** “Mientras [estado], el sistema DEBE [acción]”.
- **Condicional:** “Si [precondición], el sistema DEBE [acción]”.
- **Caso no deseado:** “Si [condición de error], entonces el sistema DEBE [respuesta]”.

Cada requisito DEBE complementarse con escenarios BDD verificables en formato
`Given / When / Then`, incluyendo casos positivos, negativos y de autorización cuando
corresponda.

### Versionado Semántico y Git
El producto DEBE seguir SemVer 2.0.0:

- **MAJOR:** cambio incompatible en contrato público o comportamiento;
- **MINOR:** nueva funcionalidad compatible; y
- **PATCH:** corrección de errores o parche de seguridad.

La API DEBE versionarse mediante `/api/v1/`. La versión de la API NO DEBE cambiar por
parches internos; solo DEBE incrementarse ante cambios incompatibles del contrato
JSON.

El repositorio DEBE usar GitFlow:

- `main`: producción protegida;
- `develop`: integración continua;
- `feature/<nombre>`: nuevas funcionalidades; y
- `hotfix/<nombre>`: parches urgentes de producción.

Los cambios en `main` y `develop` DEBEN realizarse mediante Pull Requests con revisión
y verificaciones automáticas exitosas. Los commits DEBEN seguir Conventional Commits
con el formato `tipo(módulo): descripción corta`, por ejemplo:
`feat(recomendaciones): validar máquina de estados`.

### Gestión de Contexto en Spec Kit
Los artefactos del flujo SDD son:

- `.specify/memory/constitution.md`: gobierno y principios no negociables;
- `specs/<feature>/spec.md`: historias, requisitos EARS y criterios BDD;
- `specs/<feature>/clarify.md`: ambigüedades resueltas;
- `specs/<feature>/plan.md`: arquitectura, ER, OpenAPI y ADRs;
- `specs/<feature>/tasks.md`: tareas atómicas y dependencias; y
- artefactos de análisis y convergencia generados por las herramientas disponibles.

La trazabilidad DEBE mantenerse desde la norma legal verificada hasta el requisito
EARS, escenario BDD, contrato OpenAPI, tarea, prueba automatizada, commit y
documentación técnica. Ningún cambio DEBE considerarse completo si rompe esa cadena
sin una excepción aprobada.

## Desarrollo, Documentación y Puertas de Calidad

El proyecto DEBE seguir Docs as Code. Los cambios de arquitectura, flujo de negocio,
autorización o contratos DEBEN actualizar documentación técnica, diagramas C4,
OpenAPI y portal Quarto cuando esos artefactos existan.

La integración continua DEBE ejecutar lint, análisis estático disponible, pruebas,
controles de seguridad y detección de secretos. Una Pull Request DEBE aportar
trazabilidad, pruebas relevantes, cobertura de estados y evidencias cuando aplique,
controles de seguridad, actualización documental o justificación de no modificación
y notas de migración para cambios de esquema o contrato.

## Gobernanza

Esta constitución es el documento de gobierno de mayor jerarquía. Si otra práctica
entra en conflicto con ella, DEBE resolverse a favor de esta constitución o
registrarse una excepción aprobada antes de continuar.

Toda modificación DEBE identificar la sección afectada, registrar impactos en
requisitos, código, pruebas, documentación y operación, incluir un plan de migración
cuando corresponda, ser aprobada por responsables técnicos e institucionales y
comunicarse al equipo.

La versión de esta constitución sigue semver:

- **MAJOR:** elimina o redefine un principio de forma incompatible;
- **MINOR:** agrega un principio o amplía materialmente el gobierno; y
- **PATCH:** aclara, corrige redacción o realiza cambios no semánticos.

El cumplimiento DEBE revisarse durante especificación, diseño, Pull Request y
validación de lanzamiento. Las revisiones DEBEN comprobar invariantes de dominio,
autorización, auditoría, integridad de evidencias, concurrencia, errores, pruebas,
documentación y secretos. Las excepciones DEBEN ser explícitas, documentadas,
aprobadas, justificadas con controles compensatorios y limitadas en el tiempo cuando
sea posible.

La constitución DEBE revisarse cuando cambien la arquitectura, la base legal, la
seguridad, el ciclo de vida, los contratos de integración o el flujo SDD.

**Versión**: 1.1.1 | **Ratificada**: 2026-10-20 | **Ultima modificacion**: 2026-10-20
