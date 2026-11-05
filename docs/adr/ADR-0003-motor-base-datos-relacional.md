# ADR-0003 — Motor de base de datos relacional

- **Estado:** Propuesto (pendiente de selección definitiva)
- **Fecha:** 2026-10-21
- **Relacionado con:** Constitución §VI; `plan.md` §3
- **Decisores:** Equipo de desarrollo CGE

## Contexto

El sistema requiere integridad referencial estricta entre recomendaciones, responsables, tareas, evidencias e historial; transacciones atómicas; y control de concurrencia. El dominio es inherentemente relacional (relaciones N:M recomendación↔responsable, dependencias por clave foránea).

## Decisión

Adoptar una **base de datos relacional** como almacén transaccional principal. La selección del motor concreto (PostgreSQL u otro equivalente) **DEBE** confirmarse por el equipo responsable del stack tecnológico, considerando: transacciones ACID, restricciones `CHECK` y de clave foránea, permisos a nivel de tabla (para inmutabilidad del historial) y soporte de versionado optimista.

## Consecuencias

- **Positivas:** integridad referencial nativa; transacciones; madurez operativa.
- **Negativas:** la decisión está incompleta hasta fijar el motor; algunos motores ofrecen controles de permisos más finos que otros.

## Alternativas consideradas

- **Almacén no relacional:** rechazado como almacén principal por la necesidad de integridad referencial estricta (Constitución §VI); podría usarse auxiliarmente en fases posteriores.

## Preguntas abiertas

- ¿Qué motor específico adopta el equipo? (responsable del stack tecnológico).
