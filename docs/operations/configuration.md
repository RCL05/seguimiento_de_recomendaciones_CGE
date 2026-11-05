# Configuración segura y operación

Guía de variables de entorno, integración SSO, SMTP, almacenamiento de
evidencias y controles de seguridad para SITRA-CGE UNL.

## 1. Principios

- Los secretos se inyectan por variables de entorno o gestor de secretos; nunca
  se versionan ni se guardan en la base de datos.
- La API de configuración de notificaciones rechaza claves que contengan
  `smtp`, `password`, `token`, `secret` o `credential`.
- Producción exige `DJANGO_DEBUG=false`, `DJANGO_SECRET_KEY` robusta y
  `DJANGO_ALLOWED_HOSTS` explícito.
- Los logs no incluyen credenciales, tokens, contenido de PDF ni datos
  personales completos; usan `request_id`, IDs y hashes.

## 2. Variables de entorno

| Variable | Obligatoria | Ejemplo | Uso |
| --- | --- | --- | --- |
| `DJANGO_SECRET_KEY` | Sí en producción | `cambiar-en-gestor-de-secretos` | Firma criptográfica de Django. |
| `DJANGO_DEBUG` | Sí | `false` | Desactiva trazas y páginas de error detalladas. |
| `DJANGO_ALLOWED_HOSTS` | Sí en producción | `sitra.unl.edu.ec` | Hosts permitidos, separados por coma. |
| `DJANGO_MEDIA_ROOT` | No | `/var/lib/sitra/media` | Ruta local de evidencias. |
| `POSTGRES_DB` | Sí en producción | `sitra_cge` | Activa el backend PostgreSQL. |
| `POSTGRES_USER` | No | `sitra_app` | Usuario de base de datos. |
| `POSTGRES_PASSWORD` | Sí en producción | `***` | Contraseña de base de datos. |
| `POSTGRES_HOST` | No | `db` | Host de PostgreSQL. |
| `POSTGRES_PORT` | No | `5432` | Puerto de PostgreSQL. |
| `SSO_ISSUER` | Sí en producción | `https://sso.unl.edu.ec` | Emisor OIDC/LDAP institucional. |
| `SSO_CLIENT_ID` | Sí en producción | `sitra-cge` | Identificador del cliente SSO. |
| `SSO_CLIENT_SECRET` | Sí en producción | `***` | Secreto del cliente SSO. |
| `SSO_REDIRECT_URI` | Sí en producción | `https://sitra.unl.edu.ec/auth/callback` | Retorno autorizado. |
| `EMAIL_HOST` | Sí para correo | `smtp.unl.edu.ec` | Servidor SMTP institucional. |
| `EMAIL_PORT` | No | `587` | Puerto SMTP. |
| `EMAIL_HOST_USER` | Sí para correo | `notificaciones@unl.edu.ec` | Cuenta emisora. |
| `EMAIL_HOST_PASSWORD` | Sí para correo | `***` | Secreto SMTP. |
| `EMAIL_USE_TLS` | No | `true` | STARTTLS obligatorio en producción. |
| `DEFAULT_FROM_EMAIL` | No | `SITRA-CGE <no-reply@unl.edu.ec>` | Remitente visible. |
| `EVIDENCE_STORAGE_BACKEND` | No | `s3` | `local` o `s3`. |
| `EVIDENCE_S3_BUCKET` | Sí con S3 | `sitra-evidencias` | Bucket privado de PDFs. |
| `EVIDENCE_S3_ENDPOINT` | No | `https://s3.unl.edu.ec` | Endpoint compatible S3. |
| `EVIDENCE_S3_ACCESS_KEY` | Sí con S3 | `***` | Credencial de escritura. |
| `EVIDENCE_S3_SECRET_KEY` | Sí con S3 | `***` | Secreto de escritura. |
| `VITE_API_BASE` | No | `https://sitra.unl.edu.ec` | Base de API para el frontend. |

