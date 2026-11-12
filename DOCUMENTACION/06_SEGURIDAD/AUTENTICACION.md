## Mecanismo

SITRA-CGE no gestiona contraseñas. La identidad la aporta el **SSO institucional** y la API emite su propio **JWT de acceso** (ADR-0002).

| Paso | Componente | Detalle verificado |
|---|---|---|
| 1. Intercambio | `POST /api/v1/sesiones` (`LoginSsoView`, `AllowAny`) | Cuerpo `{"credential": "…"}` |
| 2. Validación de la credencial | `SsoAdapter.authenticate` | Con `DEBUG=true`, acepta tokens de desarrollo fijos; en otro caso, introspección OAuth2 contra `SSO_INTROSPECTION_URL` (timeout 5 s). Exige `active=true`, correo y rol válido |
| 3. Aprovisionamiento | `SsoAdapter._persist_identity` | Crea o actualiza `Usuario` y `UnidadOrganica` en una transacción |
| 4. Emisión | `SsoAdapter.issue_session` | JWT **HS256**; claims `iss=sitra-cge`, `aud=sitra-cge-api`, `sub`, `user_id`, `email`, `role`, `unit_id`, `iat`, `exp` (+3600 s), `jti` |
| 5. Uso | `JWTBearerAuthentication` | `Authorization: Bearer <jwt>`; `jwt.decode` con algoritmo fijo y claims obligatorios |
| 6. Revalidación | `JWTBearerAuthentication` | La cuenta debe existir, estar activa y conservar **el mismo rol y la misma unidad** que el token; si no, 401 |
| 7. Auditoría | `IniciarSesionSso` | El inicio de sesión se registra en `AuditLog` |

## Clave de firma

- `JWT_SIGNING_KEY` o, en su defecto, `DJANGO_SECRET_KEY`; se exige longitud ≥ 32 caracteres (`RuntimeError` si no).
- Con `DEBUG=true` y sin `DJANGO_SECRET_KEY`, se genera una clave aleatoria por proceso: los tokens dejan de valer al reiniciar y no se comparten entre procesos. Para Compose se define `JWT_SIGNING_KEY` explícitamente.
- Con `DEBUG=false` sin `DJANGO_SECRET_KEY`, el arranque falla (`settings.py`).

## Sesión en el cliente

La SPA guarda la sesión en `sessionStorage` (`frontend/src/api/client.ts`): se borra al cerrar la pestaña y no se envía automáticamente como cookie (sin riesgo CSRF), pero es legible por JavaScript, de modo que una vulnerabilidad XSS permitiría robar el token durante su hora de vigencia. No existe *refresh token* ni revocación explícita (`jti` se emite pero no se consulta en una lista de revocación); el cambio de rol, unidad o la desactivación de la cuenta invalidan el token de forma efectiva gracias al paso 6.

## Pruebas que lo verifican

| Prueba | Qué demuestra |
|---|---|
| `tests/unit/usuarios/test_sso_jwt.py::test_emits_jwt_with_expiration_and_authorization_claims` | Claims y expiración |
| `tests/unit/usuarios/test_sso_jwt.py::test_rejects_expired_or_tampered_jwt` | Rechazo de token expirado o alterado |
| `tests/api/test_http_api.py::test_peticion_sin_token_responde_401_authentication_required` | 401 sin token |
| `tests/api/test_endpoints_base.py::test_401_incluye_www_authenticate` | Cabecera `WWW-Authenticate` |
| `tests/integration/usuarios/test_identity_configuration_flow.py` | Flujo completo de identidad |
| `tests/integration/usuarios/test_admin_flow.py` (`test_sso_adapter_interpreta_claims_de_introspeccion`, `test_tokens_sso_de_desarrollo_crean_identidades_completas`) | Claims de introspección y tokens de desarrollo |
| `tests/integration/usuarios/test_admin_flow.py::test_tokens_de_desarrollo_no_se_aceptan_fuera_de_debug` | Tokens fijos inactivos fuera de `DEBUG` |
| `tests/security/test_hallazgos_semana4.py` (`test_login_fallido_se_audita_y_responde_con_www_authenticate`, `test_login_limita_intentos_por_ip`) | Login fallido auditado sin eco del secreto; límite de intentos `LOGIN_THROTTLE_RATE` (10/min) |

## Brechas y recomendaciones

| Brecha | Riesgo | Recomendación |
|---|---|---|
| `DEBUG=true` activa tokens de desarrollo conocidos (H-10) | Si se habilita en producción, cualquiera con esos tokens obtiene identidad | `DEBUG` ya es `false` por defecto; mantenerlo así y añadir `check --deploy` en CI |
| Proveedor SSO productivo no definido | Comportamiento real por validar | Acordar con DTI (OIDC recomendado) y ampliar `SsoAdapter` |
| Sin revocación por `jti` | Token robado válido hasta 1 h | Lista de revocación o TTL menor |

## Django Admin

`/admin/` usa la autenticación propia de Django (`django.contrib.auth`, usuarios con contraseña) y es **independiente** del JWT. No hay superusuarios en los datos iniciales; crearlos es responsabilidad de operación (`manage.py createsuperuser`).
