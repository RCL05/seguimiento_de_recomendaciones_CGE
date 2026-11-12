## Fuentes del propio proyecto

| Fuente | Ubicación |
|---|---|
| Especificación vigente, plan, tareas, modelo de datos, contrato | `specs/001-seguimiento-recomendaciones/` |
| Especificación inicial (histórica) | `.spec/` |
| Decisiones de arquitectura | `docs/adr/ADR-0001…ADR-0011` |
| Documentación previa | `docs/*.md`, `docs/architecture/`, `docs/operations/` |
| Contrato OpenAPI | `backend/contracts/openapi.yaml` |
| Código fuente y pruebas | `backend/`, `frontend/` |
| Historial de cambios | `git log` del repositorio `RCL05/seguimiento_de_recomendaciones_CGE` |

## Documentación de tecnologías

Django [@django52], Django REST Framework [@drf], drf-spectacular [@drfspectacular], React [@react19], Vite [@vite], Vitest [@vitest], Playwright [@playwright], PostgreSQL [@postgresql16] y Quarto [@quarto].

## Estándares y especificaciones

- Contrato de API: OpenAPI 3.0.3 [@openapi303].
- Tokens y autenticación: JWT [@rfc7519] e introspección OAuth 2.0 [@rfc7662].
- Requisitos: sintaxis EARS [@ears] y escenarios BDD *Given/When/Then*.
- Procesos: BPMN 2.0.2 [@bpmn202].
- Arquitectura: modelo C4 [@c4model], Structurizr DSL [@structurizrdsl], PlantUML [@plantuml] y registros de decisión ADR [@nygard2011adr].
- Seguridad: OWASP Top 10 [@owasptop10] y OWASP API Security Top 10 [@owaspapi2023].
- Metodología: Spec-Driven Development con GitHub Spec Kit [@speckit].
- Publicación: GitHub Pages con flujos personalizados [@ghpages].

## Normativa aplicable

- **Acuerdo No. 010-CG-2022** de la Contraloría General del Estado, citado por la especificación como referencia para el catálogo de estados y la matriz de cumplimiento. El texto de la norma **no está incluido en el repositorio** y su correspondencia con el sistema está pendiente de validación por la UAI (H-09). Esta documentación no interpreta la norma.

## Herramientas utilizadas en esta documentación

| Herramienta | Uso |
|---|---|
| Quarto 1.11.9 (portable) | Construcción y verificación del portal |
| Mermaid (integrado en Quarto) | Vistas de diagramas C4, UML, ER y estados |
| bpmn-js 17.11.1 (en el navegador) | Visualización de los diagramas BPMN directamente desde sus fuentes `.bpmn` |
| pytest, Vitest, ESLint, Vite | Ejecución de pruebas y verificaciones registradas en *Resultados* |
| drf-spectacular | Regeneración y comparación del contrato |

## Declaración de uso de inteligencia artificial

- **En el desarrollo del proyecto**: el repositorio incluye agentes, *prompts* y *skills* de GitHub Spec Kit para asistentes de IA (`.github/agents/speckit.*.agent.md`, `.github/prompts/`, `.github/skills/`, `.specify/integrations/copilot.manifest.json`). Esto evidencia que el equipo utilizó asistentes de IA dentro del flujo SDD; el alcance concreto de su uso no consta en el repositorio y debe declararlo el equipo.
- **En esta documentación**: el análisis del código, la redacción de los capítulos, los diagramas, el portal Quarto y el workflow de publicación fueron elaborados con asistencia de un modelo de IA (Claude, de Anthropic) operando sobre el repositorio, a solicitud del equipo. Toda afirmación técnica se contrastó con el código o con la ejecución de comandos; las limitaciones se declaran explícitamente. El contenido debe ser revisado por el equipo antes de su entrega formal.

## Bibliografía
