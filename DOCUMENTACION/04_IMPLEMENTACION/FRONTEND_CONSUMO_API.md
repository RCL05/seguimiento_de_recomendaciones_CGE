# Consumo de la API desde el frontend

Este documento registra cómo el frontend consume la API para la feature **Consulta de recomendaciones** (APE-006): qué operación del contrato usa, qué servicio la llama, qué componente la presenta, qué estados muestra y cómo se verifica.

## Trazabilidad

| Eslabón | Elemento | Fuente | Responsable |
|---|---|---|---|
| Feature | F-006 · Consulta del estado de cumplimiento | `feature-map.md` §6 | — |
| Historia y criterio | HU-02 (consulta del estado) · CA-02.2 (filtrado por estado, unidad y plazo) | `feature-map.md`, F-006 | — |
| Requisitos | RF-019 (el ejecutor solo ve su unidad) · RNF-003 (autorización por rol y por objeto) · RNF-004 (contrato de respuesta) | `specs/001-seguimiento-recomendaciones/spec.md` | — |
| Operación OpenAPI | `listarRecomendaciones` · `GET /api/v1/recomendaciones` · seguridad `bearerAuth` | `backend/contracts/openapi.yaml` | — |
| Implementación backend | `RecomendacionListCreateView.get` → `ListRecomendaciones.execute` | `backend/modules/recomendaciones/` | — |
| Configuración | URL base (`VITE_API_BASE`), proxy de Vite y CORS | `frontend/.env.example`, `frontend/vite.config.ts` | Integrante 1 |
| Modelos | `RecommendationQuery`, `Recommendation`, `PaginatedResult<T>` | `frontend/src/models/domain.types.ts` | Integrante 2 |
| Cliente HTTP | `requestResult`, `serializeQuery`, `ApiError` | `frontend/src/services/apiClient.ts` | Integrante 2 |
| Servicio | `recommendationsService.listPage(filters)` | `frontend/src/services/recommendations.service.ts` | Integrante 2 |
| Componente y ruta | [Componente de consulta y su ruta] | [`frontend/src/features/…`] | Integrante 3 |
| Estados, pruebas y evidencias | Estados de la interfaz, casos PI-01 a PI-09 | Este documento, `frontend/docs/evidencias/` | Integrante 4 |

Los roles que pueden consultar son los de `ListRecomendaciones.ALLOWED_ROLES` en el backend: UAI, Ejecutor, Rectorado y Auditor CGE. El DTI recibe 403.

## Correspondencia con el contrato

| Contrato (`listarRecomendaciones`) | Frontend |
|---|---|
| `GET /api/v1/recomendaciones` | `recommendationsService.listPage(filters)` → `requestResult("/api/v1/recomendaciones" + serializeQuery(filters))` |
| Seguridad `bearerAuth` | `apiClient.ts` agrega `Authorization: Bearer <JWT>` desde la sesión |
| `page` (entero ≥ 1, por defecto 1) | `RecommendationQuery.page` |
| `page_size` (1 a 100, por defecto 25) | `RecommendationQuery.page_size` |
| `state` (`PENDIENTE`, `EN_PROCESO`, `EN_VALIDACION`, `REABIERTA`, `CUMPLIDA`) | `RecommendationQuery.state` |
| `priority` (`ALTA`, `MEDIA`, `BAJA`) | `RecommendationQuery.priority` |
| `unit_id`, `due_date`, `due_before`, `due_after` | Mismos nombres en `RecommendationQuery`; fechas en formato `YYYY-MM-DD` |
| `vencida` (booleano) | `RecommendationQuery.vencida` |
| 200 `RecomendacionesEnvelope`: `data` y `meta.pagination` | `PaginatedResult<Recommendation>`: `{ items, pagination }` |
| 400 `VALIDATION_ERROR` | `ApiError` con `status` 400 y `code` |
| 401 `AUTHENTICATION_REQUIRED` | `ApiError` 401; el cliente borra la sesión y emite `sitra:session-expired` |
| 403 `PERMISSION_DENIED` | `ApiError` 403 |

## Estados de la interfaz

Cada estado corresponde a una respuesta documentada en el contrato:

