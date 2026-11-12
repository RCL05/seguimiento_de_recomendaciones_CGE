## Datos de publicación

| Dato | Valor |
|---|---|
| Repositorio de las fuentes | `RCL05/seguimiento_de_recomendaciones_CGE` (rama `main`, carpetas `docs/` y `DOCUMENTACION/`) |
| Repositorio de publicación | `BrTrl3/sitra-cge-docs` (público) |
| URL pública | **https://brtrl3.github.io/sitra-cge-docs/** |
| Proyecto Quarto | `docs/` (`docs/_quarto.yml`) |
| Salida | `docs/_site/` (no versionada) |
| Workflow de publicación | `.github/workflows/publicar.yml` en `BrTrl3/sitra-cge-docs` |
| Workflow de verificación | `.github/workflows/publish-quarto.yml` en este repositorio |
| Fuente de Pages | **GitHub Actions** |

Se publica desde un repositorio aparte porque activar Pages y guardar secretos en el
repositorio del proyecto requiere permisos de administración. El repositorio de
publicación no necesita tokens: el proyecto es público y su workflow lo descarga.

## Cómo funcionan los workflows

| Workflow | Evento | Qué hace |
|---|---|---|
| `publish-quarto.yml` (proyecto) | `push` a `main` o `develop`, o `pull_request`, que toque `docs/**`, `DOCUMENTACION/**` o el workflow | Solo **construye** el portal para verificar que compila |
| `publicar.yml` (`sitra-cge-docs`) | Todos los días a las 06:00 (Ecuador), a mano o con un `push` a su `main` | Descarga `main` del proyecto, construye y **publica** |

Pasos de `publicar.yml`: `actions/checkout@v4` del proyecto → `quarto-dev/quarto-actions/setup@v2`
(Quarto 1.11.9) → `quarto render docs` (ejecuta antes `assets/scripts/sync-diagrams.ts`, que copia
las fuentes BPMN/DSL/PUML) → `actions/configure-pages@v5` → `actions/upload-pages-artifact@v3`
con `docs/_site` → `actions/deploy-pages@v4` en el entorno `github-pages`.

Permisos: el workflow solo tiene `contents: read`; el job de despliegue añade `pages: write` e
`id-token: write`, los mínimos exigidos por `deploy-pages`.

## Publicar los cambios

1. Editar las fuentes en `DOCUMENTACION/` o `docs/` e integrarlas en `main` del proyecto.
2. Esperar la publicación diaria, o publicarla de inmediato:

   ```bash
   gh workflow run publicar.yml -R BrTrl3/sitra-cge-docs
   ```

   También desde *Actions → Publicar documentación → Run workflow* en `BrTrl3/sitra-cge-docs`.
   El campo *ref* permite publicar otra rama del proyecto, por ejemplo `develop`.
3. Comprobar en *Actions* que ambos jobs terminan en verde y abrir https://brtrl3.github.io/sitra-cge-docs/.

## Construcción local

```bash
# Requiere Quarto ≥ 1.4 (https://quarto.org/docs/get-started/)
quarto render docs        # genera docs/_site/
quarto preview docs       # vista previa con recarga automática
```

## Mantenimiento del portal

| Tarea | Cómo |
|---|---|
| Corregir o ampliar un capítulo | Editar **solo** el archivo fuente en `DOCUMENTACION/NN_*/…md`; la página `.qmd` lo incluye |
| Añadir una página | Crear el `.md` en `DOCUMENTACION/`, una página `docs/<capítulo>/<nombre>.qmd` con `{{< include … >}}` y registrarla en `website.sidebar` de `_quarto.yml` |
| Editar un diagrama BPMN | Abrir `DOCUMENTACION/02_PROCESOS/DIAGRAMAS/*.bpmn` en bpmn.io o Camunda Modeler; el portal lo muestra tal cual |
| Editar C4 / UML | `DOCUMENTACION/03_ARQUITECTURA/DIAGRAMAS/workspace.dsl` y `*.puml`; actualizar también la vista Mermaid del capítulo |
| Añadir una referencia | `DOCUMENTACION/10_REFERENCIAS/references.bib` y citar con `[@clave]` |
| Republicar | Hacer *merge* a `main` y ejecutar `gh workflow run publicar.yml -R BrTrl3/sitra-cge-docs` |
| Cambiar la versión de Quarto | Parámetro `version` del paso *Instalar Quarto*, en los dos workflows |

Los `.md` históricos de `docs/` (ADR, manuales) no forman parte del render (lista `project.render`) y siguen disponibles en el servidor Quart (`python docs_server/app.py`).
