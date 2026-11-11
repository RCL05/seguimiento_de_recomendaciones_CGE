## Criterios de éxito (SC) de la especificación

Estados: **Verificado** (prueba automatizada aprobada que lo demuestra) · **Parcial** · **No verificado**.

| SC | Criterio | Método de verificación | Evidencia | Estado |
|---|---|---|---|---|
| SC-001 | Toda recomendación nueva conserva responsable, plazo, estado inicial y vínculo con informe | Integración | `test_registro_asignacion_duplicados_y_estado_inicial` | Verificado |
| SC-002 | Toda transición a `CUMPLIDA` tiene revisión interna y evidencia validada | Unitaria + integración | `test_completion_requires_validated_evidence_and_internal_review`, `test_cumplida_requiere_revision_interna_y_evidencia_validada` | Verificado |
| SC-003 | Toda operación mutativa produce evento de auditoría con campos mínimos | Integración | `test_flujo_principal_aprobacion_y_cadena_de_auditoria`, `test_cambios_de_configuracion_y_preferencias_quedan_auditados` | Parcial — se verifica en los flujos principales, no exhaustivamente para cada endpoint mutativo |
| SC-004 | Todo acceso de un ejecutor a otra unidad se rechaza y registra | Seguridad | `test_bola_idor_entre_unidades_retorna_404_sin_revelar_existencia_y_audita`, `test_bola_entre_unidades_responde_404_y_audita_el_intento` | Verificado |
| SC-005 | 95 % del tablero < 3 s | Rendimiento | `test_objetivos_performance_definidos` (sin medición) | **No verificado** (H-19) |
| SC-006 | 95 % de la matriz < 5 s | Rendimiento | ídem | **No verificado** (H-19) |
| SC-007 | Toda evidencia modificada produce discrepancia de hash | Integración | `test_hash_original_coincide_y_evidencia_alterada_se_detecta`, `test_integridad_detecta_archivo_alterado` | Verificado |
| SC-008 | Todo vencimiento se marca y notifica sin duplicados | Integración | `test_job_registra_y_notifica_sin_cambiar_estado_y_es_idempotente`, `test_umbrales_alerta_15_dias_o_menos_e_idempotencia` | Verificado |
| SC-009 | ≥ 90 % de usuarios completa su tarea sin asistencia | Evaluación de aceptación con usuarios | — | **No verificado** (no hay registro de evaluación) |
| SC-010 | Trazabilidad requisito → prueba → documentación | Revisión documental | *Matriz de trazabilidad* de este portal | Parcial — RNF-005/006 sin prueba |

## Requisitos no funcionales

| RNF | Verificación | Estado |
|---|---|---|
| RNF-001 Integridad | `test_integrity_flow.py` | Verificado |
| RNF-002 Auditoría protegida | `test_audit_immutability.py`, `test_consulta_auditoria_solo_autorizados_y_sin_modificacion` | Verificado (nivel ORM) |
| RNF-003 Autorización en servidor | Pruebas de seguridad y API | Verificado |
| RNF-004 Invariantes del contrato | `test_response_envelope_preserves_success_error_invariants` | Verificado |
| RNF-005 / 006 Rendimiento | — | No verificado |
| RNF-007 Disponibilidad ante fallo de correo | `test_delivery_retries.py`, `test_smtp_fallido_no_revierte_transaccion_y_reintentos` | Verificado — no revierte y reintenta hasta 3 intentos |
| RNF-008 Privacidad | `test_secret_and_log_safety.py` | Verificado |
| RNF-009 EARS + BDD | Revisión de `spec.md` | Verificado (documental) |
| RNF-010 OpenAPI 3.0.3 + CSV | `test_api_contract.py`, `test_matriz_es_get_y_csv` | Verificado |
| RNF-011 Navegación por rol | `App.test.tsx` | Parcial (Vitest; E2E no ejecutado) |
| RNF-012 Accesibilidad | — | No verificado |
| RNF-013 Mantenibilidad | Existencia de pruebas por regla de dominio | Parcial |

## Verificación de esta documentación

| Elemento | Método | Resultado |
|---|---|---|
| Endpoints y roles | Lectura de vistas y casos de uso; contrato regenerado | Coinciden, salvo H-14 (documentado) |
| Modelo de datos | Lectura de modelos y migraciones | Coincide |
| Estados y transiciones | `ALLOWED_TRANSITIONS` | Coincide |
| Comandos de instalación y pruebas | Ejecución local (backend, frontend) | Correctos; Docker no ejecutado |
| Portal Quarto | `quarto render docs` | Ver *Informe final* |
