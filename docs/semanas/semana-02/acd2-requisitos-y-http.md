# ACD 2: requisitos y fundamentos de HTTP

**Proyecto:** SITRA-CGE UNL (Proyecto 4, Seguimiento de recomendaciones CGE)

Este documento registra las 13 actividades de la sesión. Los requisitos completos están
en [`spec.md`](../../../specs/001-seguimiento-recomendaciones/spec.md). Los ejemplos HTTP
son solicitudes y respuestas reales de la API, capturadas el 2026-11-05 contra un
servidor local con datos de prueba. Los tokens y los identificadores largos se abreviaron.

## Actividad 1: revisar problema, actores, alcance y preguntas

| Elemento | Resultado de la revisión | Dónde está |
|---|---|---|
| Problema | Falta de trazabilidad en el cumplimiento de las recomendaciones de la CGE | `spec.md`, Contexto del problema |
| Actores | UAI, ejecutor, Rectorado, auditor CGE, DTI, CGE, SSO y correo | `spec.md`, Actores |
| Alcance | Registro, plan, evidencias, dictamen, vencimientos, tablero, matriz y auditoría | `spec.md`, Alcance y restricciones |
| Preguntas | Resueltas en Clarifications; las abiertas están en Preguntas pendientes | `spec.md` y `.spec/clarify.md` |

## Actividad 2: requisitos funcionales

Se formularon 24 requisitos funcionales (RF-001 a RF-024) con sintaxis EARS. Agrupados
por capacidad:

| Capacidad | Requisitos |
|---|---|
| Identidad y administración | RF-001, RF-002, RF-003 |
| Registro de informes y recomendaciones | RF-005, RF-006 |
| Plan de acción y evidencias | RF-007, RF-008, RF-024 |
| Flujo de estados y dictamen | RF-009, RF-010, RF-023 |
| Plazos y alertas | RF-004, RF-011, RF-012, RF-021 |
| Consulta y reportes | RF-013, RF-014, RF-018 |
| Reglas transversales de la API | RF-015, RF-016, RF-017, RF-019, RF-020, RF-022 |

## Actividad 3: requisitos no funcionales

| Atributo pedido | Requisito | Cómo se verifica |
|---|---|---|
| Seguridad | RNF-002, RNF-003, RNF-008 | Pruebas de BOLA/IDOR, roles y seguridad de logs |
| Rendimiento | RNF-005, RNF-006 | Percentil 95 bajo 3 y 5 segundos. Aún sin medición real |
| Disponibilidad | RNF-007 | Un fallo de correo no revierte la operación de negocio |
| Usabilidad | RNF-011, SC-009 | Evaluación con usuarios representativos. Pendiente |
| Accesibilidad | RNF-012 | Etiquetas, uso con teclado y estado no solo por color |
| Mantenibilidad | RNF-013 | Pruebas de dominio y capas separadas |
| Interoperabilidad | RNF-010 | OpenAPI 3.0.3 validado y CSV UTF-8 |
| Integridad y auditabilidad | RNF-001, RNF-002 | Verificación SHA-256 y bitácora |

## Actividad 4: revisión de la redacción

Criterios aplicados: claro, específico, pertinente, verificable y consistente con el alcance.

| Requisito | Problema encontrado | Corrección o estado |
|---|---|---|
| RF-009 | Nombraba 7 estados que no coincidían con el flujo acordado | Corregido: 5 estados y HTTP 409 ante una transición no definida |
| RF-012 | "En Mora" como estado bloqueaba el cumplimiento tardío | Corregido: vencimiento como indicador y notificación única |
| RF-007 | La fecha del hito era imposible de cumplir con el plazo vencido | Corregido: regla dentro y fuera de plazo |
| RF-010 | No decía que las observaciones son obligatorias | Corregido: "DEBE exigir observaciones" |
| RNF-005, RNF-006 | "Carga institucional definida" no está cuantificada | **Pendiente:** definir volumen con la UAI |
| RF-014 | "Según el Acuerdo No. 010-CG-2022" no indica qué columnas exige | **Pendiente:** validar con la UAI |

## Actividad 5: caso de uso representativo

**Caso de uso: dar cumplimiento a una recomendación**

- **Actores:** ejecutor (principal) y UAI.
- **Precondición:** la recomendación está registrada y asignada a la unidad del ejecutor.
- **Flujo principal:**
  1. El ejecutor registra un hito. La recomendación pasa a En Proceso.
  2. El ejecutor carga un PDF. El sistema calcula el SHA-256 y la pasa a En Validación.
  3. La UAI revisa la evidencia y la aprueba.
  4. La recomendación pasa a Cumplida y la operación queda auditada.
- **Flujos alternativos:**
  - La UAI rechaza con observaciones: vuelve a En Proceso y el ejecutor corrige.
  - El archivo no es PDF o supera 30 MB: se rechaza y el estado no cambia.
  - El plazo vence: la recomendación queda marcada como vencida, conserva su estado y puede cumplirse tarde.
  - Un ejecutor de otra unidad la consulta: recibe 404 y el intento queda registrado.

