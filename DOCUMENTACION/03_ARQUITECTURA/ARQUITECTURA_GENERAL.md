## Estilo arquitectónico

SITRA-CGE es un **monolito modular** con **arquitectura por capas** inspirada en arquitectura limpia (ADR-0001), acompañado de una **SPA** independiente que consume la API por HTTP/JSON.

- **Monolito**: un único proceso Django sirve toda la API; una única base de datos.
- **Modular**: el código de negocio se divide por capacidad en `backend/modules/<módulo>/`.
- **Por capas**: cada módulo separa `presentation` → `application` → `domain`, con `infrastructure` como adaptador.
- **Puertos y adaptadores** para servicios externos: SSO (`usuarios/ports/sso_port.py`), notificación (`notificaciones/ports/notification_port.py`), almacenamiento (`core/files/storage_ports.py`).

## Capas

```{mermaid}
flowchart TB
  P["Presentación<br/>views.py · serializers.py · urls.py<br/>(DRF, drf-spectacular)"]
  A["Aplicación<br/>casos de uso: create_*, issue_*, upload_*, get_*<br/>transacciones y auditoría"]
  D["Dominio<br/>state_machine · vencimiento · plan_accion · dictamen<br/>(sin dependencias de Django)"]
  I["Infraestructura<br/>models (ORM) · repositories · storage · smtp · sso_adapter"]
  C["core<br/>api · auth · audit · security · shared"]
  P --> A --> D
  A --> I
  P -.-> C
  A -.-> C
```

| Capa | Responsabilidad | Ejemplo verificado |
|---|---|---|
| Presentación | Validar forma de la entrada, invocar el caso de uso, construir la envoltura, documentar OpenAPI | `recomendaciones/presentation/views.py::DictamenView` |
| Aplicación | Orquestar la operación: autorización de objeto, bloqueo, transición, persistencia y auditoría en una transacción | `recomendaciones/application/issue_dictamen.py` |
| Dominio | Reglas puras: transiciones permitidas, vencimiento, fechas de hitos | `recomendaciones/domain/state_machine.py`, `domain/vencimiento.py` |
| Infraestructura | ORM, consultas anotadas, archivos, correo, SSO | `recomendaciones/infrastructure/repositories.py::anotar_vencimiento`, `storage.py` |
| `core` | Elementos transversales | `core/api/response_envelope.py`, `core/auth/authentication.py`, `core/audit/models.py` |

**Desviaciones verificadas** respecto del ideal de capas:

- Los modelos ORM de `informes_cge` y `evidencias` viven en `recomendaciones/models.py`; esos módulos no son apps Django propias.
- Algunas vistas consultan el ORM directamente (p. ej. `BandejaView` en notificaciones), sin caso de uso intermedio.
- El dominio usa `RecommendationState` de `core/shared/domain_types.py`, mientras el ORM usa `Recomendacion.Estado`; ambos catálogos coinciden en valores.

## Componentes principales

| Componente | Tipo | Responsabilidad |
|---|---|---|
| SPA (`frontend/`) | React 19 + Vite | Vistas por rol, sesión JWT en `sessionStorage`, cliente HTTP tipado |
| API (`backend/`) | Django 5.2 + DRF | Reglas de negocio, autorización, persistencia, auditoría |
| Base de datos | SQLite / PostgreSQL 16 | Datos transaccionales y bitácora |
| Almacenamiento de archivos | Sistema de archivos (`MEDIA_ROOT`) | PDF de evidencias e informes, no expuesto como estático |
| Programador | Servicio `scheduler` (Compose) o cron | Ejecuta `evaluar_plazos` |
| Documentación | Swagger UI, Quart (`docs_server/`), portal Quarto | Contrato y documentación |

## Comunicación

| Origen → destino | Protocolo | Formato | Autenticación |
|---|---|---|---|
| Navegador → SPA | HTTP (Vite dev server :5173) | HTML/JS | — |
| SPA → API | HTTP; en desarrollo vía proxy de Vite (`/api`, `/health`) | JSON con envoltura universal; PDF binario en cargas | `Authorization: Bearer <JWT>` |
| API → base de datos | Driver Django (sqlite3 / psycopg 3) | SQL | Credenciales por entorno |
| API → SSO | HTTPS POST (introspección OAuth2) | `application/x-www-form-urlencoded` → JSON | Basic (`SSO_CLIENT_ID`/`SSO_CLIENT_SECRET`) |
| API → SMTP | SMTP con STARTTLS opcional | Texto plano | `EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD` |
| Programador → API | Invocación de comando de gestión en el mismo contenedor | — | — |

## Límites modulares

Los límites declarados en `docs/architecture/sitra-cge.md` (§3) siguen siendo la referencia. La auditoría observó que `reportes` y `notificaciones` leen directamente modelos de `recomendaciones` y `usuarios`, lo que respeta la dirección permitida (lectura), y que `informes_cge`/`evidencias` dependen de los modelos de `recomendaciones` (no solo de identificadores). No existen pruebas automáticas que verifiquen los límites de importación.

## Atributos de calidad y tácticas

| Atributo | Táctica implementada |
|---|---|
| Integridad del negocio | Máquina de estados en dominio; transiciones en transacción con bloqueo de fila |
| Trazabilidad | `AuditLog` append-only escrito en la misma transacción que el cambio |
| Seguridad | JWT revalidado contra la cuenta activa en cada petición; RBAC + autorización de objeto; archivos privados |
| Interoperabilidad | OpenAPI 3.0.3 generado del código y verificado en pruebas; CSV UTF-8 con BOM |
| Disponibilidad | Fallo de correo no revierte la operación de negocio |
| Mantenibilidad | Capas, casos de uso pequeños, 145 pruebas backend y 12 de frontend |
