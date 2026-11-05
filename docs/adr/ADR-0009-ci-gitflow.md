# ADR-0009 — Integración Continua y ramas GitFlow

- **Estado:** Aceptado
- **Fecha:** 2026-10-21
- **Relacionado con:** Constitución §XII y §XIII; `plan.md` §6.3
- **Decisores:** Equipo de desarrollo CGE

## Contexto

La Constitución exige GitFlow, Pull Requests con revisión y validaciones automatizadas, y CI con análisis estático y ejecución de pruebas. El equipo trabaja con ramas `feature/*` en paralelo.

## Decisión

Adoptar el modelo **GitFlow** (`main`, `develop`, `feature/*`, `release/*`, `hotfix/*`) y una **pipeline de Integración Continua** que ejecuta análisis estático, pruebas (unitarias, integración, autorización) y lint del contrato OpenAPI. Ningún cambio se fusiona a `develop` o `main` sin PR revisado y CI en verde.

## Consecuencias

- **Positivas:** trazabilidad de cambios, calidad verificable, menos conflictos entre integrantes.
- **Negativas:** requiere disciplina de ramas y mantenimiento de la pipeline.

## Alternativas consideradas

- **Trunk-based development:** no fue el modelo acordado por el equipo (Constitución §XII).
- **Sin CI:** rechazada, incumpliría §IX y §XIII.
