# ADR-0008 — Contenedorización con Docker y configuración por entorno

- **Estado:** Aceptado
- **Fecha:** 2026-10-21
- **Relacionado con:** Constitución §XIII; `plan.md` §6.3
- **Decisores:** Equipo de desarrollo CGE

## Contexto

Se requiere reproducibilidad del entorno de desarrollo entre los integrantes del equipo y separación limpia de configuración entre desarrollo, pruebas y producción.

## Decisión

Usar **Docker** para el backend y **docker-compose** para el entorno de desarrollo (API + base de datos + almacenamiento de evidencias). La configuración se parametriza por variables de entorno, con archivos de ejemplo por entorno y sin secretos versionados.

## Consecuencias

- **Positivas:** entorno reproducible; paridad entre integrantes; base para CI y despliegue.
- **Negativas:** curva de aprendizaje inicial; requiere mantener los artefactos de contenedor actualizados.

## Alternativas consideradas

- **Instalación manual por integrante:** rechazada por inconsistencia de entornos.
- **Solo entornos gestionados externos:** rechazada en F1 por costo y dependencia.
