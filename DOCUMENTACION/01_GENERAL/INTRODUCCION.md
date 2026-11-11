## Presentación

**SITRA-CGE UNL** es un sistema web que permite a la Universidad Nacional de Loja (UNL) registrar, asignar, ejecutar, validar y auditar el cumplimiento de las recomendaciones emitidas por la Contraloría General del Estado (CGE) en sus informes de examen especial.

El sistema se compone de:

- una **API REST** en Django 5.2 y Django REST Framework, organizada como monolito modular por capas;
- una **aplicación web** (SPA) en React 19, TypeScript y Vite, con vistas diferenciadas por rol;
- una **base de datos relacional** (SQLite en desarrollo, PostgreSQL 16 en contenedores);
- un **almacenamiento privado** de documentos PDF con huella SHA-256;
- una **tarea programada** idempotente que evalúa plazos, emite alertas y registra vencimientos.

## Contexto

La CGE es el organismo de control del Ecuador. Cuando audita a una entidad pública emite informes con recomendaciones de cumplimiento obligatorio. Dentro de la UNL, la **Unidad de Auditoría Interna (UAI)** recibe esos informes, asigna cada recomendación a una unidad orgánica responsable y, finalmente, dictamina si el cumplimiento está respaldado por evidencia suficiente. La **máxima autoridad (Rectorado)** responde institucionalmente por ese cumplimiento.

## Antecedentes disponibles en el repositorio

| Antecedente | Fuente |
|---|---|
| Delimitación del problema y riesgo crítico normativo | `docs/problem-definition.md` |
| Especificación inicial (constitución, HU, clarificaciones CL-xx) | `.spec/` (histórico) |
| Especificación vigente con requisitos EARS y escenarios BDD | `specs/001-seguimiento-recomendaciones/spec.md` |
| Decisiones de arquitectura ADR-0001…ADR-0011 | `docs/adr/` |
| Historial de desarrollo (desde 2026-10-08) | `git log` |

El proyecto se desarrolló como trabajo académico de un equipo de cuatro integrantes (`docs/equipo-y-responsabilidades.md`) siguiendo **Spec-Driven Development** con GitHub Spec Kit (`docs/flujo-speckit.md`).

## Público destinatario de esta documentación

| Público | Capítulos recomendados |
|---|---|
| Evaluadores y docentes | Introducción, Requisitos, Trazabilidad, Calidad, Informe final |
| Desarrolladores nuevos | Arquitectura, Implementación, API, Despliegue |
| Responsables de seguridad | Seguridad, Riesgos y controles |
| Operación (DTI) | Configuración, Despliegue, Operación y mantenimiento |
| Usuarios funcionales (UAI, Rectorado) | Actores, Procesos |

## Convenciones de esta documentación

- **Verificado**: comprobado leyendo el código o ejecutando un comando durante la auditoría (2026-11-10).
- **Declarado**: afirmado por la especificación o por documentos previos, sin verificación independiente.
- Los identificadores `RF-xxx`, `RNF-xxx`, `SC-xxx` y `HUx` son los de `spec.md`; `H-xx` son hallazgos de esta auditoría (ver *Control maestro*).
