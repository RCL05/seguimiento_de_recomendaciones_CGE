> Registro permanente del trabajo de análisis, documentación y publicación. Si se pierde el contexto, este archivo indica el estado y la próxima tarea.

## Objetivo

Analizar SITRA-CGE UNL y producir una documentación técnica, arquitectónica y funcional verificable, publicada como portal Quarto (`docs/`) y preparada para GitHub Pages, sin alterar el funcionamiento del sistema.

## Alcance

- **Incluye**: auditoría técnica y documental; documentación general, procesos, arquitectura (C4, UML, ADR), implementación, API, seguridad, calidad, despliegue, operación y referencias; portal Quarto; workflow de publicación; informe de cierre.
- **No incluye**: cambios en código fuente, lógica de negocio, migraciones, API ni configuración de producción. Los defectos encontrados se registran como hallazgos con recomendación.
- **Archivos del proyecto modificados**: `.gitignore` (salidas de Quarto: `docs/_site/`, `docs/.quarto/`, `docs/assets/diagrams/src/`) y `.claude/launch.json` (configuración `docs-portal` que sirve `docs/_site` en el puerto 4321). Archivos nuevos: `DOCUMENTACION/**`, `docs/_quarto.yml`, `docs/index.qmd`, `docs/**/*.qmd`, `docs/assets/**`, `docs/.gitignore` (generado por Quarto), `.github/workflows/publish-quarto.yml`. Ningún archivo de `backend/`, `frontend/` ni `specs/` fue modificado.

## Inventarios

- Técnico: `DOCUMENTACION/00_AUDITORIA/INVENTARIO_TECNICO.md`
- Documental: `DOCUMENTACION/00_AUDITORIA/AUDITORIA_DOCUMENTAL.md`
- Matriz de cumplimiento inicial: `DOCUMENTACION/00_AUDITORIA/MATRIZ_CUMPLIMIENTO.md`

## Decisión de organización (evita duplicación)

Cada capítulo tiene **una sola fuente**: el archivo Markdown en `DOCUMENTACION/NN_*/`. Las páginas del portal (`docs/NN-*/…qmd`) contienen únicamente metadatos y un `{{< include >}}` de esa fuente. Los diagramas tienen su fuente editable (`.bpmn`, `.dsl`, `.puml`) en `DIAGRAMAS/` y su vista renderizable en Mermaid dentro del capítulo.

## Lista de tareas

| Tarea | Descripción | Dependencias | Estado | Entregables |
|---|---|---|---|---|
| TASK-001 | Inventario técnico | — | COMPLETADA | `00_AUDITORIA/INVENTARIO_TECNICO.md` |
| TASK-002 | Auditoría documental | TASK-001 | COMPLETADA | `00_AUDITORIA/AUDITORIA_DOCUMENTAL.md` |
| TASK-003 | Matriz de cumplimiento | TASK-002 | COMPLETADA | `00_AUDITORIA/MATRIZ_CUMPLIMIENTO.md` |
| TASK-004 | Control maestro | TASK-001..003 | COMPLETADA | este archivo |
| TASK-010..013 | Documentación general y trazabilidad | Fase 0 | COMPLETADA | `01_GENERAL/*` |
| TASK-020..022 | Procesos y BPMN | TASK-012 | COMPLETADA | `02_PROCESOS/*` |
| TASK-030..032 | Arquitectura, C4, UML, ADR | Fase 0 | COMPLETADA | `03_ARQUITECTURA/*` |
| TASK-040..043 | Implementación y modelo de datos | Fase 0 | COMPLETADA | `04_IMPLEMENTACION/*` |
| TASK-05x | API e integraciones | TASK-042 | COMPLETADA | `05_API/*` |
| TASK-06x | Seguridad | TASK-05x | COMPLETADA | `06_SEGURIDAD/*` |
| TASK-07x | Pruebas y calidad (ejecución real) | Fase 0 | COMPLETADA | `07_CALIDAD/*` |
| TASK-08x | Instalación y despliegue | Fase 0 | COMPLETADA | `08_DESPLIEGUE/*` |
| TASK-09x | Operación y mantenimiento | TASK-08x | COMPLETADA | `09_OPERACION/*` |
| TASK-10x | Referencias y declaración de IA | todas | COMPLETADA | `10_REFERENCIAS/*` |
| TASK-110..115 | Portal Quarto | Fases 1–10 | COMPLETADA | `docs/_quarto.yml`, `docs/**/*.qmd`, `docs/assets/` |
| TASK-120..122 | Workflow y guía GitHub Pages | TASK-110 | COMPLETADA | `.github/workflows/publish-quarto.yml`, `11_PUBLICACION_GITHUB_PAGES.md` |
| TASK-123 | Verificación local (`quarto render docs`) | TASK-110..122 | COMPLETADA | Resultado en `12_CIERRE/INFORME_FINAL.md` |
| TASK-123b | Verificación del despliegue real en GitHub Pages | merge a `main` + configuración de Pages por el propietario | BLOQUEADA | Requiere acción del propietario del repositorio (`RCL05`) |
| TASK-124 | Mantenimiento del portal | TASK-121 | COMPLETADA | `11_PUBLICACION_GITHUB_PAGES.md` §Mantenimiento |
| TASK-130..133 | Validación final e informe | todas | COMPLETADA | `12_CIERRE/INFORME_FINAL.md` |

