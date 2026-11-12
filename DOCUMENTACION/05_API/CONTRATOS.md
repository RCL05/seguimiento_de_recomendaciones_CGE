## Contrato OpenAPI

| Aspecto | Valor |
|---|---|
| Archivo publicado | `backend/contracts/openapi.yaml` (3 593 líneas) |
| Réplica | `specs/001-seguimiento-recomendaciones/contracts/openapi.yaml` |
| Versión OpenAPI | 3.0.3 (`OAS_VERSION`) |
| Título / versión | `SITRA-CGE UNL API` / `1.0.0` |
| Operaciones | 31 (23 rutas `/api/v1` + `/health/`) |
| Componentes | 75 esquemas, esquema de seguridad `bearerAuth` (HTTP bearer, JWT) |
| Enumeraciones con nombre | `RolInstitucionalEnum`, `EstadoRecomendacionEnum`, `EstadoEvidenciaEnum`, `TipoEvidenciaEnum`, `PrioridadEnum` |

### Verificación de correspondencia con la implementación

El proyecto aplica *contract-first* verificado por pruebas (`backend/tests/contract/test_api_contract.py`):

| Verificación | Prueba | Resultado (2026-11-11) |
|---|---|---|
| El contrato publicado es idéntico al generado desde el código | `test_contrato_publicado_coincide_con_el_codigo` | Aprobada |
| Toda ruta `/api/v1` está documentada | `test_toda_ruta_api_v1_esta_documentada` | Aprobada |
| Toda operación protegida declara `bearerAuth` y `401` | `test_operaciones_protegidas_declaran_bearer_y_401` | Aprobada |
| La envoltura de éxito y error respeta sus invariantes | `test_contract_envoltorio_exitoso_y_error` | Aprobada |

Además, durante la auditoría se regeneró el esquema con `python manage.py spectacular --file <tmp>` y se comparó con `diff`: **sin diferencias** respecto de ambas copias del contrato.

Discrepancia semántica conocida: el contrato documenta `403` para `GET /dashboard/kpis`, pero la implementación no restringe por rol (sí acota los datos del EJECUTOR a su unidad; H-14 parcial). La prueba de contrato compara estructura, no comportamiento de autorización.

### Regenerar el contrato

```bash
cd backend
python manage.py spectacular --file contracts/openapi.yaml
cp contracts/openapi.yaml ../specs/001-seguimiento-recomendaciones/contracts/openapi.yaml
python -m pytest tests/contract -q
```

## Envoltura universal de respuestas (ADR-0007, RF-015)

Éxito:

```json
{
  "success": true,
  "message": "Recomendación registrada",
  "data": { "id": "…", "state": "PENDIENTE" },
  "errors": null,
  "meta": {
    "request_id": "1f0e…-uuid-v4",
    "timestamp": "2026-11-10T15:04:05.123456+00:00",
    "version": "v1",
    "pagination": { "page": 1, "page_size": 25, "total": 40, "total_pages": 2, "has_next": true, "has_previous": false }
  }
}
```

Error:

```json
{
  "success": false,
  "message": "Transición inválida: PENDIENTE -> CUMPLIDA.",
  "data": null,
  "errors": { "code": "CONFLICT", "detail": "Transición inválida: PENDIENTE -> CUMPLIDA." },
  "meta": { "request_id": "…", "timestamp": "…", "version": "v1", "pagination": null }
}
```

Invariantes (RNF-004): `success=true ⇒ errors=null`; `success=false ⇒ data=null` y código 4xx/5xx. `meta.pagination` vale `null` salvo en los listados paginados. Los errores de validación de serializer incluyen el detalle por campo.

Excepciones a la envoltura: descargas de PDF (`application/pdf`), matriz (`text/csv; charset=utf-8`), y respuestas `204`, `304` y `HEAD` según `spec.md`.

## Contratos de datos relevantes

| Contrato | Regla |
|---|---|
| Fechas | `YYYY-MM-DD` en zona `America/Guayaquil` para fechas de negocio; `timestamp` y auditoría en UTC ISO-8601 |
| Identificadores | UUID para todos los recursos de negocio |
| Estados | `PENDIENTE`, `EN_PROCESO`, `EN_VALIDACION`, `REABIERTA`, `CUMPLIDA` |
| Prioridad | `ALTA`, `MEDIA`, `BAJA` |
| Evidencia | `type` ∈ {`BORRADOR`, `FINAL`}, `status` ∈ {`VIGENTE`, `ANULADA`} |
| CSV | UTF-8 con BOM, separador coma, salto `\n`, 10 columnas fijas |
