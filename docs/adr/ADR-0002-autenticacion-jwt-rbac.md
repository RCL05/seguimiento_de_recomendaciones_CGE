# ADR-0002 — Autenticación JWT y RBAC a nivel de endpoint y recurso

- **Estado:** Aceptado
- **Fecha:** 2026-10-21
- **Relacionado con:** Constitución §VII; `plan.md` §4.1; `specify.md` RNF-02
- **Decisores:** Equipo de desarrollo CGE

## Contexto

El sistema maneja información sensible de control institucional. La Constitución exige autenticación segura, autorización por roles (Administrador, Responsable de Unidad, Validador, Auditor) y control de acceso a nivel de recurso (un usuario no debe gestionar recomendaciones ajenas a su área).

## Decisión

Usar autenticación basada en **JWT** firmado que transporta identidad, rol y unidad, y aplicar autorización en dos niveles: (1) restricción por rol en el endpoint, y (2) verificación de pertenencia al recurso por unidad. La separación de responsabilidades se garantiza a nivel de dominio (quien registra avance no aprueba su propio cumplimiento).

## Consecuencias

- **Positivas:** mecanismo sin estado, apto para web y móvil; control granular por rol y recurso.
- **Negativas:** requiere gestión de expiración/refresco y revocación; el contenido del token debe tratarse como no confiable.

## Alternativas consideradas

- **Sesiones de servidor:** rechazada por menor idoneidad para múltiples clientes (F2/F3).
- **Solo RBAC por rol sin control de recurso:** rechazada, incumple RNF-02 y Constitución §VII.
