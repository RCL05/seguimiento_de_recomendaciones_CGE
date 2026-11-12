## Arquitectura de la API

| Característica | Implementación verificada |
|---|---|
| Estilo | REST orientado a recursos (sustantivos en plural; el método HTTP expresa la operación) |
| Prefijo y versión | `/api/v1/` (`config/urls.py::API_V1`); `meta.version = "v1"` |
| Formato | JSON con envoltura universal; excepciones: carga de PDF (`application/pdf`), descarga de PDF y matriz CSV |
| Contrato | OpenAPI **3.0.3** generado con drf-spectacular; publicado en `backend/contracts/openapi.yaml` (réplica en `specs/…/contracts/openapi.yaml`) |
| Documentación viva | Swagger UI en `/api/docs/`, esquema en `/api/schema/` (públicos) |
| Autenticación | `Authorization: Bearer <JWT>` (esquema `bearerAuth`), salvo `POST /sesiones` y `GET /health/` |
| Autorización | Rol en la vista (`require_roles`) + rol y objeto en el caso de uso |
| Paginación | `page` (≥ 1, por defecto 1) y `page_size` (1–100, por defecto 25) en listados; resultado en `meta.pagination` |
| Correlación | Cabecera opcional `X-Request-ID` (UUID); se devuelve en `meta.request_id` |
| CORS | Solo para `/api/*` y `/health/*`; orígenes de `DJANGO_CORS_ALLOWED_ORIGINS`; cabeceras permitidas `authorization`, `content-type`, `x-filename`, `x-evidence-type`, `x-request-id`; expuestas `Location`, `Content-Disposition` |
| Creación | `201 Created` con cabecera `Location` del recurso |

## Recursos

| Recurso | Ruta base | Módulo |
|---|---|---|
| Sesión | `/sesiones` | usuarios |
| Unidades orgánicas | `/unidades` | usuarios |
| Usuarios | `/usuarios` | usuarios |
| Informes CGE | `/informes` | informes_cge |
| Recomendaciones | `/recomendaciones` | recomendaciones |
| Hitos del plan de acción | `/recomendaciones/{id}/hitos` | recomendaciones |
| Dictámenes | `/recomendaciones/{id}/dictamenes` | recomendaciones |
| Evidencias | `/recomendaciones/{id}/evidencias`, `/evidencias/{id}` | evidencias |
| Notificaciones | `/notificaciones`, `/notificaciones/preferencias`, `/notificaciones/configuracion` | notificaciones |
| Indicadores y reportes | `/dashboard/kpis`, `/reportes/tablero`, `/reportes/matriz-cge` | reportes |
| Auditoría | `/auditoria` | reportes |

## Autenticación y autorización (resumen)

1. El cliente obtiene un JWT con `POST /api/v1/sesiones` enviando `{"credential": "<token SSO>"}`.
2. Cada petición posterior envía `Authorization: Bearer <access_token>`; el token expira en 3600 s.
3. `JWTBearerAuthentication` rechaza con **401** si el token falta, expiró, fue alterado o si el rol/unidad cambiaron desde su emisión. La respuesta incluye `WWW-Authenticate: Bearer realm="sitra-cge"`.
4. Un rol no autorizado recibe **403 `PERMISSION_DENIED`**; un recurso de otra unidad o inexistente recibe **404 `RESOURCE_NOT_FOUND`** (y el intento se audita).

Detalle en *Seguridad → Autenticación* y *Seguridad → Autorización*.

## Manejo de errores

| HTTP | Código | Causa típica |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Campos inválidos, JSON mal formado, fecha de hito inválida, archivo no PDF, rechazo sin observaciones |
| 401 | `AUTHENTICATION_REQUIRED` | Falta o es inválido el token |
| 403 | `PERMISSION_DENIED` | El rol no puede ejecutar la operación |
| 404 | `RESOURCE_NOT_FOUND` | Recurso inexistente o de otra unidad |
| 405 | `METHOD_NOT_ALLOWED` | Método no admitido (incluye cabecera `Allow`; se evalúa antes que la autenticación) |
| 409 | `CONFLICT` / `BUSINESS_RULE_VIOLATION` | Transición inválida, duplicado, doble dictamen, evidencia en un estado que no la admite (incluido `PENDIENTE` sin plan) |
| 413 | `PAYLOAD_TOO_LARGE` | PDF mayor que `MAX_PDF_SIZE_BYTES` |
| 415 | `UNSUPPORTED_MEDIA_TYPE` | `Content-Type` no admitido |
| 500 | `INTERNAL_ERROR` | Error no controlado, sin trazas en la respuesta |

## Versionado

La versión mayor está en la ruta (`/api/v1`). No existe todavía una política escrita de deprecación ni una `v2`. El número de versión del contrato (`info.version: 1.0.0`) se define en `SPECTACULAR_SETTINGS["VERSION"]`.