## Hallazgos

Severidad: **A** alta (riesgo funcional o de seguridad), **M** media (documentación que induce a error o control incompleto), **B** baja (higiene).

| ID | Sev. | Hallazgo | Evidencia | Recomendación |
|---|---|---|---|---|
| H-01 | M | `docs/architecture/sitra-cge.md` y `docs/operations/configuration.md` describen autenticación por cabeceras `X-User-ID`/`X-Role`/`X-Unit-ID`; el código usa `Authorization: Bearer <JWT>` | `backend/core/auth/authentication.py` | Actualizar ambos documentos |
| H-02 | M | Se documenta bloqueo optimista con campo `version`; el modelo no tiene ese campo y se usa bloqueo pesimista `select_for_update` | `recomendaciones/models.py`, `issue_dictamen.py` | Corregir docs; ADR-0004 debe reflejar la variante implementada |
| H-03 | A | Se documenta "análisis antimalware" de PDF; no existe implementación | búsqueda `malware/clamav` sin resultados | Implementar escaneo (p. ej. ClamAV) o retirar la afirmación |
| H-04 | M | Variables documentadas sin efecto: `EVIDENCE_STORAGE_BACKEND`, `EVIDENCE_S3_*`, `SSO_ISSUER`, `SSO_REDIRECT_URI`, `APP_ENV`, `VITE_API_BASE` (esta última sí la usa el frontend). Solo existe almacenamiento local | `grep` en `backend/` | Marcar como reservadas o implementar el adaptador S3 |
| H-05 | A | Reintentos SMTP: se documentan "3 reintentos con espera exponencial"; el código marca `FALLIDA` y no vuelve a intentar (solo procesa `PENDIENTE`). `SmtpAdapter` solo se usa en pruebas | `notificaciones/application/service.py` | Implementar reintento acotado o corregir RNF-007 / docs |
| H-06 | M | `data-model.md` usa el catálogo de estados anterior | `specs/001-…/data-model.md` | Regenerar desde los modelos |
| H-07 | M | `tasks.md` no refleja el avance real (77 casillas sin marcar con archivos y pruebas presentes) | `specs/001-…/tasks.md` | Sincronizar casillas |
| H-08 | M | RF-003 (reasignar recomendación conservando historial) no implementado | `spec.md` "sin implementar"; sin caso de uso | Planificar en el siguiente incremento |
| H-09 | M | Columnas de la matriz CSV no validadas contra el Acuerdo 010-CG-2022 | `export_matriz.py`, preguntas pendientes en `spec.md` | Validar con la UAI |
| H-10 | A | `DJANGO_DEBUG` vale `true` por defecto y `ALLOWED_HOSTS` `*`; con `DEBUG=true` los tokens SSO de desarrollo quedan activos | `config/settings.py`, `sso_adapter.py` | Invertir el valor por defecto o exigir variable en despliegue |
| H-11 | B | Comentario residual en `settings.py`: "#prueba de conexion de comits en discord" | `config/settings.py` última línea | Eliminar |
| H-12 | M | No hay configuración `LOGGING`; los `logger.info` dependen del valor por defecto de Django | `config/settings.py` | Definir LOGGING estructurado con `request_id` |
| H-13 | B | La vista `/` (panel de demostración) consulta `/api/v1/recomendaciones` sin token (responde 401) y muestra un flujo de estados antiguo | `core/web/views.py` | Retirar o actualizar |
| H-14 | M | `GET /api/v1/dashboard/kpis` no restringe rol: cualquier usuario autenticado (incluido EJECUTOR) obtiene totales institucionales; además omite `REABIERTA` del desglose | `reportes/application/get_kpis.py` | Confirmar si es intencional; documentado como comportamiento actual |
| H-15 | B | Contrato duplicado en `backend/contracts/` y `specs/…/contracts/` (hoy idénticos) | `diff` sin diferencias | Mantener una copia o automatizar la sincronización |
| H-16 | B | La sección "Deuda técnica" de `sitra-cge.md` cita `core/api/views.py`, que ya no existe | árbol de `core/api` | Actualizar |
| H-17 | B | Dos fuentes SDD (`.spec/` y `specs/001-…`) con numeraciones distintas | carpetas citadas | Declarar `.spec/` como histórico |
| H-18 | M | La prueba E2E de Playwright no se ejecuta en CI ni se ejecutó en esta auditoría | `ci.yml`, `frontend/tests/e2e` | Añadir job E2E |
| H-19 | A | La "prueba de rendimiento" solo compara constantes; RNF-005/RNF-006 no tienen medición | `tests/integration/reportes/test_report_performance.py` | Implementar prueba de carga con el volumen de referencia del plan |
| H-20 | B | `npm run build` modifica `frontend/tsconfig.tsbuildinfo`, que está versionado | `git status` tras build | Añadirlo a `.gitignore` |
| H-21 | B | Enlaces a ADR con nombres inexistentes en `sitra-cge.md` | §6 de ese documento | Corregir rutas |
| H-22 | M | El `Dockerfile` ejecuta `runserver` (servidor de desarrollo); no hay configuración de producción (Gunicorn/Uvicorn, proxy TLS) | `backend/Dockerfile` | Crear perfil de producción |
| H-23 | B | ADR-0003 sigue "Propuesto" aunque SQLite/PostgreSQL están implementados | `docs/adr/ADR-0003…` | Actualizar estado |
| H-24 | M | `plazo_legal_dias` y `fecha_vencimiento_legal` se reciben por separado y no se valida su coherencia; un informe o unidad inexistente responde 409 `BUSINESS_RULE_VIOLATION` en lugar de 400/404 | `create_recomendacion.py` | Calcular la fecha en servidor o validar la coherencia |
| H-25 | B | `evidencias/application/reject_evidence.py` (`RejectEvidence`) no lo invoca ninguna vista: el rechazo lo resuelve `IssueDictamen` con `approved=false` | `grep RejectEvidence` solo encuentra su definición | Eliminar o integrar para evitar dos implementaciones de la misma regla |

