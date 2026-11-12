# Colección de Postman

| Archivo | Contenido |
|---|---|
| `SITRA-CGE.postman_collection.json` | 51 solicitudes en 5 carpetas: cubre las 31 operaciones del contrato OpenAPI, con pruebas automáticas y un ejemplo de respuesta real en cada solicitud |
| `SITRA-CGE-desarrollo.postman_environment.json` | `http://127.0.0.1:8000` y las credenciales de prueba de desarrollo |
| `SITRA-CGE-preproduccion.postman_environment.json` | URL y credenciales SSO por completar |
| `SITRA-CGE-produccion.postman_environment.json` | URL y credenciales SSO por completar, con `solo_lectura=true` |
| `archivos/informe-ejemplo.pdf` | PDF que se adjunta al registrar un informe con `multipart/form-data` |
| `generar_coleccion.py` | Genera la colección y los tres entornos |

## Uso

1. Levante el backend. En desarrollo, las credenciales de prueba (`uai-sso-token`, `ejecutor-sso-token`,
   `dti-sso-token`, `rectorado-sso-token`) solo funcionan con `DJANGO_DEBUG=true`:

   ```bash
   DJANGO_DEBUG=true python backend/manage.py runserver
   ```

2. En Postman, importe la colección y el entorno que vaya a usar (**Import**), y selecciónelo arriba a la derecha.
3. Configure la carpeta `postman/` como *Working directory* (**Settings → General**). Así Postman encuentra
   `archivos/informe-ejemplo.pdf`. Si no, en la solicitud del informe con PDF vuelva a elegir el archivo.
4. Ejecute `00 Salud y sesión` y luego el resto de carpetas en orden, o la colección completa con **Run collection**.

## Variables

| Dónde | Variables | Uso |
|---|---|---|
| Entorno | `baseUrl`, `entorno`, `solo_lectura` | Servidor y modo de ejecución |
| Entorno (secretas) | `cred_uai`, `cred_ejecutor`, `cred_dti`, `cred_rectorado` | Credencial con la que se crea cada sesión |
| Entorno (secretas, dinámicas) | `token_uai`, `token_ejecutor`, `token_dti`, `token_rectorado` | JWT guardados por `00 Salud y sesión`. Cada entorno conserva los suyos |
| Colección (dinámicas) | `informe_id`, `recomendacion_id`, `dictamen_id`, `evidencia_*`, `sufijo`, fechas… | Identificadores creados durante la ejecución |

Cada solicitud usa la autenticación **Bearer Token** de Postman con el token del rol correspondiente.
Las solicitudes públicas (`/health/` y `POST /sesiones`) usan **No Auth**.

## Entornos

| Entorno | Qué completar | Escritura |
|---|---|---|
| Desarrollo | Nada | Sí |
| Preproducción | `baseUrl` y las credenciales SSO de cuentas de prueba | Sí |
| Producción | `baseUrl` y las credenciales SSO | **No**: con `solo_lectura=true`, el script de la colección omite toda solicitud que no sea `GET`, salvo `POST /sesiones` |

Los valores secretos se escriben en **Current value**, no en **Initial value**, para que no se compartan al
exportar o sincronizar el workspace.

## Carpetas

| Carpeta | Qué prueba |
|---|---|
| 00 Salud y sesión | Salud del servicio, sesión de cuatro roles y credencial inválida (401 con `WWW-Authenticate`) |
| 01 Administración DTI | Unidades, usuarios (consulta y asignación de rol y unidad) y configuración de notificaciones |
| 02 Flujo de cumplimiento | Informe (JSON y con PDF adjunto) → recomendación → hito → evidencia → dictamen (y su consulta por `Location`) → reapertura → reasignación → auditoría |
| 03 Reportes y notificaciones | Tablero, KPIs por rol, matriz CGE en CSV, preferencias de notificación y bandeja |
| 04 Errores HTTP | 400 (incluida una referencia inexistente), 401, 403, 404, 405 y 409 (incluida evidencia sin plan) |

Cada ejecución usa un número de informe distinto, así que la colección puede repetirse.

## Límite de inicio de sesión

El login admite 10 intentos por minuto por IP y la colección hace 6. Si la ejecuta dos veces seguidas,
espere un minuto o suba el límite en desarrollo:

```bash
LOGIN_THROTTLE_RATE=100/min DJANGO_DEBUG=true python backend/manage.py runserver
```

## Ejecución por línea de comandos

```bash
npx newman run postman/SITRA-CGE.postman_collection.json -e postman/SITRA-CGE-desarrollo.postman_environment.json --working-dir postman
```

## Regenerar la colección

Los ejemplos de respuesta salen de una ejecución real de newman. Los JWT se reemplazan por `<jwt>`:

```bash
npx newman run postman/SITRA-CGE.postman_collection.json -e postman/SITRA-CGE-desarrollo.postman_environment.json --working-dir postman --reporters json --reporter-json-export reporte.json
python postman/generar_coleccion.py postman --ejemplos reporte.json
```
