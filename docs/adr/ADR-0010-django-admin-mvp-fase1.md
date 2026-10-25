# ADR-0010 — Django Admin como MVP interno de Fase 1

- **Estado:** Aceptado (excepción arquitectónica registrada)
- **Fecha:** 2026-10-21
- **Relacionado con:** Constitución §II, §IV, §XVI; `plan.md` §7; ADR-0003
- **Decisores:** Equipo de desarrollo CGE

## Contexto

La Constitución §II exige arquitectura por capas con dominio independiente del framework y Monolito Modular; §IV exige un API REST documentado con OpenAPI; §XVI define F1 como "API backend robusto". El equipo recibió la indicación de implementar una o dos funcionalidades usando **Django Admin** como primer entregable de la Fase 1.

Django Admin es una interfaz de gestión interna generada por el framework, no un API REST, y su modelo de dominio queda acoplado al ORM de Django.

## Decisión

Adoptar **Django Admin como MVP interno de Fase 1** para las funcionalidades de mayor valor y menor riesgo, empezando por **F-001 (Recomendaciones + Responsables)**. El API REST (Constitución §IV) queda planificado para una etapa posterior de F1. Se implementaron las entidades `Unidad`, `Responsable`, `Recomendacion` y `Asignacion` (N:M) con reglas básicas del dominio (plazo obligatorio, fecha límite ≥ emisión, estado, prioridad).

Se registra esta decisión como **excepción arquitectónica explícita**, conforme a la gobernanza de la Constitución ("Toda excepción arquitectónica DEBE ser explícita, justificada y aprobada").

## Consecuencias

- **Positivas:** entregable funcional rápido y verificable; valida el modelo de datos con usuarios reales; bajo costo de implementación; base para migrar reglas al dominio cuando se construya el API REST.
- **Negativas:** incumple temporalmente §II/§IV; el dominio queda acoplado al framework mientras dure el MVP; la lógica en `admin.py`/`models.py` deberá extraerse a una capa de dominio/servicios al construir el API.

## Cumplimiento parcial ya aplicado

- Dominio modelado con reglas de negocio (validación de fechas, estados, prioridad) — avance hacia §II/§VIII.
- Metadatos de auditoría (`creado_en`, `actualizado_en`) — avance hacia §VII.
- Control de datos de prueba no versionados (`db.sqlite3` en `.gitignore`) y entorno reproducible (`requirements.txt`) — §XIII.

## Alternativas consideradas

- **Django REST Framework desde el inicio:** preferible para cumplir §IV, pero descartado como primer paso por indicación del requirente; queda como siguiente hito.
- **Solo documentación sin entregable funcional:** rechazado por no aportar valor demostrable.

## Pendientes

- Implementar el API REST (DRF u equivalente) para cumplir §IV.
- Extraer la lógica de negocio de `admin.py` a servicios de dominio.
- Resolver las clarificaciones CL-01/CL-05/CL-07 antes del flujo de estados y evidencias.
