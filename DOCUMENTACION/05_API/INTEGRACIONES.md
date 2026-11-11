## Integraciones externas

| Integración | Mecanismo real | Configuración | Estado | Comportamiento ante fallo |
|---|---|---|---|---|
| SSO institucional | Introspección OAuth2 (RFC 7662): `POST` a `SSO_INTROSPECTION_URL` con `Basic client_id:client_secret` y `token=…`; espera `active`, `email`/`correo`, `role`/`rol`, `name`/`nombres` y unidad | `SSO_INTROSPECTION_URL`, `SSO_CLIENT_ID`, `SSO_CLIENT_SECRET` | Implementado; el proveedor de la UNL aún no está definido | Timeout 5 s; cualquier error → identidad vacía → `401` |
| Tokens SSO de desarrollo | Diccionario fijo en `SsoAdapter._development_identity` | Activo solo con `DJANGO_DEBUG=true` | Implementado (solo desarrollo) | — |
| Correo SMTP | `django.core.mail.send_mail` con `EMAIL_BACKEND` SMTP (o consola en desarrollo sin `EMAIL_HOST`) | `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL`, `EMAIL_TIMEOUT`, `DEFAULT_FROM_EMAIL`, `EMAIL_BACKEND` | Implementado | La notificación pasa a `FALLIDA`, `intentos+1`; no se revierte la operación de negocio; se reintenta en cada ejecución hasta 3 intentos |
| Almacenamiento de archivos | Sistema de archivos local bajo `MEDIA_ROOT` | `DJANGO_MEDIA_ROOT` | Implementado | Si la escritura falla, se borra el archivo parcial y no se crea la evidencia |
| Almacenamiento S3 | — | `EVIDENCE_STORAGE_BACKEND`, `EVIDENCE_S3_*` | **No implementado** (variables sin efecto, H-04) | — |
| CGE | Exportación manual de la matriz CSV | — | Sin integración técnica (fuera de alcance) | — |

## Integraciones internas

| Productor → consumidor | Mecanismo |
|---|---|
| SPA → API | HTTP/JSON; en desarrollo, proxy de Vite (`/api`, `/health` → `VITE_BACKEND_PROXY_TARGET` o `http://127.0.0.1:8000`); en otros entornos `VITE_API_BASE` |
| Programador → núcleo | `python manage.py evaluar_plazos` (imprime JSON) o `POST /api/v1/evaluaciones-plazos` |
| Casos de uso → auditoría | Llamada directa a `record_audit` dentro de la transacción |
| Documentación | `docs_server/app.py` lee `docs/**/*.md` del sistema de archivos |

## Puertos definidos

| Puerto | Archivo | Implementaciones |
|---|---|---|
| SSO | `usuarios/ports/sso_port.py` | `SsoAdapter` |
| Notificación | `notificaciones/ports/notification_port.py` | `SmtpAdapter` (usado en pruebas); la entrega real usa `django.core.mail` |
| Almacenamiento | `core/files/storage_ports.py` | `EvidenceStorage` (local, en flujo; usado por la API) y `LocalEvidenceStorage` (`evidencias/infrastructure/storage_adapter.py`, en memoria completa) |
