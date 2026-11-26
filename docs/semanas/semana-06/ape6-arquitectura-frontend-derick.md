# APE 6 - Arquitectura, configuración y CORS del frontend

**Integrante 1:** Derick Paul Vargas Vasquez

**Fecha:** 26 de noviembre de 2026

**Rama:** `feature/ape6-arquitectura-frontend-derick`

**Base revisada:** `origin/develop`, commit `8213c56`.

## Alcance individual

Se reutiliza el frontend React + TypeScript + Vite del repositorio. Las referencias
a Angular y `environment.ts` de la distribución se adaptan a variables `VITE_*`,
al proxy de Vite y al cliente `fetch` existente.

La intervención cubre configuración por entorno, URL base, revisión del transporte
HTTP, CORS y respuestas de control 1 y 4. Conserva los modelos, los métodos de
dominio del servicio, las pantallas y sus estados visuales. La implementación de
esos elementos corresponde a los integrantes 2, 3 y 4 según la distribución.

## Estructura y contrato revisados

| Elemento                    | Archivo o ubicación                                            |
| --------------------------- | -------------------------------------------------------------- |
| Entrada React               | `frontend/src/main.tsx`                                        |
| Aplicación y sesión         | `frontend/src/App.tsx`                                         |
| Rutas por rol               | `frontend/src/routes.tsx`                                      |
| Pantallas por funcionalidad | `frontend/src/features/`                                       |
| Cliente HTTP compartido     | `frontend/src/api/client.ts`                                   |
| Proxy y Vitest              | `frontend/vite.config.ts`                                      |
| Contrato oficial            | `backend/contracts/openapi.yaml`                               |
| Copia de Spec Kit           | `specs/001-seguimiento-recomendaciones/contracts/openapi.yaml` |
| CORS                        | `backend/config/settings.py`                                   |

Ambos contratos publicados son idénticos y utilizan OpenAPI **3.0.3**. Algunas
referencias históricas del plan todavía mencionan 3.1; no se modifica el contrato
ni se cambia el alcance del backend en esta intervención.

Como caso de comprobación de la infraestructura se utiliza la consulta de KPIs
ya existente. Esto no fija ni reemplaza la selección de feature del equipo.

| Trazabilidad del caso revisado | Valor                                                              |
| ------------------------------ | ------------------------------------------------------------------ |
| Capacidad                      | Consultar indicadores del seguimiento de recomendaciones           |
| Operación OpenAPI              | `consultarKpisDashboard`                                           |
| Endpoint                       | `GET /api/v1/dashboard/kpis`                                       |
| Autenticación                  | `Authorization: Bearer <JWT>`                                      |
| Cuerpo de solicitud            | No requiere                                                        |
| Respuesta exitosa              | `200`, envoltura `KpisDashboardEnvelope` con `data` de tipo `Kpis` |
| Errores declarados             | `401` y `500`                                                      |
| Método existente               | `api.getDashboardKPIs()`                                           |
| Pantalla existente             | `frontend/src/features/dashboard/pages/DashboardKPIs.tsx`          |

El esquema de datos declara `total_recomendaciones`, `recomendaciones_por_estado`,
`tasa_cumplimiento_porcentaje`, `recomendaciones_vencidas_o_en_mora` y
`total_informes_cge`. La pantalla ya consulta ese método; no se modifica.

## Configuración implementada

- Plantilla `frontend/.env.example` y tipos explícitos para las variables.
- Carga de variables por modo con `loadEnv`, respetando las del proceso y Compose.
- Proxy de `/api` y `/health` hacia el backend; fallback local `http://127.0.0.1:8000`.
- Puerto de desarrollo `5173` estricto para conservar un origen conocido.
- Normalización de espacios y barras finales de `VITE_API_BASE`.
- Pruebas del cliente para URL relativa y absoluta, Bearer, JSON, FormData y `401`.

Con `VITE_API_BASE` vacío, Vite reenvía las rutas relativas. Con una URL absoluta,
el navegador solicita directamente al backend y se aplica CORS. La base no lleva
`/api/v1`; ese prefijo ya está incluido en los métodos del cliente.

Consultar [frontend/README.md](../../../frontend/README.md) para ejemplos y
comandos de ejecución. No se incorporan secretos ni archivos locales de entorno.

## CORS y autenticación

La configuración existente ya registra `corsheaders` y coloca `CorsMiddleware`
antes de los demás middlewares. Admite orígenes explícitos mediante
`DJANGO_CORS_ALLOWED_ORIGINS`; en desarrollo incluye `localhost:5173` y
`127.0.0.1:5173`.

Se permiten `authorization`, `content-type`, `x-filename`, `x-evidence-type` y
`x-request-id`, además de `accept`. Se exponen `Location` y `Content-Disposition`.
Las solicitudes protegidas siguen requiriendo un JWT válido. No se necesitó
ampliar los orígenes ni modificar la política del backend.

