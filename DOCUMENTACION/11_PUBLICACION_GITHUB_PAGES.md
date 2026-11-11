## Datos de publicación

| Dato | Valor |
|---|---|
| Repositorio | `RCL05/seguimiento_de_recomendaciones_CGE` |
| Propietario | `RCL05` (cuenta con permisos de administración necesaria para activar Pages) |
| URL pública esperada | **https://rcl05.github.io/seguimiento_de_recomendaciones_CGE/** |
| Proyecto Quarto | `docs/` (`docs/_quarto.yml`) |
| Salida | `docs/_site/` (no versionada) |
| Workflow | `.github/workflows/publish-quarto.yml` |
| Fuente de Pages | **GitHub Actions** (no "Deploy from a branch") |

Las rutas del sitio son relativas y `site-url` está fijado en `_quarto.yml`, por lo que funciona bajo el subdirectorio `/seguimiento_de_recomendaciones_CGE/`.

## Cómo funciona el workflow

| Evento | Qué hace |
|---|---|
| `push` a `main` que toque `docs/**`, `DOCUMENTACION/**` o el workflow | Construye y **publica** |
| `pull_request` con esos cambios | Solo **construye** (verifica que compila); no publica |
| `workflow_dispatch` | Construye y publica manualmente |

Pasos del job `build`: `actions/checkout@v4` → `quarto-dev/quarto-actions/setup@v2` (Quarto 1.11.9) → `quarto render docs` (ejecuta antes `assets/scripts/sync-diagrams.ts`, que copia las fuentes BPMN/DSL/PUML) → `actions/configure-pages@v5` → `actions/upload-pages-artifact@v3` con `docs/_site`.
Job `deploy`: `actions/deploy-pages@v4` en el entorno `github-pages`.

Permisos: el workflow solo tiene `contents: read`; el job de despliegue añade `pages: write` e `id-token: write`, los mínimos exigidos por `deploy-pages`. El grupo de concurrencia `pages` evita publicaciones simultáneas.

## Guía para el propietario del repositorio

1. **Integrar los cambios en `main`.** El entorno `github-pages` solo permite desplegar desde la rama por defecto. Abra un pull request de `feature/sdd-spec-kit-structure` hacia `develop`/`main` según GitFlow (ADR-0009). El PR ejecutará la construcción de prueba.
2. **Ingresar a GitHub** con la cuenta `RCL05` (o una con rol *Admin* en el repositorio).
3. **Abrir el repositorio** `https://github.com/RCL05/seguimiento_de_recomendaciones_CGE`.
4. **Entrar a *Settings*** (pestaña superior derecha del repositorio).
5. **Abrir *Pages*** en el menú lateral, sección *Code and automation*.
6. **Configurar la fuente**: en *Build and deployment → Source* elegir **GitHub Actions**.
7. **Revisar permisos**: en *Settings → Actions → General* confirmar que las Actions están permitidas. En *Settings → Environments → github-pages* comprobar que la regla de ramas admite `main`. No es necesario cambiar *Workflow permissions*: el workflow declara sus propios permisos.
8. **Ejecutar el workflow**: hacer *merge* a `main` (se dispara solo) o ir a *Actions → "Publicar documentación (Quarto → GitHub Pages)" → Run workflow*.
9. **Comprobar la publicación**: en *Actions* ambos jobs deben terminar en verde; el job *Publicar en GitHub Pages* muestra la URL.
10. **Obtener el enlace público**: en *Settings → Pages* aparece "Your site is live at https://rcl05.github.io/seguimiento_de_recomendaciones_CGE/". Opcional: añadirlo en *About → Website* del repositorio.

Si el repositorio es privado, GitHub Pages requiere un plan que lo permita (GitHub Pro, Team o Enterprise); en repositorios públicos es gratuito.

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
| Republicar | Hacer *merge* a `main`; o *Run workflow* |
| Cambiar la versión de Quarto | Parámetro `version` del paso *Instalar Quarto* |

Los `.md` históricos de `docs/` (ADR, manuales) no forman parte del render (lista `project.render`) y siguen disponibles en el servidor Quart (`python docs_server/app.py`).