| Estado | Cuándo ocurre | Qué debe ver la persona usuaria |
|---|---|---|
| Carga | Mientras la solicitud está en curso | "Consultando recomendaciones…" |
| Éxito | 200 con resultados | Tabla con número, descripción, unidad, vencimiento y estado; total y página |
| Vacío | 200 con `data: []` | "No hay recomendaciones que coincidan con los filtros" |
| Validación en la interfaz | Datos incoherentes antes de enviar, por ejemplo "Vence desde" posterior a "Vence hasta" | Mensaje junto al filtro; no se llama a la API |
| Validación del backend | 400 `VALIDATION_ERROR` | "Revise los filtros" y el detalle de `errors.detail` |
| Sesión vencida | 401 | Vuelta a la pantalla de inicio de sesión |
| No autorizado | 403 | "Su rol no tiene permiso para consultar recomendaciones" |
| Servidor no disponible | 5xx o sin conexión | Mensaje sin detalle técnico y opción de **Reintentar** |

**Criterios:**

- Hay un único estado activo a la vez. Por eso el estado se modela como un solo valor y no como varios booleanos que podrían contradecirse.
- No se ofrece reintentar ante un 400 ni un 401, porque repetir la misma solicitud da el mismo resultado: hay que corregir el filtro o volver a iniciar sesión.
- El 5xx no muestra el mensaje técnico: al usuario no le sirve una traza ni un "Error HTTP 500".
- La lista vacía no es un error: es un 200 válido sin resultados.

La validación en la interfaz solo evita una llamada inútil. El backend vuelve a validar todos los parámetros (`ListRecomendaciones.execute`), porque la API también puede llamarse sin el frontend.

## Dependencias detectadas al integrar

| Punto | Efecto | Responsable sugerido |
|---|---|---|
| `serializeQuery` solo omite los valores `undefined`; una cadena vacía se envía | Si el componente pasa `unit_id: ""` o `priority: ""`, el backend responde 400 ("Los filtros unit_id y priority no pueden estar vacíos"). El componente debe convertir los filtros vacíos en `undefined` | Integrante 3 |
| `ApiError` no conserva `errors.fields` | Un 400 solo puede mostrar el mensaje general, no el error de cada campo | Integrante 2 |
| `PaginatedResult.pagination` puede ser `null` | El componente debe tolerarlo, aunque esta operación siempre envía `meta.pagination` | Integrante 3 |

## Pruebas de integración

Con el backend en modo desarrollo (`DJANGO_DEBUG=true`) y el frontend en `http://localhost:5173`:

| ID | Caso | Resultado esperado |
|---|---|---|
| PI-01 | Operación en Swagger (`/api/docs/`) con un token de `POST /sesiones` | 200 con `data` y `meta.pagination` |
| PI-02 | Consulta desde la interfaz como UAI | Tabla; en DevTools, `GET /api/v1/recomendaciones?…` con 200 y `Authorization: Bearer …` |
| PI-03 | Carga con la red limitada (DevTools → "Slow 3G") | Estado de carga visible |
| PI-04 | Filtro por estado | URL con `state=REABIERTA` y sin filtros vacíos |
| PI-05 | Filtros sin resultados | Estado vacío |
| PI-06 | Validación: fechas invertidas en la interfaz; `page_size=500` en Swagger | Mensaje sin solicitud en Network; 400 `VALIDATION_ERROR` |
| PI-07 | Sesión vencida: borrar `sitra.session` en DevTools → Application | 401 y vuelta al login |
| PI-08 | Backend detenido | Servidor no disponible y **Reintentar** |
| PI-09 | Consulta como Ejecutor | Solo recomendaciones de su unidad (DEP-A) |

Las capturas se guardan en `frontend/docs/evidencias/` con el ID del caso en el nombre (por ejemplo, `PI-02-exito.png`).

En desarrollo, sin `DJANGO_SECRET_KEY`, el backend genera una clave nueva en cada arranque y los tokens anteriores dejan de valer. Para PI-08 conviene arrancarlo con una clave fija de desarrollo; si no, al reintentar la aplicación vuelve al login.
