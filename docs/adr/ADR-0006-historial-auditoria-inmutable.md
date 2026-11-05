# ADR-0006 — Historial de auditoría append-only e inmutable

- **Estado:** Aceptado
- **Fecha:** 2026-10-21
- **Relacionado con:** Constitución §VII y §VIII; `plan.md` §3.5; `specify.md` §3.4
- **Decisores:** Equipo de desarrollo CGE

## Contexto

La trazabilidad es el núcleo del sistema: debe registrarse quién cambió el estado, cuándo, desde qué IP y qué evidencia adjuntó, sin posibilidad de alteración posterior. La anulación de una evidencia debe conservar el historial.

## Decisión

Implementar el historial como una estructura **append-only e inmutable**: solo se permiten inserciones. Se revocan los permisos de `UPDATE` y `DELETE` a nivel de base de datos para el usuario de la aplicación, además de prohibirlos en la capa de dominio. Cada registro incluye actor, rol, IP, timestamp, acción, estado anterior/nuevo y evidencia asociada. La anulación de evidencia no elimina el registro original.

## Consecuencias

- **Positivas:** trazabilidad verificable y a prueba de manipulación; respalda la validez de la auditoría.
- **Negativas:** crecimiento continuo del historial; requiere estrategia de retención/particionado (ver CL-10) y de respaldo.

## Alternativas consideradas

- **Tabla mutable con logs de aplicación:** rechazada por no garantizar inmutabilidad ante accesos indebidos.
- **Logs externos únicamente:** rechazada por dificultar la consulta probatoria desde el sistema.
