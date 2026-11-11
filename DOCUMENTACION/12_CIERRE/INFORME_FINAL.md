## Resumen ejecutivo

Se analizó SITRA-CGE UNL (Django 5.2 + DRF / React 19 + Vite) sobre la rama `feature/sdd-spec-kit-structure` (commit `a565ba2`) y se produjo una documentación técnica verificada contra el código, publicada como portal Quarto en `docs/` y preparada para GitHub Pages mediante `.github/workflows/publish-quarto.yml`.

- El sistema implementa y prueba **23 de 24** requisitos funcionales; RF-001 (SSO) es parcial porque el proveedor productivo no está definido. RF-003 (reasignación) y RF-004 (reintento de correo) quedaron resueltos.
- La suite automatizada pasa completa: **145 pruebas de backend** y **12 de frontend**; lint y build correctos; el contrato OpenAPI regenerado coincide con el publicado.
- Se registraron **25 hallazgos** (H-01…H-25), de los cuales 4 eran de severidad alta: antimalware documentado pero inexistente (H-03), reintento SMTP inexistente (H-05, resuelto), `DEBUG=true` por defecto (H-10, resuelto) y rendimiento sin medición (H-19).
- El portal compila sin errores ni advertencias (44 páginas, 0 enlaces internos rotos). **No está publicado todavía**: requiere *merge* a `main` y activar Pages por el propietario.

## Descripción del proyecto

Plataforma web para que la Universidad Nacional de Loja registre las recomendaciones de la Contraloría General del Estado, las asigne a unidades con plazo legal, reciba evidencias PDF íntegras (SHA-256), permita el dictamen de la UAI y conserve una bitácora inmutable, con tablero ejecutivo y matriz CSV. Ver *Introducción* y *Arquitectura general*.

## Auditoría realizada

| Actividad | Alcance |
|---|---|
| Inventario técnico | Lenguajes, dependencias y versiones instaladas, módulos, persistencia, API, infraestructura |
| Auditoría documental | 22 entradas de inventario (incluidos 11 ADR y la especificación histórica) clasificadas como vigente, parcial, desactualizado o histórico |
| Revisión de código | Vistas, permisos, casos de uso, dominio, modelos, migraciones, adaptadores, configuración |
| Ejecución | `manage.py check`, pytest, regeneración del contrato, Vitest, ESLint, build |
| Contraste ADR ↔ código | 11 ADR: 6 cumplidos, 3 parciales, 1 superado, 1 implementado de hecho |

## Documentación generada

| Fase | Archivos fuente (`DOCUMENTACION/`) | Páginas del portal (`docs/`) |
|---|---|---|
| 0 Auditoría | `CONTROL_MAESTRO.md`, `00_AUDITORIA/*` (3) | `00-auditoria/*` (4) |
| 1 General | `01_GENERAL/*` (6) | `01-general/*` (6) |
| 2 Procesos | `02_PROCESOS/ANALISIS_PROCESOS.md` + 3 `.bpmn` | `02-procesos/procesos.qmd` |
| 3 Arquitectura | `03_ARQUITECTURA/*` (6) + `workspace.dsl` + 3 `.puml` | `03-arquitectura/*` (6) |
| 4 Implementación | `04_IMPLEMENTACION/*` (4) | `04-implementacion/*` (4) |
| 5 API | `05_API/*` (4) | `05-api/*` (4) |
| 6 Seguridad | `06_SEGURIDAD/*` (4) | `06-seguridad/*` (4) |
| 7 Calidad | `07_CALIDAD/*` (4) | `07-calidad/*` (4) |
| 8 Despliegue | `08_DESPLIEGUE/*` (6) | `08-despliegue/*` (6) |
| 9 Operación | `09_OPERACION/OPERACION_Y_MANTENIMIENTO.md` | `09-operacion/*` |
| 10 Referencias | `10_REFERENCIAS/REFERENCIAS.md`, `references.bib` (22 entradas) | `10-referencias/*` |
| 11 Publicación | `11_PUBLICACION_GITHUB_PAGES.md` | `11-publicacion/*` |
| 12 Cierre | `12_CIERRE/INFORME_FINAL.md` | `12-cierre/*` |
| Portal | — | `_quarto.yml`, `index.qmd`, `assets/styles/custom.scss`, `assets/scripts/{bpmn-viewer.html, sync-diagrams.ts}` |
| Automatización | — | `.github/workflows/publish-quarto.yml` |

Cada página del portal contiene solo metadatos, el objetivo y un `{{< include >}}` de su fuente: no hay contenido duplicado.

## Diagramas elaborados

