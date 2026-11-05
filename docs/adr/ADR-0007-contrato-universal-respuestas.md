# ADR-0007 — Contrato Universal de Respuestas JSON

- **Estado:** Aceptado
- **Fecha:** 2026-10-21
- **Relacionado con:** Constitución §V y §X; `plan.md` §2.2
- **Decisores:** Equipo de desarrollo CGE

## Contexto

Dos clientes distintos (Web en F2 y Móvil en F3) consumirán el mismo API. Se requiere un formato uniforme de respuesta y de errores para simplificar el consumo y estandarizar el manejo de fallos, sin exponer detalles internos.

## Decisión

Todas las respuestas **DEBEN** seguir el esquema unificado:

```json
{
  "success": true,
  "message": "string",
  "data": {},
  "errors": [],
  "meta": { "request_id": "string", "timestamp": "string", "version": "string" }
}
```

Los errores usan objetos `{ code, category, message }` con categorías Validación/Negocio/Autorización/Infraestructura y códigos HTTP estándar. `request_id` se propaga a los logs de auditoría.

## Consecuencias

- **Positivas:** contrato único, predecible y documentable en OpenAPI; facilita el manejo uniforme en ambos clientes.
- **Negativas:** ligera sobrecarga por metadatos en cada respuesta; requiere disciplina para no romper el contrato.

## Alternativas consideradas

- **Respuestas ad hoc por endpoint:** rechazada por inconsistencia y mayor costo de integración en F2/F3.