Archivo local de referencia: `backend/.env.example`. Copiarlo a `.env` y completar solo
en el entorno de desarrollo; `.env` está ignorado por Git.

## 3. SSO institucional

Flujo esperado:

1. El frontend redirige al proveedor SSO de la UNL.
2. El proveedor retorna un `credential`/token firmado al backend.
3. `SsoAdapter.authenticate(token=...)` valida emisor, audiencia, expiración y
   firma; devuelve `correo`, `nombres`, `rol` y `unidad_codigo`.
4. El backend crea o actualiza `Usuario` y `UnidadOrganica`, y responde la
   identidad junto con el rol efectivo.
5. Cada petición posterior usa `X-User-ID`, `X-Role` y `X-Unit-ID` emitidos por
   la sesión autenticada.

Roles válidos: `DTI`, `UAI`, `EJECUTOR`, `RECTORADO`, `CGE_AUDITOR`. Un rol no
reconocido responde `400 VALIDATION_ERROR`.

Estado actual: `SsoAdapter` es un simulador para pruebas con los tokens
`valid-sso-token` y `dti-sso-token`; `login_sso` ya consume el diccionario
(`correo`, `nombres`, `rol`, `unidad_codigo`). Antes de producción debe
reemplazarse por la validación OIDC real.

## 4. SMTP y notificaciones

- El canal interno siempre está disponible; el canal correo requiere
  `EMAIL_*` configurado y `canal_email_activo=true`.
- Los envíos usan TLS, timeout de 10 segundos y máximo de 3 reintentos con
  espera exponencial.
- Las alertas se programan de forma idempotente por
  `(destinatario, tipo, recomendación, ventana)`.
- La configuración institucional (`GET/PUT /api/v1/notificaciones/configuracion`)
  solo la administra `DTI` y todo cambio queda en `AuditLog`.
- Las preferencias personales (`GET/PUT /api/v1/notificaciones/preferencias`)
  solo las edita el propio usuario o `DTI`.
- En producción los jobs se ejecutan por cron o tarea programada; el endpoint
  `POST /api/v1/jobs/evaluar-plazos` queda restringido a `DTI`.

Ejemplo de cron (cada hora):

```cron
0 * * * * cd /opt/sitra/backend && /opt/sitra/.venv/bin/python manage.py evaluar_plazos
```

## 5. Almacenamiento de evidencias

- Límite: 30 MB por PDF; se valida extensión, MIME, firma `%PDF`, SHA-256 y
  análisis antimalware.
- El nombre original se registra como metadato; el objeto se guarda con un
  identificador opaco.
- El bucket debe ser privado, con cifrado en reposo y versionado.
- La descarga exige autorización por rol y unidad; un acceso indebido responde
  `404` y registra `ACCESS_DENIED` en auditoría.
- Para `local`, `DJANGO_MEDIA_ROOT` debe estar fuera del árbol servido
  públicamente y con permisos `750`.
- Para `s3`, usar credenciales de mínimo privilegio y URLs firmadas de corta
  duración.

## 6. Despliegue y verificación

```bash
# Backend
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
.venv/Scripts/python manage.py migrate
.venv/Scripts/python manage.py check --deploy

# Frontend
cd frontend
npm ci
npm run build
```

Checklist de producción:

- [ ] `DJANGO_DEBUG=false` y `DJANGO_ALLOWED_HOSTS` restringido.
- [ ] HTTPS obligatorio y HSTS habilitado en el proxy.
- [ ] `DJANGO_SECRET_KEY` y credenciales en gestor de secretos.
- [ ] PostgreSQL con backups cifrados y restauración probada.
- [ ] Bucket privado con cifrado y versionado.
- [ ] SMTP con TLS y cuenta dedicada.
- [ ] Jobs programados y monitoreados.
- [ ] Logs centralizados con `request_id` y alertas de `ACCESS_DENIED`.
- [ ] Rotación de credenciales SSO/SMTP/S3 documentada.
