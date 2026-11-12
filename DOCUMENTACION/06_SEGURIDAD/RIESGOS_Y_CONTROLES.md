## Método

Los riesgos se identificaron a partir de la especificación, del riesgo crítico declarado por el equipo y de la revisión del código. Se clasificaron con el **OWASP Top 10 (2021)** y el **OWASP API Security Top 10 (2023)**. Cada riesgo se relaciona con los controles **existentes** (verificados) y, por separado, con las **recomendaciones** (no implementadas).

Probabilidad e impacto: A (alto), M (medio), B (bajo). Riesgo residual estimado tras los controles existentes.

## Matriz de riesgos y controles

| ID | Riesgo | Categoría OWASP | P / I | Controles existentes (verificados) | Residual | Recomendación |
|---|---|---|---|---|---|---|
| R-01 | Declarar cumplida una recomendación sin sustento (riesgo crítico de negocio) | — (lógica de negocio) | M / A | Máquina de estados en dominio; `CUMPLIDA` solo por dictamen UAI con evidencia validada; 409 ante transición ilegal; 19 pruebas | B | Validar catálogo con la UAI y el Acuerdo 010-CG-2022 (H-09) |
| R-02 | Ejecutor accede a recomendaciones de otra unidad (BOLA/IDOR) | API1:2023 · A01:2021 | A / A | Autorización por objeto en casos de uso; 404 uniforme; auditoría `ACCESS_DENIED`; pruebas de seguridad | B | — |
| R-03 | Uso de funciones de otro rol (BFLA) | API5:2023 · A01:2021 | M / A | `require_roles` en vistas + verificación en casos de uso; KPIs del EJECUTOR acotados a su unidad | B | Restringir el desglose institucional de KPIs por rol si se decide (H-14 parcial) |
| R-04 | Suplantación con token robado o forjado | API2:2023 · A07:2021 | M / A | JWT HS256 con `iss`/`aud`/`exp`/`jti` obligatorios; revalidación de rol/unidad/estado en cada petición; TTL 1 h; login limitado (`LOGIN_THROTTLE_RATE`) y fallido auditado | M | Revocación por `jti`; CSP para mitigar XSS |
| R-05 | Despliegue con `DEBUG=true` (tokens de desarrollo activos, trazas) | A05:2021 · API8:2023 | M / A | `DEBUG=false` exige `DJANGO_SECRET_KEY`; tokens de desarrollo solo con `DEBUG` | M | `DEBUG` ya es `false` por defecto; añadir `check --deploy` y completar el perfil productivo (H-22, ADR-R03) |
| R-06 | Carga de archivo malicioso | A04:2021 · API8:2023 | M / M | Solo `.pdf`, firma `%PDF-`, ≤ 30 MB (cabecera y flujo real), nombre opaco UUID, almacenamiento fuera de estáticos, descarga autorizada | M | Escaneo antimalware (H-03); `Content-Disposition` con `X-Content-Type-Options` |
| R-07 | Alteración de evidencias tras su carga | A08:2021 | B / A | SHA-256 almacenado; verificación de integridad (UAI, CGE); anulación lógica sin borrado; FK `PROTECT` | B | Almacenamiento WORM o versionado |
| R-08 | Manipulación de la bitácora | A09:2021 | B / A | `AuditLog` append-only en el ORM; sin permisos por defecto en Admin | M | Revocar UPDATE/DELETE en PostgreSQL (ADR-R02) |
| R-09 | Exposición de secretos en logs o respuestas | A02:2021 · A09:2021 | M / A | `redact_sensitive`; la configuración rechaza claves con aspecto de secreto; errores sin trazas; `.env` ignorado por Git | B | Escaneo de secretos en CI |
| R-10 | Inyección SQL | A03:2021 | B / A | ORM de Django con consultas parametrizadas; sin SQL crudo en módulos | B | — |
| R-11 | Condiciones de carrera en transiciones | API6:2023 (flujos de negocio) | M / M | `transaction.atomic` + `select_for_update`; prueba de concurrencia | B en PostgreSQL · M en SQLite | Ejecutar la prueba de concurrencia contra PostgreSQL |
| R-12 | Consumo excesivo de recursos (cargas grandes, listados) | API4:2023 | M / M | Límite de 30 MB antes de leer; `page_size ≤ 100`; bandeja limitada a 100 | M | Throttling global de DRF; límites en el proxy |
| R-13 | CORS permisivo | A05:2021 | B / M | Orígenes explícitos; sin orígenes fuera de `DEBUG` si no se configuran | B | — |
| R-14 | Ausencia de cabeceras de transporte seguro (HSTS, cookies seguras) | A05:2021 | M / M | `SecurityMiddleware` y `XFrameOptionsMiddleware` activos | M | `SECURE_HSTS_SECONDS`, `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE` en producción |
| R-15 | Pérdida de alertas por fallo de correo | — (disponibilidad) | M / M | Alerta interna persiste; fallo no revierte el negocio; reintento acotado a 3 intentos | B | Monitorear el estado `FALLIDA` |
| R-16 | Dependencias vulnerables | A06:2021 | M / M | Versiones acotadas en manifiestos; `package-lock.json` | M | `pip-audit` / `npm audit` / Dependabot en CI |
| R-17 | Monitoreo insuficiente | A09:2021 | M / M | `request_id` en respuestas y auditoría; `/health/`; `LOGGING` a consola | M | Enviar logs a un agregador y alertar sobre `ACCESS_DENIED` |

## Controles por categoría

| Control | Implementado | Evidencia |
|---|---|---|
| Autenticación fuerte delegada (SSO) | Parcial | `sso_adapter.py` |
| Autorización por rol y objeto | Sí | `permissions.py`, casos de uso |
| Validación de entradas | Sí | Serializers DRF, validadores de modelo, `validate_pdf` |
| Manejo de errores sin fuga de información | Sí | `exception_handler.py`, `SafeExceptionReporterFilter` |
| Integridad de documentos | Sí | SHA-256 + verificación |
| Auditoría inmutable | Sí (ORM) | `core/audit/models.py` |
| Gestión de secretos por entorno | Sí | `settings.py`, `.env.example`, `.gitignore` |
| Cifrado en tránsito | No configurado en la aplicación | Depende del proxy (no existe configuración) |
| Cifrado en reposo | No | Depende de la infraestructura |
| Limitación de tasa | No | — |
| Escaneo antimalware | No | — |