Las pruebas existentes en `backend/tests/api/test_http_semantics.py` comprueban
el preflight autorizado, la exposición de `Location` y la ausencia de permiso
CORS para un origen no autorizado. Las pruebas de contrato comparan el esquema
generado con ambos YAML y verifican rutas y requisitos de autenticación.

## Preguntas de control

### 1. ¿Qué información del contrato OpenAPI necesita el frontend para consumir un endpoint?

Necesita la ruta exacta y su versión, el método HTTP, los parámetros de ruta y
consulta, las cabeceras, el mecanismo de autenticación y el esquema del cuerpo
cuando exista. Debe conocer también los tipos, campos obligatorios, restricciones,
formatos de respuesta, códigos de éxito y errores declarados.

En el caso revisado, `GET /api/v1/dashboard/kpis` no envía cuerpo, requiere un JWT
Bearer y devuelve los indicadores dentro de `data` con estado `200`. La envoltura
es `success`, `message`, `data`, `errors` y `meta`; el contrato también declara
`401` y `500`. La URL base se configura por entorno.

### 4. ¿Qué ocurre si frontend y backend se ejecutan en orígenes diferentes?

Un origen combina protocolo, host y puerto. Por eso `http://localhost:5173` y
`http://localhost:8000` son diferentes. El navegador aplica la política de mismo
origen y exige permiso CORS para que el frontend pueda leer la respuesta de la
API. Algunas solicitudes, como las que incluyen `Authorization`, requieren un
preflight `OPTIONS`; si no se autoriza, no se envía la solicitud posterior.

Para solicitudes directas, Django permite los orígenes del frontend mediante
`DJANGO_CORS_ALLOWED_ORIGINS` y las cabeceras necesarias. Durante el desarrollo,
el proxy de Vite permite usar rutas del mismo origen del frontend y reenviarlas
al backend. El proxy no demuestra por sí mismo que CORS funcione; se comprueba
también el acceso directo. CORS no reemplaza la autenticación ni los permisos.

## Resultados de verificación

Comprobaciones ejecutadas el 26 de noviembre de 2026:

| Comprobación                                               | Resultado                                                             |
| ---------------------------------------------------------- | --------------------------------------------------------------------- |
| ESLint del frontend                                        | Sin errores                                                           |
| Vitest                                                     | 17 pruebas aprobadas en 5 archivos; incluye 5 nuevas del cliente HTTP |
| TypeScript (`tsc -b`) y Vite (`vite build`)                | Compilación correcta                                                  |
| Django (`manage.py check --settings=config.test_settings`) | Sin problemas                                                         |
| Semántica HTTP, CORS y contrato publicado                  | 20 pruebas aprobadas                                                  |
| API HTTP y endpoints base                                  | 23 pruebas aprobadas                                                  |
| Health real por proxy y acceso directo desde Chrome        | `200` en ambos casos                                                  |
| Login y KPIs reales mediante el cliente React y el proxy   | Sesión válida y consulta `200`                                        |
| KPIs directos con Bearer y CORS desde Chrome               | `200`, datos iguales a los del proxy                                  |
| Consulta directa sin autenticación desde Chrome            | `401` legible por el cliente                                          |
| Preflight con origen permitido                             | `200` y cabeceras CORS esperadas                                      |
| Preflight con origen no autorizado                         | Sin `Access-Control-Allow-Origin`                                     |
| Pantalla React existente de KPIs                           | Carga completada con los datos del backend real                       |
| Proxy definido en archivo de entorno de un modo temporal   | Reenvío correcto a un puerto de backend distinto del predeterminado   |
| Variable de proceso usada por Compose                      | Tiene prioridad sobre el archivo de entorno                           |

La integración se ejecutó con Django y Vite locales, Chrome sin interfaz visible
y una base SQLite temporal creada y migrada exclusivamente para la comprobación.
Los servicios y el archivo temporal de entorno se retiraron al terminar; no se
modificó la base de desarrollo. El conjunto de datos estaba vacío salvo la
identidad creada por el login de prueba.

Se utilizó Python 3.12 y Node.js 24.22.3 disponibles en el entorno de trabajo;
Compose y CI mantienen Node.js 22. Se conservaron `package.json` y su lockfile.
No se ejecutó Docker Compose porque el motor Docker estaba apagado. La prueba de
prioridad verificó la configuración que inyecta Compose, sin levantar contenedores.

## Referencias

- [Configuración y loadEnv de Vite 6](https://v6.vite.dev/config/#using-environment-variables-in-config).
- [Variables de entorno de Vite 6](https://v6.vite.dev/guide/env-and-mode.html).
- [Documentación de django-cors-headers](https://github.com/adamchainz/django-cors-headers).
