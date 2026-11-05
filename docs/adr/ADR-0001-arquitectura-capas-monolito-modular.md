# ADR-0001 — Arquitectura por capas con Monolito Modular

- **Estado:** Aceptado
- **Fecha:** 2026-10-21
- **Relacionado con:** Constitución §II y §III; `plan.md` §1
- **Decisores:** Equipo de desarrollo CGE

## Contexto

El sistema de seguimiento de recomendaciones CGE debe evolucionar en tres fases (F1 Backend, F2 Web, F3 Móvil) y crecer en capacidades (recomendaciones, evidencias, auditoría, RBAC, reportes). Se requiere separación de responsabilidades y bajo acoplamiento sin adoptar la complejidad prematura de microservicios.

## Decisión

Adoptar una arquitectura de cuatro capas (Presentación/API, Aplicación, Dominio, Infraestructura/Persistencia) implementada como **Monolito Modular**, con límites por capacidad de negocio y dependencias dirigidas hacia el dominio.

## Consecuencias

- **Positivas:** independencia del dominio respecto al framework; testeabilidad; posibilidad de extraer módulos a servicios en el futuro si fuese necesario; un único despliegue en F1.
- **Negativas:** disciplina requerida para respetar límites entre módulos; riesgo de acoplamiento si no se revisa.

## Alternativas consideradas

- **Microservicios desde F1:** rechazada por sobreingeniería frente al tamaño del equipo y del alcance (Constitución §II).
- **Monolito en capas sin módulos:** rechazada por menor cohesión y mayor acoplamiento entre capacidades.