| Diagrama | Fuente editable | Vista en el portal |
|---|---|---|
| BPMN P1, P2, P3 | `DOCUMENTACION/02_PROCESOS/DIAGRAMAS/*.bpmn` (BPMN 2.0 con DI) | Visor `bpmn-js` que dibuja la propia fuente |
| Estados de la recomendación | Mermaid en el capítulo | Mermaid |
| C4 C1, C2, C3 | `DOCUMENTACION/03_ARQUITECTURA/DIAGRAMAS/workspace.dsl` | Mermaid equivalente |
| UML clases, secuencias (dictamen, autenticación) | `clases_dominio.puml`, `secuencia_dictamen.puml`, `secuencia_autenticacion.puml` | Mermaid equivalente |
| Entidad-relación | Derivado de los modelos | Mermaid `erDiagram` |
| Capas, actores, pirámide de pruebas, despliegue recomendado | Mermaid en el capítulo | Mermaid |

## Validaciones realizadas

| Validación | Método | Resultado |
|---|---|---|
| Compilación del portal | `quarto render docs` (Quarto 1.11.9) | ✅ 44 páginas, salida 0, sin advertencias (la única advertencia inicial, una cita falsa por `@vitejs`, se corrigió) |
| Enlaces e recursos internos | Script que recorre los `href`/`src` de `docs/_site` | ✅ 3 625 enlaces internos, 0 rotos |
| Diagramas Mermaid | Navegador: 14 diagramas en 11 páginas | ✅ Todos renderizados, 0 errores de sintaxis |
| Diagramas BPMN | Navegador: carga de las 3 fuentes con `bpmn-js` | ✅ 21, 28 y 15 formas dibujadas |
| Fuentes BPMN | Análisis XML | ✅ Bien formadas (9, 14 y 8 flujos de secuencia) |
| Navegación | Barra superior, barra lateral con 13 secciones, búsqueda, migas | ✅ |
| Responsive | Viewport 375 × 812 en las páginas con tablas | ✅ Tras ajustar CSS, sin desplazamiento horizontal de página (las tablas anchas se desplazan dentro de sí mismas) |
| Bibliografía | Citas `[@…]` resueltas por citeproc | ✅ Sin citas no encontradas |
| Workflow | Revisión de sintaxis, permisos y eventos | ✅ Preparado; **no ejecutado** en GitHub |
| Exactitud técnica | Cada afirmación contrastada con código o comandos; correcciones aplicadas durante la redacción (p. ej. `due_date` lo envía el cliente; `approved` en lugar de `resultado`; `sessionStorage`) | ✅ |
| Fuentes Structurizr / PlantUML | — | ⏸️ No compiladas (requieren Structurizr CLI y PlantUML) |

## Matriz final

