# ADR-0004 — Control de concurrencia optimista y pesimista

- **Estado:** Aceptado
- **Fecha:** 2026-10-21
- **Relacionado con:** Constitución §VI; `plan.md` §3.3
- **Decisores:** Equipo de desarrollo CGE

## Contexto

Pueden producirse actualizaciones simultáneas sobre la misma recomendación (por ejemplo, dos validadores actuando a la vez, o un cambio de estado mientras se carga una evidencia). La Constitución §VI exige evitar actualizaciones sobrepuestas.

## Decisión

Aplicar **control de concurrencia optimista** (columna de versión; conflicto → HTTP 409) como mecanismo por defecto para la actualización de recomendaciones, y **control pesimista** (bloqueo de fila) para las transiciones críticas de estado que compiten por el mismo recurso.

## Consecuencias

- **Positivas:** el modo optimista evita bloqueos en operaciones de lectura/modificación de baja contención; el pesimista garantiza consistencia en transiciones críticas.
- **Negativas:** requiere manejar y comunicar los conflictos (409) al cliente; exige que los clientes reintenten.

## Alternativas consideradas

- **Solo optimista:** insuficiente para transiciones concurrentes críticas.
- **Solo pesimista:** introduce bloqueos innecesarios en el resto de operaciones.
