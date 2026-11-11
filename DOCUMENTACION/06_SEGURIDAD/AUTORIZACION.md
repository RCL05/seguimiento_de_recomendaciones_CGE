## Modelo

La autorización se aplica **siempre en el servidor** (RNF-003) y en dos niveles:

1. **Por rol (RBAC)** en la vista: `IsAuthenticatedActor` + `require_roles(...)` (`backend/core/auth/permissions.py`). Fallo → **403 `PERMISSION_DENIED`**.
2. **Por objeto** en el caso de uso: el ejecutor solo opera sobre recomendaciones y evidencias de **su unidad**. Fallo → **404 `RESOURCE_NOT_FOUND`** idéntico al de un recurso inexistente, y registro `ACCESS_DENIED` en `AuditLog` (RF-019, protección BOLA/IDOR).

Los casos de uso repiten la comprobación de rol aunque la vista ya la haya hecho (defensa en profundidad): p. ej. `export_matriz_cge_csv`, `get_dashboard`, `reabrir_recomendacion`.

## Matriz rol × operación (verificada en código)

✔ permitido · ◐ permitido con restricción de objeto · — denegado

| Operación | UAI | EJECUTOR | RECTORADO | CGE_AUDITOR | DTI |
|---|---|---|---|---|---|
| Registrar informe | ✔ | — | — | — | — |
| Consultar informes / documento | ✔ | — | ✔ | ✔ | — |
| Registrar recomendación | ✔ | — | — | — | — |
| Listar / consultar recomendación y hitos | ✔ | ◐ su unidad | ✔ | ✔ | — |
| Reabrir recomendación | ✔ | — | — | — | — |
| Registrar hito | — | ◐ su unidad | — | — | — |
| Cargar evidencia | — | ◐ su unidad | — | — | — |
| Anular evidencia | ✔ | — | — | — | — |
| Descargar evidencia | ✔ (incl. anuladas) | ◐ su unidad, no anuladas | — | — | — |
| Verificar integridad | ✔ | — | — | ✔ | — |
| Emitir dictamen | ✔ | — | — | — | — |
| Tablero ejecutivo | ✔ | — | ✔ | ✔ | — |
| KPIs | ✔ | ✔ | ✔ | ✔ | ✔ (sin restricción, H-14) |
| Matriz CSV | ✔ | — | ✔ | ✔ | — |
| Consultar auditoría | ✔ | — | — | ✔ | — |
| Bandeja de notificaciones | ◐ propias | ◐ propias | ◐ propias | ◐ propias | ◐ propias |
| Preferencias de notificación | ◐ propias | ◐ propias | ◐ propias | ◐ propias | ✔ de cualquiera |
| Configuración de notificaciones | — | — | — | — | ✔ |
| Ejecutar evaluación de plazos | — | — | — | — | ✔ |
| Catálogo de unidades | ✔ | — | — | — | ✔ |
| Registrar unidad / gestionar usuarios y roles | — | — | — | — | ✔ |

## Segregación de funciones

| Regla | Mecanismo |
|---|---|
| Quien ejecuta no aprueba su propio cumplimiento | Carga = EJECUTOR; dictamen = UAI |
| Quien administra identidad no opera el flujo | DTI no tiene acceso a recomendaciones (`ALLOWED_ROLES` excluye DTI) |
| El auditor externo solo lee | CGE_AUDITOR sin operaciones mutativas |
| Una cuenta tiene un único rol | Campo `Usuario.rol` |

## Frontend

`frontend/src/routes.tsx` filtra el menú por rol con los mismos conjuntos que el backend. Es una ayuda de usabilidad (RNF-011): **no** es un control de seguridad; el backend rechaza igualmente cualquier llamada no autorizada.

## Pruebas

| Prueba | Control |
|---|---|
| `tests/security/test_evidence_object_authorization.py` (2) | BOLA/IDOR → 404 sin revelar existencia y auditado |
| `tests/integration/test_quickstart.py::test_bola_entre_unidades_responde_404_y_audita_el_intento` | BOLA en flujo completo |
| `tests/unit/test_mvp.py::test_executor_cannot_upload_for_another_unit` | Carga en otra unidad |
| `tests/integration/test_foundation.py::test_autorizacion_por_rol_y_unidad` | Rol y unidad |
| `tests/security/test_audit_and_reports.py` | Auditoría y matriz restringidas por rol |
| `tests/api/test_endpoints_base.py::test_integridad_no_disponible_para_ejecutor` | Integridad restringida |
| `tests/integration/notificaciones/test_settings_flow.py::test_usuario_no_puede_consultar_preferencias_de_otro` | Preferencias propias |
| `tests/unit/notificaciones/test_settings_rules.py::test_solo_dti_configura_y_segregacion_de_funciones` | Configuración solo DTI |
