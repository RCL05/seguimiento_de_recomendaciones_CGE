## Información tratada

| Dato | Clasificación | Dónde se almacena | Quién accede |
|---|---|---|---|
| Correo institucional y nombre | Dato personal | `usuarios` | DTI (gestión); el propio usuario (sesión) |
| Rol y unidad | Dato institucional | `usuarios`, JWT | Sistema; DTI |
| Informes CGE (PDF) | Documento oficial reservado | `MEDIA_ROOT/informes/` | UAI, RECTORADO, CGE_AUDITOR |
| Evidencias (PDF) | Documento institucional | `MEDIA_ROOT/evidencias/<uuid>.pdf` | UAI; ejecutor de la unidad |
| Dictámenes y observaciones | Registro oficial | `dictamenes_uai` | Usuarios con acceso a la recomendación |
| Bitácora (IP, actor, acciones) | Registro de seguridad | `audit_logs` | UAI, CGE_AUDITOR |
| Secretos (JWT, SMTP, SSO, BD) | Secreto | Variables de entorno | Operación |

## Medidas implementadas

| Medida | Detalle | Evidencia |
|---|---|---|
| Archivos no públicos | `MEDIA_ROOT` no se sirve como estático, ni siquiera con `DEBUG` | `config/urls.py`; `test_media_no_se_publica_ni_con_debug` |
| Nombres opacos | El archivo se guarda como `<uuid>.pdf`; el nombre original solo como metadato | `storage.py` |
| Minimización en logs | Redacción recursiva de claves sensibles (`authorization`, `cookie`, `password`, `secret`, `token`, `smtp`, `api_key`, `private_key`…) | `core/security/log_safety.py`; `test_logs_redactados_no_incluyen_el_secreto` |
| Sin secretos en la base de datos | La configuración de notificaciones rechaza claves con aspecto de secreto y no las audita | `test_configuracion_rechaza_secretos_sin_persistirlos_ni_auditarlos` |
| Respuestas sin eco de secretos | Los errores no devuelven el valor rechazado | `test_api_no_ecoa_el_secreto_en_la_respuesta_de_error` |
| Errores sin trazas | Manejador de excepciones uniforme; `SafeExceptionReporterFilter` | `exception_handler.py` |
| Respuesta 404 uniforme | No revela si un recurso de otra unidad existe | RF-019 |
| Conservación del historial | Evidencias anuladas, no borradas; FK `PROTECT`; bitácora inmutable | modelos |
| Secretos fuera de Git | `.env` y `.env.*` ignorados; solo `.env.example` con valores de ejemplo | `.gitignore` |

## Observaciones

- `docker-compose.yml` contiene **valores por defecto de desarrollo** para `POSTGRES_PASSWORD`, `DJANGO_SECRET_KEY` y `JWT_SIGNING_KEY` (marcados "change-me"). Son aceptables solo en local; un despliegue debe sobreescribirlos.
- No hay política de **retención** ni de **eliminación** de datos personales definida (`spec.md` la deja para la planificación con las áreas responsables).
- No hay cifrado en reposo gestionado por la aplicación; depende de la infraestructura (disco, volumen o servicio de base de datos).
- La normativa ecuatoriana de protección de datos personales aplicable a la UNL debe ser evaluada por las instancias competentes; esta documentación no constituye análisis legal.

## Recomendaciones

1. Definir retención de bitácora, evidencias y notificaciones con la UAI y la DTI.
2. Cifrar volúmenes de base de datos y archivos, y los respaldos.
3. Añadir `X-Content-Type-Options: nosniff` y `Content-Disposition` controlado en las descargas (verificar con una prueba).
4. Registrar accesos de lectura a documentos sensibles si la UAI lo requiere (hoy se auditan las mutaciones y los accesos denegados).
