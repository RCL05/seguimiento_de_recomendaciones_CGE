## Criterios

Cada documento existente se comparó con el código de la rama auditada (2026-11-10). Se clasificó como:

- **Vigente**: coincide con la implementación.
- **Parcial**: útil, pero con secciones desactualizadas o incompletas.
- **Desactualizado**: contradice el código o decisiones posteriores.
- **Histórico**: registro de una etapa anterior; se conserva, pero no es fuente de verdad.

Ningún documento existente fue eliminado ni reescrito. Las correcciones se reflejan en el portal y se registran como hallazgos.

## Inventario y clasificación

| Documento | Contenido | Estado | Reutilización / acción |
|---|---|---|---|
| `README.md` | Instalación, ejecución, tokens SSO, máquina de estados, problemas comunes | Vigente | Base de los capítulos 8 (Despliegue) y 1 (estados) |
| `specs/001-…/spec.md` | Actores, HU1–HU6, RF-001…RF-024, RNF-001…RNF-013, SC-001…SC-010, clarificaciones | Vigente (estado "en revisión") | Fuente principal de requisitos y trazabilidad |
| `specs/001-…/plan.md` | Contexto técnico, constitución, estructura | Parcial: menciona OpenAPI 3.1 (el contrato es 3.0.3) | Reutilizado en arquitectura y tecnologías |
| `specs/001-…/data-model.md` | Entidades y DDL lógico | Desactualizado: catálogo de estados antiguo (`EN_PLANIFICACION`, `EN_MORA`, `RECHAZADA_CORRECCION`); sin `estado`/`tipo`/`validada` en evidencias | Sustituido por el modelo de datos derivado de los modelos Django (cap. 4) |
| `specs/001-…/tasks.md` | 146 tareas T001–T088 | Desactualizado: 77 casillas sin marcar aunque existen los archivos y pruebas; describe estados y rutas antiguas | No se usa como evidencia de avance; ver H-07 |
| `specs/001-…/quickstart.md` | Escenarios de validación | Parcial | Referenciado en calidad |
| `specs/001-…/research.md` | Decisiones de investigación | Histórico | Referenciado en ADR |
| `specs/001-…/contracts/openapi.yaml` | Contrato | Vigente: idéntico a `backend/contracts/openapi.yaml` y al esquema generado | Fuente del capítulo de API |
| `backend/contracts/openapi.yaml` | Contrato publicado | Vigente (verificado por `test_contrato_publicado_coincide_con_el_codigo`) | Fuente del capítulo de API |
| `.spec/*.md` | Constitución, specify, clarify, plan, tasks de la etapa inicial | Histórico: otra numeración (HU-05, F-003, CL-xx) | Citado por los ADR; no es fuente vigente |
| `feature-map.md` | Mapa de funcionalidades inicial | Histórico | Contexto |
| `docs/ARQUITECTURA.md` | C4 en Mermaid, operación y despliegue | Vigente en lo esencial | Base de C1–C3 |
| `docs/architecture/sitra-cge.md` | C4 en texto, límites modulares, seguridad | Parcial / desactualizado: autenticación por cabeceras `X-User-ID`/`X-Role`, bloqueo optimista con `version`, antimalware, deuda técnica ya resuelta, enlaces a ADR inexistentes | Límites modulares reutilizados; resto corregido (H-01, H-02, H-03, H-16, H-21) |
| `docs/adr/ADR-0001…0011` | 11 decisiones | Vigentes como registro histórico; ADR-0003 "Propuesto" aunque PostgreSQL/SQLite ya están en uso | Consolidados en el capítulo ADR |
| `docs/operations/configuration.md` | Variables de entorno, SSO, SMTP, almacenamiento | Parcial: documenta variables que el código no lee (`EVIDENCE_STORAGE_BACKEND`, `EVIDENCE_S3_*`, `SSO_ISSUER`, `SSO_REDIRECT_URI`), reintentos SMTP exponenciales inexistentes, cabeceras `X-*` y tokens antiguos | Corregido en el capítulo de configuración (H-04, H-05) |
| `docs/manual-tecnico.md` | Guía técnica v0.1.0 (2026-10-20) | Parcial: describe la vista HTML de demostración y el estado anterior | Reemplazado funcionalmente por los capítulos 4 y 8 |
| `docs/manual-usuario.md` | Guía por rol | Parcial | Referenciado en actores |
| `docs/trazabilidad.md` | Método de trazabilidad y ejemplos | Vigente como método; rangos de tareas antiguos | Base de la matriz de trazabilidad |
| `docs/problem-definition.md` | Problema, actores, alcance, riesgo crítico | Vigente | Base de problema y justificación |
| `docs/hoja-de-ruta.md`, `docs/equipo-y-responsabilidades.md`, `docs/flujo-speckit.md`, `docs/control-questions.md` | Gestión del proyecto | Vigentes como contexto | Referenciados |
| `docs/README.md` | Índice de `docs/` | Vigente | Se mantiene; el portal Quarto convive con él |
| Swagger UI (`/api/docs/`) | Documentación viva de la API | Vigente | Referenciado |

## Información faltante antes de esta auditoría

- Diagramas de procesos (BPMN) y diagramas UML de código.
- Modelo entidad-relación alineado con las migraciones actuales.
- Matriz de riesgos y controles de seguridad.
- Registro de resultados reales de pruebas.
- Guía de despliegue y publicación de la documentación (GitHub Pages).
- Documento de operación (logging, salud, respaldos).

## Consolidación aplicada

- Requisitos: una sola fuente (`spec.md`), resumida y enlazada en el portal.
- Contrato: `backend/contracts/openapi.yaml` como fuente; la copia en `specs/` se declara réplica.
- Arquitectura: `docs/ARQUITECTURA.md` + `docs/architecture/sitra-cge.md` consolidados en el capítulo 3, corrigiendo lo desactualizado.
- Configuración: `README.md` + `docs/operations/configuration.md` + `.env.example` consolidados en el capítulo 8, marcando las variables sin efecto.