## Actividad 6: historias de usuario y criterios de aceptación

| Historia | Actor | Prioridad | Criterios en `spec.md` |
|---|---|---|---|
| HU-1 Registrar y asignar recomendaciones | UAI | P1 | 3 escenarios |
| HU-2 Gestionar plan y evidencias | Ejecutor | P1 | 3 escenarios |
| HU-3 Revisar, aprobar o devolver evidencias | UAI | P1 | 5 escenarios |
| HU-4 Supervisar riesgos y vencimientos | Rectorado | P2 | 5 escenarios |
| HU-5 Auditar y exportar el cumplimiento | UAI y auditor CGE | P2 | 3 escenarios |
| HU-6 Administrar identidad y configuración | DTI | P3 | 3 escenarios |

Ejemplo (HU-4, escenario 4):

> **Dado** que el ejecutor entregó una evidencia a tiempo y sigue sin dictamen,
> **cuando** pasa la fecha de vencimiento,
> **entonces** la recomendación no se considera vencida y la UAI puede dictaminar.

## Actividad 7: funcionamiento básico de HTTP

Registro de una recomendación:

```http
POST /api/v1/recomendaciones HTTP/1.1
Content-Type: application/json
Authorization: Bearer <token>

{
  "report_id": "7e805c02-...",
  "number": "R-01",
  "description": "Actualizar el reglamento de bienes.",
  "unit_id": "DEP-A",
  "legal_days": 90,
  "due_date": "2027-01-30",
  "priority": "ALTA"
}
```

```http
HTTP/1.1 201 Created
Content-Type: application/json
Location: /api/v1/recomendaciones/4bc790b9-...
Allow: GET, POST, HEAD, OPTIONS

{
  "success": true,
  "message": "Recomendación creada",
  "data": {
    "id": "4bc790b9-...",
    "number": "R-01",
    "unit_id": "DEP-A",
    "state": "PENDIENTE",
    "vencida": false
  },
  "errors": null,
  "meta": { "request_id": "3c5de0ff-...", "version": "v1", "pagination": null }
}
```

(El cuerpo de la respuesta se resumió: también incluye plazo, prioridad y descripción.)

| Elemento | En este ejemplo | Función |
|---|---|---|
| Método | `POST` | Crear un recurso en la colección |
| URL | `/api/v1/recomendaciones` | Identifica la colección, en la versión 1 de la API |
| Cabeceras de solicitud | `Content-Type`, `Authorization` | Formato del cuerpo e identidad del cliente |
| Cuerpo de solicitud | JSON con los datos | Información para crear el recurso |
| Código de estado | `201 Created` | El recurso se creó |
| Cabeceras de respuesta | `Location`, `Content-Type` | Dónde está el recurso nuevo y en qué formato responde |
| Cuerpo de respuesta | Envoltura universal | Resultado, datos y metadatos |

## Actividad 8: métodos HTTP

| Método | Semántica | Uso en el proyecto |
|---|---|---|
| GET | Consultar, sin modificar | Listados, detalle, tablero y matriz CSV |
| POST | Crear o iniciar una operación | Informes, recomendaciones, hitos, evidencias, dictámenes |
| PUT | Reemplazar una representación | Preferencias y configuración de notificaciones |
| PATCH | Modificar parcialmente | Reabrir una recomendación, anular una evidencia, cambiar rol o unidad de un usuario |
| DELETE | Eliminar | **No se usa:** las evidencias se anulan lógicamente para conservar la trazabilidad |

Dos decisiones que se pueden defender:

- La matriz usa `GET` porque solo lee datos.
- El dictamen usa `POST /dictamenes` porque crea un recurso nuevo, no modifica uno existente.

## Actividad 9: códigos de estado

| Código | Significado | Caso real en el proyecto |
|---|---|---|
| 200 OK | Operación exitosa | `GET /recomendaciones` |
| 201 Created | Recurso creado | `POST /recomendaciones`, con `Location` |
| 204 No Content | Éxito sin cuerpo | **No se usa:** todas las operaciones devuelven datos |
| 400 Bad Request | Datos inválidos | Faltan campos o `legal_days` es 0 |
| 401 Unauthorized | Sin autenticación válida | Petición sin token o credencial incorrecta |
| 403 Forbidden | Autenticado sin permiso | Un ejecutor intenta crear una recomendación |
| 404 Not Found | No existe o no es visible | Recurso inexistente, o de otra unidad (BOLA/IDOR) |
| 405 Method Not Allowed | Método no admitido | `PUT /recomendaciones/{id}`, con `Allow` |
| 409 Conflict | Conflicto con el estado actual | Número duplicado o dictamen sobre una recomendación ya cumplida |
| 413 Content Too Large | Archivo demasiado grande | PDF de más de 30 MB |
| 422 Unprocessable Content | Entidad no procesable | **No se usa:** la constitución del proyecto asigna 400 a las validaciones |
| 500 Internal Server Error | Fallo inesperado | Mensaje genérico, sin trazas ni SQL |

