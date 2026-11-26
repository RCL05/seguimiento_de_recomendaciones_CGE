# Frontend React - SITRA-CGE UNL

Aplicación existente en React, TypeScript y Vite. La configuración de la APE 6
reutiliza sus rutas, pantallas y cliente `src/api/client.ts`.

## Desarrollo local

Se recomienda Node.js 22, la versión utilizada por Docker Compose y CI.
Desde `frontend/`:

```powershell
npm ci
Copy-Item .env.example .env.local
npm run dev
```

En bash, usar `cp .env.example .env.local` para copiar la plantilla.
Si `.env.local` ya existe, conservarlo y editar sus valores. El backend debe estar
activo en otra terminal; consultar la guía de ejecución del [repositorio](../README.md).

Vite utiliza el puerto `5173` y falla si está ocupado, para evitar cambiar a un
origen que Django no tenga permitido. Reiniciar Vite después de cambiar variables.

| Variable                    | Valor local             | Uso                                                                    |
| --------------------------- | ----------------------- | ---------------------------------------------------------------------- |
| `VITE_API_BASE`             | Vacío                   | Base de las solicitudes del navegador; las rutas ya incluyen `/api/v1` |
| `VITE_BACKEND_PROXY_TARGET` | `http://127.0.0.1:8000` | Destino de `/api` y `/health` en el servidor de desarrollo             |

`vite.config.ts` carga `.env`, `.env.local` y los archivos del modo mediante
`loadEnv`. Las variables del proceso tienen prioridad: por eso Compose conserva
su destino `http://backend:8000` aunque exista una configuración local.

## Formas de comunicación

### Proxy de desarrollo

```dotenv
VITE_API_BASE=
VITE_BACKEND_PROXY_TARGET=http://127.0.0.1:8000
```

El navegador solicita `http://localhost:5173/api/v1/...` y Vite reenvía al backend.
La comunicación del navegador es con su mismo origen. En Compose, el destino
interno es `http://backend:8000`; ese nombre no se utiliza como URL pública.

### Acceso directo a la API

```dotenv
VITE_API_BASE=http://localhost:8000
```

El navegador accede a otro origen. Django debe permitir el origen exacto del
frontend en `DJANGO_CORS_ALLOWED_ORIGINS`, por ejemplo
`http://localhost:5173,http://127.0.0.1:5173`. Protocolo, host y puerto forman
parte del origen; CORS no sustituye la autenticación Bearer.

La base no debe incluir `/api/v1`: el cliente ya agrega esa ruta. Los espacios y
barras finales se eliminan al leer la configuración. Las variables `VITE_*` son
públicas y no deben contener secretos.

### Build

`VITE_API_BASE` se incorpora al compilar; cambiar una variable del servidor después
no modifica un build existente. Una base vacía requiere que el servidor publicado
redirija `/api` al backend. `server.proxy` de Vite solo configura el desarrollo.

## Verificación

```powershell
npm run lint
npm test
npm run build
```

Con ambos servicios activos, comprobar `http://localhost:5173/health/` y revisar
en DevTools la solicitud de la feature elegida, su método, autenticación,
respuesta JSON y estado HTTP. Para verificar CORS, usar también una solicitud
directa al backend; el proxy por sí solo no comprueba esa política.

El [informe del integrante 1](../docs/semanas/semana-06/ape6-arquitectura-frontend-derick.md)
incluye el contrato revisado, los límites de la intervención y las preguntas 1 y 4.

## Feature de la APE 6: Consulta de recomendaciones

### Trazabilidad

| Eslabón | Elemento |
|---|---|
| Feature | F-006 · Consulta del estado de cumplimiento (`feature-map.md`) |
| Historia y criterio | HU-02 · CA-02.2: filtrado por estado, unidad y plazo |
| Requisitos | RF-019: el ejecutor solo ve su unidad · RNF-003 · RNF-004 |
| Operación OpenAPI | `listarRecomendaciones` · `GET /api/v1/recomendaciones` · seguridad `bearerAuth` |
| Modelos | `RecommendationQuery`, `PaginatedResult<Recommendation>` en `src/models/domain.types.ts` |
| Servicio | `recommendationsService.listPage(filters)` en `src/services/recommendations.service.ts` |
| Componente y ruta | [componente de consulta y su ruta] |
| Evidencias | `docs/evidencias/` (casos PI-01 a PI-09) |

La correspondencia parámetro por parámetro con el contrato, los estados de la interfaz
y los casos de prueba de integración están en
[`DOCUMENTACION/04_IMPLEMENTACION/FRONTEND_CONSUMO_API.md`](../DOCUMENTACION/04_IMPLEMENTACION/FRONTEND_CONSUMO_API.md).

### Estados de la interfaz

| Estado | Respuesta de la API | Qué ve la persona usuaria |
|---|---|---|
| Carga | Solicitud en curso | "Consultando recomendaciones…" |
| Éxito | 200 con resultados | Tabla con paginación |
| Vacío | 200 con `data: []` | "No hay recomendaciones que coincidan con los filtros" |
| Validación | Datos incoherentes antes de enviar, o 400 `VALIDATION_ERROR` | Mensaje para corregir el filtro |
| Sesión vencida | 401 | Vuelta al inicio de sesión |
| No autorizado | 403 | "Su rol no tiene permiso para consultar recomendaciones" |
| Servidor no disponible | 5xx o sin conexión | Mensaje sin detalle técnico y **Reintentar** |

### Contribuciones

| Integrante | Parte | Evidencia |
|---|---|---|
| [Integrante 1] | Configuración, URL base, cliente HTTP y CORS | PR #24 |
| [Integrante 2] | Modelos y servicio según OpenAPI | PR #23 |
| [Integrante 3] | Componente, validaciones y ruta | [PR] |
| [Integrante 4] | Gestión de estados, pruebas, evidencias y documentación | PR #25 |
