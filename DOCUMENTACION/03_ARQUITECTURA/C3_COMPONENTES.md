## Propósito del nivel

Descompone el contenedor **API REST** en sus componentes (módulos y piezas transversales) y muestra sus dependencias reales. Fuente editable: `DIAGRAMAS/workspace.dsl` (vista `componentesApi`).

## Diagrama de componentes de la API

```{mermaid}
flowchart TB
  spa["SPA web"]
  subgraph api["API REST (Django)"]
    urls["config/urls.py<br/>enrutamiento /api/v1"]
    subgraph core["core (transversal)"]
      auth["auth<br/>JWTBearerAuthentication · require_roles"]
      apic["api<br/>ApiView · envoltura · errores · request_id · health"]
      audit["audit<br/>AuditLog inmutable · record_audit"]
      sec["security<br/>redacción de secretos"]
    end
    usu["usuarios<br/>login SSO · usuarios · unidades"]
    inf["informes_cge<br/>registro y consulta de informes"]
    rec["recomendaciones<br/>estados · plan · dictamen · reapertura · vencimiento"]
    evi["evidencias<br/>carga · anulación · descarga · integridad"]
    noti["notificaciones<br/>alertas · mora · preferencias · configuración · job"]
    rep["reportes<br/>KPIs · tablero · matriz CSV · auditoría"]
  end
  db[("Base de datos")]
  fs[("Archivos PDF")]
  sso[["SSO"]]
  smtp[["SMTP"]]
  spa --> urls
  urls --> usu & inf & rec & evi & noti & rep
  usu & inf & rec & evi & noti & rep --> auth
  usu & inf & rec & evi & noti & rep --> apic
  inf & rec & evi & noti & usu --> audit
  inf --> rec
  evi --> rec
  noti --> rec
  rep --> rec
  rec --> usu
  usu --> sso
  noti --> smtp
  evi --> fs
  rec --> fs
  audit --> db
  rec --> db
```

## Componentes

| Componente | Ruta | Endpoints | Depende de |
|---|---|---|---|
| `core/auth` | `backend/core/auth/` | — (clases DRF) | `usuarios` (modelo `Usuario`, `SsoAdapter`) |
| `core/api` | `backend/core/api/` | `/health/` | — |
| `core/audit` | `backend/core/audit/` | — (consultado por `reportes`) | `usuarios` |
| `usuarios` | `backend/modules/usuarios/` | `sesiones`, `unidades`, `usuarios`, `usuarios/{id}` | `core` |
| `informes_cge` | `backend/modules/informes_cge/` | `informes`, `informes/{id}`, `informes/{id}/documento` | `core`, modelos de `recomendaciones` |
| `recomendaciones` | `backend/modules/recomendaciones/` | `recomendaciones`, `…/{id}`, `…/hitos`, `…/dictamenes` | `core`, `usuarios` |
| `evidencias` | `backend/modules/evidencias/` | `…/{id}/evidencias`, `evidencias/{id}`, `…/archivo`, `…/integridad` | `core`, modelos y casos de uso de `recomendaciones` |
| `notificaciones` | `backend/modules/notificaciones/` | `notificaciones`, `…/preferencias`, `…/configuracion` (la evaluación de plazos es el comando `evaluar_plazos`) | `core`, `usuarios`, `recomendaciones` |
| `reportes` | `backend/modules/reportes/` | `dashboard/kpis`, `reportes/tablero`, `reportes/matriz-cge`, `auditoria` | `core`, `recomendaciones`, `usuarios` |

Observación: el caso de uso de carga de evidencias reside en `recomendaciones/application/upload_evidencia.py` y la vista en `evidencias/presentation/views.py`; la frontera entre ambos módulos es, por tanto, de presentación y no de modelo.

## Componentes del frontend

| Componente | Ruta | Rol(es) |
|---|---|---|
| Shell, sesión y menú lateral | `src/App.tsx`, `src/routes.tsx` | Todos |
| Cliente HTTP tipado | `src/api/client.ts` | Todos |
| Registro de recomendaciones | `features/recomendaciones/pages/RegistroRecomendacionPage.tsx` | UAI |
| Revisión de evidencias | `features/evidencias/pages/ReviewEvidencePage.tsx` | UAI |
| Bandeja del ejecutor / plan de acción | `features/planes/pages/PlanAccionPage.tsx`, `features/evidencias/components/EvidenceUpload.tsx` | EJECUTOR |
| Tablero ejecutivo / KPIs | `features/dashboard/pages/ExecutiveDashboardPage.tsx`, `DashboardKPIs.tsx` | RECTORADO / resto |
| Auditoría y matriz | `features/auditoria/pages/AuditPage.tsx` | UAI, CGE_AUDITOR |
| Administración | `features/administracion/pages/UserAdminPage.tsx`, `NotificationSettingsPage.tsx` | DTI |
| UI común | `components/ui.tsx`, `FormStepper.tsx`, `Toast.tsx`, `format.ts`, `roles.ts` | — |