> **Actualización 2026-11-11.** Quedaron resueltos en el código H-01 (JWT en la documentación), H-05 (reintento SMTP acotado a 3 intentos), H-08 (reasignación RF-003 con historial), H-10 (`DEBUG=false` y hosts locales por defecto), H-11 (comentario residual eliminado), H-12 (`LOGGING` a consola con nivel configurable), H-19 (rendimiento medido con pruebas de tiempo y ausencia de N+1) y la parte de Gunicorn de H-22. Además: H-14 quedó parcialmente atenuado (los KPIs del EJECUTOR se limitan a su unidad), H-24 quedó parcialmente resuelto (informe o unidad inexistente responde 400 con `errors.fields`), el login SSO limita intentos y audita los fallidos, y se corrigieron los hallazgos de seguridad de la Semana 4 (SEC-01…SEC-04: anulación de evidencias y dictámenes). Los ajustes de contrato de la ACD 3 quedaron aplicados y verificados (`/sesiones`, `hitos` con `Location`, dictamen consultable, evidencia sin plan 409, `evaluaciones-plazos` retirado de la API). Sigue pendiente el proxy TLS y la automatización completa de despliegue.

## Limitaciones

- Docker no está instalado en el equipo auditado: `docker-compose.yml` y `Dockerfile` se documentaron por lectura, sin ejecución.
- No se ejecutó Playwright (requiere navegadores instalados); no se generaron capturas de pantalla.
- No hay acceso administrativo al repositorio `RCL05/…`: la publicación real en GitHub Pages no pudo verificarse.
- Las fuentes Structurizr DSL, PlantUML y BPMN no se compilaron a imagen (requieren herramientas externas); el portal muestra vistas Mermaid equivalentes mantenidas a mano.
- No se midió cobertura de código (no hay `pytest-cov` ni configuración de cobertura en el proyecto).

## Estado

- **Última tarea completada**: TASK-133 (informe final).
- **Tarea bloqueada**: TASK-123b (despliegue real en GitHub Pages).
- **Próxima tarea**: el propietario del repositorio integra la rama en `main`, activa Pages con fuente "GitHub Actions" y ejecuta el workflow (ver `11_PUBLICACION_GITHUB_PAGES.md`).
