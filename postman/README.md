# Colección de Postman

| Archivo | Contenido |
|---|---|
| `SITRA-CGE.postman_collection.json` | 42 solicitudes en 5 carpetas, con pruebas automáticas |
| `SITRA-CGE-local.postman_environment.json` | Entorno `SITRA-CGE local`: URL base y credenciales de desarrollo |

## Uso

1. Levante el backend en modo desarrollo. Las credenciales de prueba (`uai-sso-token`,
   `ejecutor-sso-token`, `dti-sso-token`, `rectorado-sso-token`) solo funcionan con
   `DJANGO_DEBUG=true`:

   ```bash
   python backend/manage.py runserver
   ```

2. En Postman, importe los dos archivos (**Import**) y seleccione el entorno `SITRA-CGE local`.
3. Ejecute la colección completa con **Run collection**, o las carpetas en orden.

Los tokens, los identificadores creados y las fechas se guardan solos en variables de la
colección. Cada ejecución usa un número de informe distinto, así que puede repetirse.

## Carpetas

| Carpeta | Qué prueba |
|---|---|
| 00 Salud y sesión | Salud del servicio, inicio de sesión de cuatro roles y credencial inválida (401 con `WWW-Authenticate`) |
| 01 Administración DTI | Unidades, usuarios y configuración de notificaciones |
| 02 Flujo de cumplimiento | Informe → recomendación → hito → evidencia → dictamen → reapertura → reasignación → auditoría |
| 03 Reportes y notificaciones | Tablero, KPIs por rol, matriz CGE en CSV y bandeja |
| 04 Errores HTTP | 400, 401, 403, 404, 405 y 409 |

## Límite de inicio de sesión

El login admite 10 intentos por minuto por IP y la colección hace 6. Si la ejecuta dos
veces seguidas, espere un minuto o suba el límite en desarrollo:

```bash
LOGIN_THROTTLE_RATE=100/min python backend/manage.py runserver
```

## Ejecución por línea de comandos

```bash
npx newman run postman/SITRA-CGE.postman_collection.json -e postman/SITRA-CGE-local.postman_environment.json
```
