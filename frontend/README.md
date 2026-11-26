# SITRA-CGE · Frontend web

Interfaz web de SITRA-CGE UNL, hecha en React 19, TypeScript y Vite 6. Consume la API REST del backend (`/api/v1`) según el contrato `backend/contracts/openapi.yaml`.

## Ejecución

1. Levantar el backend en modo desarrollo. Las credenciales de prueba solo funcionan con `DJANGO_DEBUG=true`:

   ```powershell
   $env:DJANGO_DEBUG="true"; .venv\Scripts\python.exe backend\manage.py runserver
   ```

2. Instalar dependencias e iniciar el frontend:

   ```powershell
   npm --prefix frontend install
   ```

   ```powershell
   npm --prefix frontend run dev
   ```

3. Abrir http://127.0.0.1:5173 y entrar con un rol de prueba (UAI, Ejecutor, Rectorado o DTI).

### Comunicación con la API y CORS

En desarrollo, Vite reenvía `/api` y `/health` al backend (`vite.config.ts`; destino en `VITE_BACKEND_PROXY_TARGET`, por defecto `http://127.0.0.1:8000`). Para el navegador, frontend y API tienen el mismo origen, así que no interviene CORS.

Si el frontend se publica en otro origen, se define `VITE_API_BASE` con la URL de la API y ese origen se agrega a `DJANGO_CORS_ALLOWED_ORIGINS` en el backend.

## Estructura

```
src/
├── api/client.ts          Cliente HTTP: token Bearer, envoltura universal y ApiError
├── components/            Componentes de interfaz compartidos
├── features/<feature>/
│   ├── services/          Acceso a datos: una función por operación del contrato
│   └── pages/             Componentes de pantalla y sus pruebas
└── routes.tsx             Rutas y roles que pueden verlas
```

## Feature de la APE-006: Consulta de recomendaciones

### Trazabilidad

| Eslabón | Elemento |
|---|---|
| Feature | F-006 · Consulta del estado de cumplimiento (`feature-map.md`) |
| Historia y criterio | HU-02 · CA-02.2: filtrado por estado, unidad y plazo |
| Requisitos | RF-019: el ejecutor solo ve su unidad · RNF-003: autorización por rol y por objeto · RNF-004: contrato de respuesta |
| Operación OpenAPI | `listarRecomendaciones` · `GET /api/v1/recomendaciones` · seguridad `bearerAuth` |
| Servicio | `src/features/recomendaciones/services/recomendacionesService.ts` → `listarRecomendaciones(filtros, signal)` |
| Componente | `src/features/recomendaciones/pages/ConsultaRecomendacionesPage.tsx` |
| Ruta | `/recomendaciones/consulta` · roles UAI, Ejecutor, Rectorado y Auditor CGE |
| Pruebas | `recomendacionesService.test.ts` (4) · `ConsultaRecomendacionesPage.test.tsx` (9) |

La correspondencia parámetro por parámetro entre el contrato y el servicio está en [`DOCUMENTACION/04_IMPLEMENTACION/FRONTEND_CONSUMO_API.md`](../DOCUMENTACION/04_IMPLEMENTACION/FRONTEND_CONSUMO_API.md).

### Estados de la interfaz

| Estado | Respuesta de la API | Qué ve la persona usuaria |
|---|---|---|
| Carga | Solicitud en curso | "Consultando recomendaciones…" |
| Éxito | 200 con resultados | Tabla con paginación |
| Vacío | 200 con `data: []` | "No hay recomendaciones que coincidan con los filtros" |
| Validación en la interfaz | No se llama a la API | "Vence desde" posterior a "Vence hasta": mensaje junto a los filtros |
| Validación del backend | 400 `VALIDATION_ERROR` | "Revise los filtros" y los errores de `errors.fields` |
| Sesión vencida | 401 `AUTHENTICATION_REQUIRED` | Vuelta al inicio de sesión |
| No autorizado | 403 `PERMISSION_DENIED` | "Acceso no autorizado" |
| Servidor no disponible | 5xx o sin conexión | Mensaje sin detalle técnico y botón **Reintentar** |

### Pruebas

```powershell
npm --prefix frontend test
```

Las pruebas del componente cubren cada estado de la tabla anterior; las del servicio comprueban la URL, la cabecera `Authorization`, la paginación y el manejo de 400 y 401.

### Evidencias de integración

Las capturas están en [`docs/evidencias/`](docs/evidencias/) y siguen los casos PI-01 a PI-09:

| ID | Caso | Resultado esperado |
|---|---|---|
| PI-01 | Operación en Swagger (`/api/docs/`) | 200 con `data` y `meta.pagination` |
| PI-02 | Consulta desde la interfaz (UAI) | Tabla y solicitud `GET …/recomendaciones?page=1&page_size=25` en DevTools |
| PI-03 | Carga con la red limitada | "Consultando recomendaciones…" |
| PI-04 | Filtro por estado | URL con `state=REABIERTA` y sin filtros vacíos |
| PI-05 | Sin resultados | Mensaje de lista vacía |
| PI-06 | Validación | Fechas invertidas en la interfaz; `page_size=500` en Swagger responde 400 |
| PI-07 | Sesión vencida | 401 y vuelta al inicio de sesión |
| PI-08 | Backend detenido | "El servidor no está disponible" y **Reintentar** |
| PI-09 | Ejecutor | Solo recomendaciones de su unidad (DEP-A) |

## Contribuciones (APE-006)

| Integrante | Parte | Evidencia |
|---|---|---|
| [Integrante 1] | Configuración del proyecto, URL base, cliente HTTP y CORS | [commit/PR] |
| [Integrante 2] | Tipos según OpenAPI y servicio de acceso a datos | [commit/PR] |
| [Integrante 3] | Componente, validaciones y ruta | [commit/PR] |
| [Integrante 4] | Gestión de estados, pruebas, evidencias y documentación | [commit/PR] |
