## Fuente

Derivado de los modelos Django (`usuarios/models.py`, `recomendaciones/models.py`, `notificaciones/models.py`, `notificaciones/infrastructure/preferences_models.py`, `core/audit/models.py`) y de sus migraciones. Sustituye al esquema de `specs/…/data-model.md`, que conserva el catálogo de estados anterior (H-06). Fuente UML editable: `03_ARQUITECTURA/DIAGRAMAS/clases_dominio.puml`.

## Diagrama entidad-relación

```{mermaid}
erDiagram
  UNIDADES_ORGANICAS ||--o{ UNIDADES_ORGANICAS : "padre"
  UNIDADES_ORGANICAS ||--o{ USUARIOS : "unidad_org"
  UNIDADES_ORGANICAS ||--o{ RECOMENDACIONES : "unidad_responsable"
  USUARIOS ||--o{ INFORMES_CGE : "creado_por"
  INFORMES_CGE ||--o{ RECOMENDACIONES : "informe"
  RECOMENDACIONES ||--o{ PLANES_ACCION : "recomendacion"
  RECOMENDACIONES ||--o{ EVIDENCIAS : "recomendacion"
  PLANES_ACCION |o--o{ EVIDENCIAS : "plan_accion"
  RECOMENDACIONES ||--o{ DICTAMENES_UAI : "recomendacion"
  EVIDENCIAS |o--o{ DICTAMENES_UAI : "evidencia"
  USUARIOS ||--o{ DICTAMENES_UAI : "evaluador"
  USUARIOS ||--o{ EVIDENCIAS : "subido_por"
  USUARIOS ||--o{ PLANES_ACCION : "creado_por"
  USUARIOS |o--o{ AUDIT_LOGS : "usuario"
  USUARIOS ||--o{ NOTIFICACIONES : "destinatario"
  RECOMENDACIONES |o--o{ NOTIFICACIONES : "recomendacion"
  USUARIOS ||--o{ PREFERENCIAS_NOTIFICACION : "usuario"
  USUARIOS |o--o{ CONFIGURACION_NOTIFICACIONES : "actualizado_por"

  UNIDADES_ORGANICAS {
    uuid id PK
    varchar codigo UK
    varchar nombre
    bool activo
  }
  USUARIOS {
    uuid id PK
    varchar correo_institucional UK
    varchar nombres
    varchar rol
    uuid unidad_org_id FK
    bool activo
  }
  INFORMES_CGE {
    uuid id PK
    varchar numero_informe UK
    varchar periodo_auditado
    date fecha_notificacion
    varchar pdf_informe_url
    varchar pdf_informe
    timestamptz creado_en
  }
  RECOMENDACIONES {
    uuid id PK
    uuid informe_id FK
    varchar numero_recomendacion
    text descripcion
    varchar prioridad
    uuid unidad_responsable_id FK
    int plazo_legal_dias
    date fecha_vencimiento_legal
    varchar estado
    timestamptz vencimiento_registrado_en
    timestamptz creada_en
  }
  PLANES_ACCION {
    uuid id PK
    uuid recomendacion_id FK
    text descripcion_hito
    date fecha_compromiso
    bool completado
  }
  EVIDENCIAS {
    uuid id PK
    uuid recomendacion_id FK
    uuid plan_accion_id FK
    varchar nombre_archivo
    bigint tamano_bytes
    varchar hash_sha256
    varchar tipo
    varchar estado
    bool validada
  }
  DICTAMENES_UAI {
    uuid id PK
    uuid recomendacion_id FK
    uuid evidencia_id FK
    varchar resultado
    text observaciones_oficiales
    timestamptz fecha_dictamen
  }
  AUDIT_LOGS {
    bigint id PK
    uuid request_id
    timestamptz timestamp_utc
    inet ip_origen
    varchar accion
    varchar entidad
    uuid entidad_id
    varchar estado_anterior
    varchar estado_nuevo
    varchar resultado
    json detalles_json
  }
  NOTIFICACIONES {
    uuid id PK
    varchar tipo
    varchar clave_idempotencia UK
    timestamptz programada_en
    int intentos
    varchar estado
    bool leida
  }
  PREFERENCIAS_NOTIFICACION {
    uuid id PK
    varchar tipo_alerta
    bool notificar_interno
    bool notificar_email
  }
  CONFIGURACION_NOTIFICACIONES {
    smallint id PK
    smallint umbral_dias
    bool notificaciones_activas
    json destinatarios_vencimiento
    json destinatarios_mora
  }
```

## Restricciones e integridad

| Tabla | Restricción | Tipo | Origen |
|---|---|---|---|
| `unidades_organicas` | `codigo` único | Base de datos | `unique=True` |
| `usuarios` | `correo_institucional` único; `rol` ∈ {DTI, UAI, EJECUTOR, RECTORADO, CGE_AUDITOR} | BD / aplicación (`choices`) | modelo |
| `informes_cge` | `numero_informe` único | BD | modelo |
| `recomendaciones` | `UNIQUE (informe_id, numero_recomendacion)` (`uq_recomendacion_informe_numero`) | BD | `Meta.constraints` |
| `recomendaciones` | `plazo_legal_dias ≥ 1`; `estado` ∈ 5 valores | Aplicación (validadores/`choices`) | modelo |
| `evidencias` | `1 ≤ tamano_bytes ≤ 30 MB`; `hash_sha256` hexadecimal de 64 caracteres | Aplicación (validadores) | modelo |
| `notificaciones` | `clave_idempotencia` única | BD | garantiza idempotencia de alertas |
| `preferencias_notificacion` | `UNIQUE (usuario, tipo_alerta)` (`uq_preferencia_usuario_tipo`) | BD | `Meta.constraints` |
| `configuracion_notificaciones` | Fila única `id=1`; `umbral_dias` 1–90 | Aplicación | `load()` + validadores |
| `audit_logs` | Sin UPDATE/DELETE desde el ORM; `default_permissions = ()` | Aplicación | `ImmutableAuditLogQuerySet`, `save()`, `delete()` |
| Todas las FK | `on_delete=PROTECT` (excepto `preferencias_notificacion.usuario`: `CASCADE`) | BD | impide borrados en cascada que destruyan historial |

Los validadores de Django (`MinValueValidator`, `RegexValidator`, `choices`) **no** generan restricciones `CHECK` en la base de datos; se aplican en la capa de aplicación.

## Historial de migraciones

| App | Migraciones | Hitos relevantes |
|---|---|---|
| `core/audit` | `0001_initial`, `0002_auditlog_resultado`, `0003_alter_auditlog_options` | Campo `resultado`; opciones de inmutabilidad |
| `usuarios` | `0001_initial` | Usuarios y unidades |
| `recomendaciones` | `0001` … `0007` | `0003` evidencia validada; `0004` catálogo de 5 estados; `0005` estado/tipo de evidencia; `0006` PDF del informe; `0007` vencimiento como indicador (devuelve cada recomendación "vencida" a su estado real) |
| `notificaciones` | `0001_initial`, `0002_preferences_and_settings` | Preferencias y configuración |

## Datos iniciales

`backend/scripts/seed_initial_data.py` crea de forma idempotente las unidades `UAI`, `DEP-A`, `DTI` y `RECTORADO` y los usuarios de prueba asociados a los tokens de desarrollo.
