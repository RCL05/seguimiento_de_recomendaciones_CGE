## Actores humanos

Los roles están definidos en `Usuario.Rol` (`backend/modules/usuarios/models.py`) y en el tipo `Role` del frontend (`frontend/src/api/client.ts`). Cada usuario tiene **un único rol** y, opcionalmente, una unidad orgánica.

| Actor | Rol | Responsabilidades | Necesidad principal | Vista inicial en la SPA |
|---|---|---|---|---|
| Unidad de Auditoría Interna | `UAI` | Registrar informes y recomendaciones; revisar evidencias; emitir dictamen; reabrir; anular evidencias; consultar auditoría e integridad; exportar matriz | Controlar formalmente el cumplimiento | `/recomendaciones` |
| Responsable de unidad | `EJECUTOR` | Registrar hitos del plan de acción y cargar evidencias PDF de **su** unidad | Demostrar el avance de sus recomendaciones | `/planes` ("Mi bandeja") |
| Máxima autoridad | `RECTORADO` | Consultar tablero ejecutivo, informes, recomendaciones y matriz | Conocer el riesgo institucional y las unidades en mora | `/tablero` (tablero ejecutivo) |
| Auditor externo | `CGE_AUDITOR` | Consultar recomendaciones, auditoría, integridad de evidencias y matriz (solo lectura) | Verificación independiente | `/tablero` |
| Administrador | `DTI` | Gestionar usuarios, roles y unidades; configurar notificaciones; ejecutar la evaluación de plazos | Mantener la plataforma alineada con la estructura institucional | `/administracion/notificaciones` |

Fuente de la vista inicial: `LANDING_PATHS` en `frontend/src/routes.tsx`.

## Actores externos (sistemas)

| Actor | Interacción | Estado |
|---|---|---|
| SSO institucional UNL | Introspección OAuth2 del token del usuario (`SSO_INTROSPECTION_URL`) | Adaptador implementado; proveedor productivo no definido |
| Servidor SMTP institucional | Entrega de alertas por correo (`EMAIL_*`) | Implementado con `django.core.mail` |
| Contraloría General del Estado | Recibe la matriz CSV (entrega fuera del sistema) | Exportación implementada; sin integración directa |
| Programador de tareas (cron o servicio `scheduler`) | Ejecuta `manage.py evaluar_plazos` | Implementado |

## Interacciones principales

```{mermaid}
flowchart LR
  UAI([UAI]) -->|registra informe y recomendación| S[SITRA-CGE]
  EJ([Ejecutor]) -->|hitos y evidencias PDF| S
  UAI -->|dictamen / reapertura| S
  REC([Rectorado]) -->|consulta tablero| S
  CGE([Auditor CGE]) -->|consulta auditoría, integridad, matriz| S
  DTI([DTI]) -->|usuarios, roles, unidades, notificaciones| S
  S -->|introspección de token| SSO[[SSO UNL]]
  S -->|alertas| SMTP[[SMTP]]
  CRON[[Programador]] -->|evaluar_plazos| S
```

## Segregación de funciones verificada

- El ejecutor **no** puede emitir dictamen (`DictamenView` exige `UAI`).
- La UAI **no** carga evidencias (`EvidenciaUploadView` exige `EJECUTOR`).
- Solo la `DTI` administra usuarios y configuración (`SOLO_DTI`, `manage_notification_settings.py`).
- Un ejecutor solo accede a recomendaciones de su unidad; fuera de ella recibe `404` y el intento se audita (`get_recomendacion.py`, prueba `test_bola_entre_unidades_responde_404_y_audita_el_intento`).

## Usuarios de prueba (solo desarrollo)

Con `DJANGO_DEBUG=true`, `SsoAdapter` acepta tokens fijos: `uai-sso-token`, `valid-sso-token` (UAI), `ejecutor-sso-token` (DEP-A), `dti-sso-token`, `rectorado-sso-token`. **No existe token de desarrollo para `CGE_AUDITOR`**; ese rol debe asignarse por la DTI a un usuario existente. Los tokens se rechazan fuera de `DEBUG` (prueba `test_tokens_de_desarrollo_no_se_aceptan_fuera_de_debug`).