| ID | Elemento | Archivo | Evidencia | Estado | Observación |
|---|---|---|---|---|---|
| F-01 | Control maestro | `DOCUMENTACION/CONTROL_MAESTRO.md` | Tareas, 25 hallazgos, limitaciones | Completo | — |
| F-02 | Inventario técnico | `00_AUDITORIA/INVENTARIO_TECNICO.md` | `pip list`, manifiestos, árbol | Completo | — |
| F-03 | Auditoría documental | `00_AUDITORIA/AUDITORIA_DOCUMENTAL.md` | 22 entradas clasificadas | Completo | — |
| F-04 | Matriz de cumplimiento inicial | `00_AUDITORIA/MATRIZ_CUMPLIMIENTO.md` | 42 artefactos | Completo | — |
| F-05 | Introducción, problema, objetivos | `01_GENERAL/{INTRODUCCION,PROBLEMA_Y_JUSTIFICACION,OBJETIVOS_Y_ALCANCE}.md` | `spec.md`, código | Completo | — |
| F-06 | Actores | `01_GENERAL/ACTORES.md` | `Usuario.Rol`, `routes.tsx` | Completo | — |
| F-07 | Requisitos con estado | `01_GENERAL/REQUISITOS.md` | 24 RF, 13 RNF, 10 reglas | Completo | RF-001 parcial (SSO productivo) |
| F-08 | Trazabilidad | `01_GENERAL/MATRIZ_TRAZABILIDAD.md` | Nombres de pruebas verificados | Completo | Eslabones faltantes declarados |
| F-09 | Procesos y BPMN | `02_PROCESOS/*` | 3 `.bpmn` renderizados | Completo | — |
| F-10 | Arquitectura y C4 | `03_ARQUITECTURA/*` | DSL + Mermaid | Completo | DSL no compilado |
| F-11 | UML (C4 nivel 4) | `03_ARQUITECTURA/C4_UML.md` | 3 `.puml` + Mermaid | Completo | PlantUML no compilado |
| F-12 | ADR | `03_ARQUITECTURA/ADR.md` | 11 históricos + 4 recomendaciones | Completo | Recomendaciones en estado Propuesto |
| F-13 | Implementación y modelo de datos | `04_IMPLEMENTACION/*` | Modelos y migraciones | Completo | — |
| F-14 | API | `05_API/*` | Contrato + vistas + casos de uso | Completo | — |
| F-15 | Seguridad | `06_SEGURIDAD/*` | Código, pruebas de seguridad, OWASP | Completo | — |
| F-16 | Calidad y resultados | `07_CALIDAD/*` | Ejecución real 2026-11-10 | Completo | Sin cobertura ni E2E ejecutado |
| F-17 | Instalación y despliegue | `08_DESPLIEGUE/*` | Comandos ejecutados (local) | Completo | Docker no verificado; sin producción real |
| F-18 | Operación | `09_OPERACION/*` | Código | Completo | — |
| F-19 | Referencias y declaración de IA | `10_REFERENCIAS/*` | 22 referencias | Completo | Uso de IA del equipo por declarar |
| F-20 | Portal Quarto | `docs/_quarto.yml`, `docs/**/*.qmd` | Render 0 errores, 0 enlaces rotos | Completo | — |
| F-21 | Workflow de publicación | `.github/workflows/publish-quarto.yml` | Revisión | Preparado | No ejecutado en GitHub |
| F-22 | Guía de publicación y mantenimiento | `11_PUBLICACION_GITHUB_PAGES.md` | — | Completo | — |
| F-23 | Publicación real | https://rcl05.github.io/seguimiento_de_recomendaciones_CGE/ | — | **Pendiente** | Requiere acción del propietario |
| F-24 | Capturas de pantalla de la aplicación | — | — | No realizado | Fuera de lo verificado; ver limitaciones |
| F-25 | Manual de usuario | `docs/manual-usuario.md` (existente) | — | Sin cambios | Fuera del alcance técnico de este encargo |

## Resultado de compilación

```text
$ quarto render docs
Running script 'assets/scripts/sync-diagrams.ts'
sync-diagrams: 7 fuentes copiadas a …/docs/assets/diagrams/src
[44/44] 12-cierre/informe-final.qmd
Output created: _site/index.html
```

## Estado de publicación

**No publicado.** Los archivos y el workflow están listos, pero no se ha hecho *merge* a `main`, no se ha activado GitHub Pages y no se ejecutó el workflow en GitHub. La auditoría no tiene acceso administrativo al repositorio `RCL05/seguimiento_de_recomendaciones_CGE`. Los enlaces "Fuente única" del portal apuntan a `main` y devolverán 404 hasta el *merge*.

## Limitaciones

- Docker y Playwright no se ejecutaron en el equipo auditado; tampoco se midió cobertura.
- Structurizr DSL y PlantUML no se compilaron; las vistas Mermaid son equivalentes mantenidas a mano y pueden divergir si se edita solo una de las dos.
- El visor BPMN carga `bpmn-js` desde `unpkg.com`; sin acceso a ese CDN el diagrama muestra un mensaje y el enlace a la fuente.
- No se generaron capturas de pantalla de la aplicación.
- La correspondencia con el Acuerdo 010-CG-2022 no se pudo verificar (norma no incluida en el repositorio).

## Pendientes

| Pendiente | Responsable sugerido |
|---|---|
| *Merge* a `main`, activar Pages (fuente GitHub Actions) y verificar la URL | Propietario del repositorio |
| Revisar y aprobar el contenido; declarar el uso de IA del equipo | Equipo |
| Atender hallazgos de severidad alta pendientes (H-03, H-19) | Equipo de desarrollo |
| Actualizar documentos desactualizados de `docs/` y `specs/` (H-01, H-02, H-06, H-07, H-16, H-21, H-23) o marcarlos como históricos | Equipo |

## Instrucciones para entregar

1. Revisar el portal localmente: `quarto preview docs`.
2. Confirmar los cambios (archivos nuevos en `DOCUMENTACION/`, `docs/`, `.github/workflows/publish-quarto.yml`; modificados `.gitignore` y `.claude/launch.json`).
3. Abrir un pull request hacia `develop`/`main`; el workflow construirá el portal como verificación.
4. Tras el *merge* a `main`, seguir la guía de *Publicación en GitHub Pages* y entregar la URL **https://rcl05.github.io/seguimiento_de_recomendaciones_CGE/**.
