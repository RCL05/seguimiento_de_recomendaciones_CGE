## Enfoque

La estrategia observada en el repositorio combina **pruebas guiadas por la especificación** (los nombres de las pruebas citan RF, HU y escenarios BDD) con una pirámide clásica: muchas pruebas unitarias del dominio, pruebas de integración de casos de uso con base de datos real (SQLite de prueba) y pruebas HTTP de la API, más pruebas específicas de contrato, seguridad y concurrencia.

```{mermaid}
flowchart TB
  e2e["E2E Playwright · 1 escenario<br/>(no se ejecuta en CI)"]
  fe["Componentes React · Vitest · 12"]
  api["API HTTP · 38 · contrato · 5"]
  int["Integración · 38 · seguridad · 17 · concurrencia · 1"]
  unit["Unitarias de dominio y reglas · 39"]
  e2e --- fe --- api --- int --- unit
```

## Niveles

| Nivel | Herramienta | Ubicación | Propósito |
|---|---|---|---|
| Unitario | pytest | `backend/tests/unit/` | Máquina de estados, vencimiento, reglas de creación, PDF, JWT, configuración de notificaciones |
| Integración | pytest-django (BD de prueba) | `backend/tests/integration/` | Casos de uso completos con persistencia, auditoría y jobs |
| API / funcional | DRF `APIClient` | `backend/tests/api/` | Semántica HTTP: códigos, `Location`, `WWW-Authenticate`, 405 + `Allow`, CORS, JSON mal formado |
| Contrato | pytest + drf-spectacular | `backend/tests/contract/` | Contrato publicado = generado; rutas documentadas; seguridad declarada |
| Seguridad | pytest | `backend/tests/security/` | BOLA/IDOR, inmutabilidad de auditoría, archivos protegidos, redacción de secretos |
| Concurrencia | pytest | `backend/tests/concurrency/` | Bloqueo de la recomendación durante el dictamen |
| Componentes | Vitest + Testing Library + jsdom | `frontend/src/**/*.test.tsx` | Navegación por rol, carga de evidencia, revisión, administración |
| Extremo a extremo | Playwright (Chromium) | `frontend/tests/e2e/` | Recorrido de las vistas de cada rol con API simulada |
| Estático | ESLint, TypeScript (`tsc -b`) | `frontend/` | Calidad y tipos |

## Casos positivos y negativos

Las pruebas cubren deliberadamente ambos tipos. Ejemplos:

| Área | Positivo | Negativo |
|---|---|---|
| Estados | `test_allows_transitions_defined_by_spec` | `test_rejects_unlisted_transitions`, `test_illegal_jump_to_completed_is_conflict` |
| Evidencias | `test_carga_valida_invalida_y_transicion_a_revision` (parte válida) | misma prueba (parte inválida), `test_evidencia_tamano_mime_extension_hash_y_autorizacion_unidad` |
| Dictamen | `test_dictamen_aprobado_201_y_doble_dictamen_409` | `test_rechazo_sin_observaciones_responde_400` |
| Autorización | `test_rectorado_inicia_sesion_y_consulta_tablero` | `test_bola_idor_entre_unidades_retorna_404_sin_revelar_existencia_y_audita` |
| Auditoría | `test_flujo_principal_aprobacion_y_cadena_de_auditoria` | `test_no_permite_actualizar_por_queryset`, `test_no_permite_eliminar_por_queryset` |
| Plazos | `test_umbrales_alerta_15_dias_o_menos_e_idempotencia` | `test_entrega_a_tiempo_no_queda_vencida_y_la_uai_puede_dictaminar` |

## Integración continua

`.github/workflows/ci.yml` ejecuta en cada push a `main`, `develop`, `feature/**` y en cada pull request:

1. Backend (Python 3.12): `pip install -r requirements.txt pytest pytest-django` → `python manage.py check` → `python -m pytest -q`.
2. Frontend (Node 22): `npm ci` → `npm run lint` → `npm test` → `npm run build`.

## Limitaciones de la estrategia

- **Sin medición de cobertura**: no hay `pytest-cov` ni configuración de cobertura en Vitest. No se informa porcentaje.
- **Rendimiento sin medir**: `test_objetivos_performance_definidos` solo afirma constantes (H-19).
- **E2E fuera de CI** (H-18) y sin pruebas contra el backend real.
- **Concurrencia en SQLite**: SQLite no implementa bloqueo de fila; la prueba no demuestra el comportamiento en PostgreSQL.
- **Accesibilidad** (RNF-012) y **usabilidad** (SC-009) sin pruebas.
- **Docker** no se prueba en CI.
