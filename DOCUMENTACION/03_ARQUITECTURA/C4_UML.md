## Propósito del nivel

El nivel 4 del modelo C4 (código) se documenta con UML para las piezas que concentran las reglas críticas: el modelo de dominio persistente, la máquina de estados y el flujo del dictamen. Fuentes editables PlantUML en `DIAGRAMAS/`:

| Diagrama | Fuente |
|---|---|
| Clases del modelo de dominio | `DIAGRAMAS/clases_dominio.puml` |
| Secuencia: emitir dictamen | `DIAGRAMAS/secuencia_dictamen.puml` |
| Secuencia: autenticación SSO → JWT | `DIAGRAMAS/secuencia_autenticacion.puml` |

Las vistas siguientes son equivalentes en Mermaid, renderizadas por Quarto.

## Diagrama de clases (modelos persistentes)

```{mermaid}
classDiagram
  direction LR
  class UnidadOrganica {
    UUID id
    str codigo «único»
    str nombre
    bool activo
  }
  class Usuario {
    UUID id
    str correo_institucional «único»
    str nombres
    Rol rol
    bool activo
  }
  class InformeCGE {
    UUID id
    str numero_informe «único»
    str periodo_auditado
    date fecha_notificacion
    url pdf_informe_url
    file pdf_informe
  }
  class Recomendacion {
    UUID id
    str numero_recomendacion
    str descripcion
    str prioridad
    int plazo_legal_dias
    date fecha_vencimiento_legal
    Estado estado
    datetime vencimiento_registrado_en
  }
  class PlanAccion {
    UUID id
    str descripcion_hito
    date fecha_compromiso
    bool completado
  }
  class Evidencia {
    UUID id
    str nombre_archivo
    int tamano_bytes
    str hash_sha256
    Tipo tipo
    Estado estado
    bool validada
  }
  class DictamenUAI {
    UUID id
    Resultado resultado
    str observaciones_oficiales
    datetime fecha_dictamen
  }
  class AuditLog {
    int id
    UUID request_id
    datetime timestamp_utc
    str accion
    str entidad
    str estado_anterior
    str estado_nuevo
    str resultado
    save() rechaza actualización
    delete() prohibido
  }
  class Notificacion {
    UUID id
    str tipo
    str clave_idempotencia «único»
    Estado estado
    int intentos
    bool leida
  }
  UnidadOrganica "0..1" <-- "*" UnidadOrganica : padre
  UnidadOrganica "0..1" <-- "*" Usuario : unidad_org
  InformeCGE "1" <-- "*" Recomendacion : informe
  UnidadOrganica "1" <-- "*" Recomendacion : unidad_responsable
  Recomendacion "1" <-- "*" PlanAccion
  Recomendacion "1" <-- "*" Evidencia
  PlanAccion "0..1" <-- "*" Evidencia
  Recomendacion "1" <-- "*" DictamenUAI
  Evidencia "0..1" <-- "*" DictamenUAI
  Usuario "1" <-- "*" DictamenUAI : evaluador
  Usuario "0..1" <-- "*" AuditLog : usuario
  Usuario "1" <-- "*" Notificacion : destinatario
  Recomendacion "0..1" <-- "*" Notificacion
```

Todas las claves foráneas usan `on_delete=PROTECT`, salvo `PreferenciaNotificacion.usuario` (`CASCADE`). El detalle de columnas y restricciones está en *Implementación → Modelo de datos*.

## Secuencia: emitir dictamen (`POST /api/v1/recomendaciones/{id}/dictamenes`)

```{mermaid}
sequenceDiagram
  autonumber
  actor UAI
  participant SPA as SPA (ReviewEvidencePage)
  participant V as DictamenView
  participant A as JWTBearerAuthentication
  participant UC as IssueDictamen
  participant SM as state_machine.transition_state
  participant DB as Base de datos
  participant AU as record_audit
  UAI->>SPA: Aprueba o rechaza la evidencia
  SPA->>V: POST …/dictamenes {evidence_id, approved, observaciones}
  V->>A: Validar Bearer JWT y cuenta activa
  A-->>V: Usuario (rol UAI)
  V->>V: require_roles(UAI) · serializer (observaciones obligatorias si approved=false)
  V->>UC: execute(actor, request_id, …)
  UC->>DB: BEGIN · SELECT … FOR UPDATE (recomendación)
  alt estado ≠ EN_VALIDACION
    UC-->>V: ConflictError → 409
  else evidencia ajena o anulada
    UC-->>V: ValidationError 400 / ConflictError 409
  else aprobado
    UC->>DB: evidencia.validada = true
    UC->>SM: EN_VALIDACION → CUMPLIDA (revisión + evidencia validada)
  else rechazado
    UC->>SM: EN_VALIDACION → EN_PROCESO
  end
  UC->>DB: INSERT dictamenes_uai · UPDATE recomendaciones.estado
  UC->>AU: INSERT audit_logs (ISSUE_DICTAMEN, estado anterior/nuevo)
  UC->>DB: COMMIT
  V-->>SPA: 201 {success, data: dictamen, meta.request_id}
```

## Secuencia: autenticación SSO → JWT

```{mermaid}
sequenceDiagram
  autonumber
  actor U as Usuario
  participant SPA
  participant L as LoginSsoView
  participant S as SsoAdapter
  participant IdP as SSO UNL (introspección)
  participant DB as Base de datos
  U->>SPA: Ingresa credencial / token SSO
  SPA->>L: POST /api/v1/auth/login-sso {credential}
  L->>S: authenticate(token=credential)
  alt DEBUG=true y token de desarrollo
    S->>S: identidad fija (uai/ejecutor/dti/rectorado)
  else
    S->>IdP: POST SSO_INTROSPECTION_URL (Basic client_id:secret)
    IdP-->>S: {active, email, role, unidad}
  end
  S->>DB: crear/actualizar Usuario y UnidadOrganica
  S->>S: emitir JWT HS256 (iss sitra-cge, aud sitra-cge-api, exp 1 h)
  L-->>SPA: 200 {access_token, token_type, expires_in, user_id, role, unit_id}
  Note over SPA: Guarda la sesión en sessionStorage
  Note over SPA,DB: Cada petición posterior envía Authorization Bearer JWT, revalidado contra la cuenta activa
```