Diferencia clave para la defensa, con respuestas reales:

```http
GET /api/v1/recomendaciones HTTP/1.1

HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer realm="sitra-cge"

{ "success": false, "message": "Se requiere un token Bearer válido.",
  "errors": { "code": "AUTHENTICATION_REQUIRED" } }
```

```http
POST /api/v1/recomendaciones HTTP/1.1
Authorization: Bearer <token de un ejecutor>

HTTP/1.1 403 Forbidden

{ "success": false, "message": "Solo el rol UAI puede realizar esta operación.",
  "errors": { "code": "PERMISSION_DENIED" } }
```

- **401:** el servidor no sabe quién eres.
- **403:** sabe quién eres, pero no tienes permiso.
- **404 por BOLA:** a un ejecutor de otra unidad se le responde "La recomendación no existe.", para no revelar que el recurso existe.

## Actividad 10: solicitudes y respuestas en JSON

Toda respuesta JSON usa la misma envoltura, con cinco campos:

| Campo | Éxito | Error |
|---|---|---|
| `success` | `true` | `false` |
| `message` | Mensaje para el cliente | Motivo del error |
| `data` | Resultado | `null` |
| `errors` | `null` | Código y detalle |
| `meta` | `request_id`, `timestamp`, `version`, `pagination` | Igual |

Un error de validación indica cada campo con problemas:

```json
{
  "success": false,
  "message": "number: Este campo es requerido.",
  "data": null,
  "errors": {
    "code": "VALIDATION_ERROR",
    "detail": "number: Este campo es requerido.",
    "fields": {
      "number": ["Este campo es requerido."],
      "legal_days": ["Asegúrese de que este valor es mayor o igual a 1."]
    }
  }
}
```

(El campo `fields` se resumió. `meta` se omitió en este ejemplo.)

La descarga de la matriz CSV y de los PDF no usa la envoltura, porque el contenido es binario.

## Actividad 11: cabeceras relevantes

| Cabecera | Propósito | Uso en el proyecto |
|---|---|---|
| Content-Type | Formato del cuerpo | `application/json`, `application/pdf`, `text/csv` |
| Accept | Formato que el cliente prefiere | El cliente puede enviar `application/json` |
| Authorization | Credenciales del cliente | `Bearer <JWT>` |
| Location | Dirección del recurso creado | En las respuestas 201 |
| ETag | Versión de una representación, para caché y concurrencia | **No implementada:** la concurrencia se controla con bloqueo de fila en el servidor |
| Allow | Métodos admitidos | En la respuesta 405 |
| WWW-Authenticate | Cómo autenticarse | En la respuesta 401 de las rutas protegidas |

**Hallazgo de esta revisión:** el 401 de `POST /auth/login-sso` no envía
`WWW-Authenticate`, y RFC 9110 lo exige para toda respuesta 401. Está pendiente de corregir.

## Actividad 12: CORS

El navegador bloquea que una página lea respuestas de otro origen (esquema, dominio y
puerto) si el servidor no lo autoriza. Afecta al proyecto porque el frontend corre en
`localhost:5173` y la API en `127.0.0.1:8000`. En desarrollo Vite lo evita con un proxy;
un frontend desplegado aparte o la aplicación móvil sí lo necesitan.

Como las peticiones usan `Authorization`, el navegador envía primero una consulta previa
(*preflight*):

```http
OPTIONS /api/v1/recomendaciones HTTP/1.1
Origin: http://localhost:5173
Access-Control-Request-Method: POST
Access-Control-Request-Headers: authorization,content-type

HTTP/1.1 200 OK
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Headers: accept, authorization, content-type, x-filename, x-evidence-type, x-request-id
Access-Control-Allow-Methods: DELETE, GET, OPTIONS, PATCH, POST, PUT
```

Un origen no autorizado (`https://sitio-externo.example`) no recibe
`Access-Control-Allow-Origin`, así que su navegador bloquea la lectura. CORS protege al
navegador: no reemplaza la autenticación. La lista de orígenes se configura con
`DJANGO_CORS_ALLOWED_ORIGINS`.

## Actividad 13: socialización y retroalimentación

Registrar aquí lo ocurrido en la sesión. No se debe llenar con observaciones que no se
hayan recibido.

| Observación recibida | Quién la hizo | Decisión | Cambio realizado |
|---|---|---|---|
| [Completar] | [Completar] | [Completar] | [Completar] |
| [Completar] | [Completar] | [Completar] | [Completar] |

Decisión ya tomada por el equipo y que conviene presentar para validar:

| Tema | Decisión | Dónde se refleja |
|---|---|---|
| Vencimiento | Es un indicador y no un estado (opción 2) | `spec.md`: Clarifications, RF-012 y catálogo de estados |
