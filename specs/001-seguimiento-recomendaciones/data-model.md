# Modelo de Datos: Seguimiento de Recomendaciones CGE

## Entidades y relaciones

- **UnidadOrgánica**: jerarquía de dependencias; una unidad puede tener una unidad
  padre y muchos usuarios y recomendaciones.
- **Usuario**: identidad institucional, rol, unidad y estado activo.
- **InformeCGE**: examen especial recibido, con número único y documento oficial.
- **Recomendación**: obligación de un informe, responsable, plazo, prioridad y estado.
- **PlanAcción**: hitos de una recomendación con fecha de compromiso y cumplimiento.
- **Evidencia**: PDF, metadatos, hash, almacenamiento y persona que carga.
- **DictamenUAI**: revisión aprobada o rechazada con observaciones.
- **AuditLog**: registro inmutable de mutaciones y transiciones.
- **Notificación**: alerta, destinatario, motivo, estado y reintentos.

## Esquema lógico normalizado

```sql
CREATE TYPE rol_institucional AS ENUM
  ('DTI', 'UAI', 'EJECUTOR', 'RECTORADO', 'CGE_AUDITOR');

CREATE TYPE estado_recomendacion AS ENUM
  ('PENDIENTE', 'EN_PLANIFICACION', 'EN_EJECUCION',
   'EN_REVISION_INTERNA', 'CUMPLIDA', 'RECHAZADA_CORRECCION', 'EN_MORA');

CREATE TYPE resultado_dictamen AS ENUM ('APROBADO', 'RECHAZADO');

CREATE TABLE unidades_organicas (
  id UUID PRIMARY KEY,
  codigo VARCHAR(50) NOT NULL UNIQUE,
  nombre VARCHAR(200) NOT NULL,
  padre_id UUID REFERENCES unidades_organicas(id),
  activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE usuarios (
  id UUID PRIMARY KEY,
  correo_institucional VARCHAR(320) NOT NULL UNIQUE,
  nombres VARCHAR(200) NOT NULL,
  rol rol_institucional NOT NULL,
  unidad_org_id UUID REFERENCES unidades_organicas(id),
  activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE informes_cge (
  id UUID PRIMARY KEY,
  numero_informe VARCHAR(100) NOT NULL UNIQUE,
  periodo_auditado VARCHAR(100) NOT NULL,
  fecha_notificacion DATE NOT NULL,
  pdf_informe_url TEXT NOT NULL,
  creado_por_id UUID NOT NULL REFERENCES usuarios(id),
  creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recomendaciones (
  id UUID PRIMARY KEY,
  informe_id UUID NOT NULL REFERENCES informes_cge(id),
  numero_recomendacion VARCHAR(50) NOT NULL,
  descripcion TEXT NOT NULL,
  prioridad VARCHAR(30) NOT NULL,
  unidad_responsable_id UUID NOT NULL REFERENCES unidades_organicas(id),
  plazo_legal_dias INTEGER NOT NULL CHECK (plazo_legal_dias > 0),
  fecha_vencimiento_legal DATE NOT NULL,
  estado estado_recomendacion NOT NULL DEFAULT 'PENDIENTE',
  creada_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (informe_id, numero_recomendacion)
);

CREATE TABLE planes_accion (
  id UUID PRIMARY KEY,
  recomendacion_id UUID NOT NULL REFERENCES recomendaciones(id),
  descripcion_hito TEXT NOT NULL,
  fecha_compromiso DATE NOT NULL,
  completado BOOLEAN NOT NULL DEFAULT FALSE,
  creado_por_id UUID NOT NULL REFERENCES usuarios(id)
);

CREATE TABLE evidencias (
  id UUID PRIMARY KEY,
  recomendacion_id UUID NOT NULL REFERENCES recomendaciones(id),
  plan_accion_id UUID REFERENCES planes_accion(id),
  nombre_archivo VARCHAR(255) NOT NULL,
  mime_type VARCHAR(100) NOT NULL CHECK (mime_type = 'application/pdf'),
  tamano_bytes BIGINT NOT NULL CHECK (tamano_bytes > 0),
  url_almacenamiento TEXT NOT NULL,
  hash_sha256 CHAR(64) NOT NULL CHECK (hash_sha256 ~ '^[0-9a-fA-F]{64}$'),
  fecha_carga TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  subido_por_id UUID NOT NULL REFERENCES usuarios(id),
  inmutable BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE dictamenes_uai (
  id UUID PRIMARY KEY,
  recomendacion_id UUID NOT NULL REFERENCES recomendaciones(id),
  evidencia_id UUID REFERENCES evidencias(id),
  evaluador_id UUID NOT NULL REFERENCES usuarios(id),
  resultado resultado_dictamen NOT NULL,
  observaciones_oficiales TEXT,
  fecha_dictamen TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_logs (
  id BIGSERIAL PRIMARY KEY,
  request_id UUID NOT NULL,
  usuario_id UUID REFERENCES usuarios(id),
  timestamp_utc TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ip_origen INET,
  modulo VARCHAR(100) NOT NULL,
  accion VARCHAR(100) NOT NULL,
  entidad VARCHAR(100) NOT NULL,
  entidad_id UUID,
  estado_anterior VARCHAR(50),
  estado_nuevo VARCHAR(50),
  detalles_jsonb JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE notificaciones (
  id UUID PRIMARY KEY,
  recomendacion_id UUID REFERENCES recomendaciones(id),
  destinatario_id UUID NOT NULL REFERENCES usuarios(id),
  tipo VARCHAR(50) NOT NULL,
  clave_idempotencia VARCHAR(200) NOT NULL UNIQUE,
  programada_en TIMESTAMPTZ NOT NULL,
  enviada_en TIMESTAMPTZ,
  intentos INTEGER NOT NULL DEFAULT 0,
  estado VARCHAR(30) NOT NULL
);
```

## Reglas de integridad y estado

1. La transición a `CUMPLIDA` requiere historial `EN_REVISION_INTERNA`, dictamen
   aprobado y evidencia PDF validada.
2. Un dictamen rechazado conserva evidencia y observaciones y mueve a
   `RECHAZADA_CORRECCION`.
3. El caso de uso bloquea la recomendación con `SELECT FOR UPDATE`, valida la
   transición, escribe el cambio y su `audit_log` dentro de la misma transacción.
4. Las cargas de evidencia validan PDF, tamaño, contenido, hash y autorización antes
   de crear el registro.
5. Las notificaciones usan `clave_idempotencia` para impedir duplicados.
6. Los usuarios ejecutores solo acceden a recomendaciones de su unidad.
