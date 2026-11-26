# Consumo de la API desde el frontend

Este documento registra cómo el frontend consume la API para la feature **Consulta de recomendaciones**: qué operación del contrato usa, qué servicio la llama, qué componente la presenta y qué pruebas lo verifican.

## Trazabilidad

| Eslabón | Elemento | Fuente |
|---|---|---|
| Feature | F-006 · Consulta del estado de cumplimiento | `feature-map.md` §6 |
| Historia y criterio | HU-02 (consulta del estado) · CA-02.2 (filtrado por estado, unidad y plazo) | `feature-map.md`, F-006 |
| Requisitos | RF-019 (el ejecutor solo ve su unidad) · RNF-003 (autorización por rol y por objeto) · RNF-004 (contrato de respuesta) | `specs/001-seguimiento-recomendaciones/spec.md` |
| Operación OpenAPI | `listarRecomendaciones` · `GET /api/v1/recomendaciones` | `backend/contracts/openapi.yaml` |
| Implementación backend | `RecomendacionListCreateView.get` → `ListRecomendaciones.execute` | `backend/modules/recomendaciones/` |
| Servicio frontend | `listarRecomendaciones(filtros, signal)` | `frontend/src/features/recomendaciones/services/recomendacionesService.ts` |
| Componente | `ConsultaRecomendacionesPage` | `frontend/src/features/recomendaciones/pages/ConsultaRecomendacionesPage.tsx` |
| Ruta de la interfaz | `/recomendaciones/consulta` · roles UAI, Ejecutor, Rectorado y Auditor CGE | `frontend/src/routes.tsx` |
| Pruebas | `recomendacionesService.test.ts` (4) · `ConsultaRecomendacionesPage.test.tsx` (9) | `frontend/src/features/recomendaciones/` |

Los roles de la ruta son los mismos que `ListRecomendaciones.ALLOWED_ROLES` en el backend. El DTI no ve la opción en el menú; si llamara a la API directamente, recibiría 403.

## Correspondencia con el contrato

| Contrato (`listarRecomendaciones`) | Servicio frontend |
|---|---|
| `GET /api/v1/recomendaciones` | `requestEnvelope("/api/v1/recomendaciones?…", { method: "GET" })` |
| Seguridad `bearerAuth` | Cabecera `Authorization: Bearer <JWT>`, agregada por `api/client.ts` |
| `page` (entero ≥ 1, por defecto 1) | `filtros.page` |
| `page_size` (1 a 100, por defecto 25) | `filtros.page_size`; la interfaz ofrece 10, 25, 50 y 100 |
| `state` (enum de 5 estados) | `filtros.state`, tipado con `ESTADOS` |
| `priority` (`ALTA`, `MEDIA`, `BAJA`) | `filtros.priority`, tipado con `PRIORIDADES` |
| `unit_id`, `due_date`, `due_before`, `due_after` | Mismos nombres; fechas en formato `YYYY-MM-DD` |
| `vencida` (booleano) | `filtros.vencida`: `true`, `false` u omitido |
| 200 `RecomendacionesEnvelope` | `{ items: data, pagination: meta.pagination }` |
| 400 `VALIDATION_ERROR` con `errors.fields` | `ApiError` con `status`, `code` y `fields` |
| 401 `AUTHENTICATION_REQUIRED` | `ApiError` 401; se borra la sesión y la aplicación vuelve al login |
| 403 `PERMISSION_DENIED` | `ApiError` 403 |

Los filtros vacíos no se envían. Por ejemplo, con estado "Reabierta" y 10 resultados por página la URL es `/api/v1/recomendaciones?page=1&page_size=10&state=REABIERTA`.

El servicio solo traduce entre la interfaz y la API: no guarda estado ni decide qué mostrar. El componente decide la presentación según el resultado del servicio.

## Estados de la interfaz

| Estado | Cuándo ocurre | Qué ve la persona usuaria |
|---|---|---|
| Carga | Mientras la solicitud está en curso | "Consultando recomendaciones…" y la sección marcada con `aria-busy` |
| Éxito | 200 con resultados | Tabla con número, descripción, unidad, vencimiento y estado; total y página actual |
| Vacío | 200 sin resultados | "No hay recomendaciones que coincidan con los filtros" |
| Validación en la interfaz | "Vence desde" posterior a "Vence hasta" | Mensaje junto a los filtros; no se llama a la API |
| Validación del backend | 400 | "Revise los filtros" y los errores por campo de `errors.fields` |
| Sesión vencida | 401 | Vuelta a la pantalla de inicio de sesión |
| No autorizado | 403 | "Acceso no autorizado" |
| Servidor no disponible | 5xx o sin conexión | Mensaje sin detalle técnico y botón **Reintentar** |

Cada cambio de filtros cancela la consulta anterior con `AbortController`. Así, la tabla siempre corresponde a los filtros que se ven en pantalla.

La validación de fechas en la interfaz solo evita una llamada inútil. El backend vuelve a validar todos los parámetros (`ListRecomendaciones.execute`), porque la API también puede llamarse sin el frontend.

## Comunicación con el backend y CORS

En desarrollo, Vite reenvía `/api` y `/health` al backend (`vite.config.ts`, variable `VITE_BACKEND_PROXY_TARGET`, por defecto `http://127.0.0.1:8000`). Para el navegador, frontend y API comparten el mismo origen, así que no interviene CORS.

Si el frontend se publica en otro origen, se define `VITE_API_BASE` con la URL de la API y ese origen debe agregarse a `DJANGO_CORS_ALLOWED_ORIGINS` en el backend. CORS está limitado a `/api/*` y `/health/*`, y expone las cabeceras `Location` y `Content-Disposition`.

## Ejecución

```powershell
$env:DJANGO_DEBUG="true"; .venv\Scripts\python.exe backend\manage.py runserver
```

```powershell
npm --prefix frontend run dev
```

Abrir `http://127.0.0.1:5173`, entrar con un rol de prueba (UAI, Ejecutor o Rectorado) y elegir **Consulta de recomendaciones**.

Pruebas del frontend:

```powershell
npm --prefix frontend test
```
