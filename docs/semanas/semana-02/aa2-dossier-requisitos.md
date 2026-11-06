# AA 2: dossier de requisitos y matriz de trazabilidad

La AA 2 es individual. Este dossier es la base común del proyecto: cada estudiante debe
revisarlo, ajustarlo y dejar constancia de lo que corrigió en
[evidencia-individual.md](evidencia-individual.md).

## Actividades

### 1. Fundamentos de HTTP en RFC 9110

| Concepto | Sección | Decisión del proyecto que justifica |
|---|---|---|
| Semántica de métodos | 9.3 | GET para consultas; POST para crear; DELETE no se usa porque nada se elimina |
| GET | 9.3.1 | La matriz CSV es de solo lectura y usa GET |
| POST | 9.3.3 | Un dictamen es un recurso nuevo |
| PUT | 9.3.4 | Reemplazo de preferencias y configuración |
| Representación y contenido | 8.3 | `Content-Type` JSON, PDF o CSV según la operación |
| Códigos 2xx | 15.3 | 201 al crear un recurso |
| Códigos 4xx | 15.5 | Distinción entre 400, 401, 403, 404, 405 y 409 |
| 500 | 15.6.1 | Mensaje genérico sin detalles internos |
| Location | 10.2.2 | En 201 identifica el recurso creado |
| Allow | 10.2.1 | Obligatorio en la respuesta 405 |
| WWW-Authenticate | 11.6.1 | Indica cómo autenticarse en un 401 |
| Authorization | 11.6.2 | Transporta el JWT Bearer |
| ETag | 8.8.3 | Se evaluó; no se implementó en este incremento |

PATCH no está en RFC 9110: se define en RFC 5789. Se usa para cambios parciales, como
reabrir una recomendación o anular una evidencia.

### 2. Fuentes del dominio

Ver la sección [4. Fuentes consultadas](#4-fuentes-consultadas).

### 3. Depuración de historias de usuario

| Historia | Actor real | Necesidad, no solución | Beneficio | Coherente con el alcance | Con criterios | Ajuste |
|---|---|---|---|---|---|---|
| HU-1 | Sí | Sí | Sí | Sí | Sí | Sin cambios |
| HU-2 | Sí | Sí | Sí | Sí | Sí | Estados actualizados; admite varios hitos |
| HU-3 | Sí | Sí | Sí | Sí | Sí | Rechazo con observaciones obligatorias y reapertura |
| HU-4 | Sí | Sí | Sí | Sí | Sí | Vencimiento como indicador y entrega a tiempo |
| HU-5 | Sí | Sí | Sí | Sí | Sí | Sin cambios |
| HU-6 | Sí | Sí | Sí | Parcial | Sí | Su escenario 2 depende de RF-003, sin implementar |

### 4. Depuración de requisitos

| Hallazgo | Requisitos | Acción |
|---|---|---|
| Contradicción con el flujo acordado | RF-007, RF-009, RF-010, RF-012 | Corregidos |
| Capacidad sin requisito | Reapertura y archivos protegidos | Agregados RF-023 y RF-024 |
| Atributos sin requisito | Interoperabilidad, usabilidad, accesibilidad, mantenibilidad | Agregados RNF-010 a RNF-013 |
| No verificable | RNF-005, RNF-006 ("carga institucional definida") | Pendiente: cuantificar con la UAI |
| Sin fuente precisa | RF-014 (columnas de la matriz) | Pendiente: validar con el acuerdo y la UAI |

### 5. y 6. Vínculo de actores y criterios, y matriz

Ver la sección [9. Matriz de trazabilidad](#9-matriz-de-trazabilidad).

### 7. Dossier

Las secciones siguientes contienen los 10 puntos pedidos.

---

## 1. Identificación del proyecto

- **Nombre:** SITRA-CGE UNL, Sistema de Trazabilidad y Seguimiento de Recomendaciones.
- **Proyecto del banco:** 4, Seguimiento de recomendaciones CGE.
- **Asignatura:** Desarrollo Basado en Plataformas, Quinto Ciclo, UNL.
- **Repositorio:** <https://github.com/RCL05/seguimiento_de_recomendaciones_CGE>

## 2. Síntesis del problema

Las recomendaciones de la CGE a la UNL son de cumplimiento obligatorio, pero su
seguimiento es manual y disperso. Esto dificulta saber qué está pendiente, quién
responde, qué evidencia existe y si la UAI la aprobó, y expone a la institución a dar por
cumplida una recomendación que normativamente no lo está.

## 3. Actores principales

| Actor | Tipo | Necesidad | Interacción con el sistema |
|---|---|---|---|
| UAI | Usuario principal | Registrar y validar el cumplimiento | Registra informes y recomendaciones, emite dictámenes |
| Ejecutor | Usuario principal | Demostrar el avance de su unidad | Registra hitos y carga evidencias |
| Rectorado | Usuario secundario | Conocer el riesgo institucional | Consulta el tablero y exporta la matriz |
| Auditor CGE | Usuario secundario | Verificar de forma independiente | Consulta historial, integridad y matriz |
| DTI | Administrador | Mantener cuentas y configuración | Gestiona usuarios, unidades y notificaciones |
| CGE | Actor externo | Recibir el reporte de cumplimiento | Recibe la matriz; sin integración directa |
| SSO y correo institucional | Servicios relacionados | Autenticar y notificar | Validan la credencial y entregan alertas |

## 4. Fuentes consultadas

| Id | Fuente | Respalda | Nota |
|---|---|---|---|
| F1 | Banco de proyectos ACD1, ficha 4 | Problema y retos | Provista por el docente |
| F2 | [RFC 9110, HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html) | Métodos, códigos y cabeceras | Fuente primaria |
| F3 | [RFC 5789, PATCH Method for HTTP](https://www.rfc-editor.org/rfc/rfc5789.html) | Uso de PATCH | Fuente primaria |
| F4 | Ley Orgánica de la Contraloría General del Estado, art. 92 | Obligatoriedad y seguimiento de las recomendaciones | Consultada mediante citas en informes públicos. **Falta verificar el texto oficial vigente** |
| F5 | Acuerdo No. 010-CG-2022 de la CGE (R. O., Segundo Suplemento 123, 9 de agosto de 2022) | Seguimiento y medios de verificación | Consultado mediante citas. **Falta obtener el texto oficial** |
| F6 | [Informe de seguimiento de recomendaciones, Ministerio del Trabajo (2024)](https://www.trabajo.gob.ec/wp-content/uploads/2025/05/Informe-Seguimiento-Contraloria-Planta-Central-2024.pdf) | Ejemplo de cómo una entidad reporta el cumplimiento | Ejemplo público |
| F7 | [OWASP API1:2023, Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/) | RF-019 | Estándar de seguridad |
| F8 | [`docs/problem-definition.md`](../../problem-definition.md) y [`.spec/clarify.md`](../../../.spec/clarify.md) | Problema, actores y clarificaciones | Producto del equipo |
| F9 | Decisión del equipo (2026-11-05) | RF-012 y catálogo de estados | Pendiente de validar con el docente |

## 5. Historias de usuario depuradas

| Id | Historia |
|---|---|
| HU-1 | Como UAI, quiero registrar informes y asignar cada recomendación a una unidad con un plazo legal, para iniciar un seguimiento formal y trazable. |
| HU-2 | Como responsable de una unidad, quiero formular hitos y cargar medios de verificación, para demostrar el avance de las acciones asignadas. |
| HU-3 | Como UAI, quiero revisar evidencias y emitir un dictamen, para que solo las recomendaciones que cumplen las condiciones pasen a Cumplida. |
| HU-4 | Como máxima autoridad, quiero consultar un tablero con el riesgo institucional y las unidades en mora, para tomar decisiones oportunas. |
| HU-5 | Como UAI o auditor de la CGE, quiero consultar el historial y exportar la matriz, para verificar el cumplimiento y entregar reportes formales. |
| HU-6 | Como administrador de la DTI, quiero gestionar cuentas, roles, dependencias y notificaciones, para mantener la plataforma alineada con la institución. |

## 6. Requisitos funcionales

La redacción completa está en
[`spec.md`](../../../specs/001-seguimiento-recomendaciones/spec.md). Su estado está en la
matriz de la sección 9.

## 7. Requisitos no funcionales

| Id | Atributo | Criterio verificable |
|---|---|---|
| RNF-001 | Integridad | Toda modificación de un PDF se detecta con SHA-256 |
| RNF-002 | Auditoría | Bitácora solo para roles autorizados y protegida |
| RNF-003 | Autorización | RBAC y control por objeto en el servidor |
| RNF-004 | Contrato | `errors=null` en éxito; `data=null` en error |
| RNF-005 | Rendimiento | 95 % del tablero en menos de 3 s |
| RNF-006 | Exportación | 95 % de la matriz en menos de 5 s |
| RNF-007 | Disponibilidad | Un fallo de correo no revierte el negocio |
| RNF-008 | Privacidad | Sin credenciales ni trazas en respuestas y registros |
| RNF-009 | Requisitos | Sintaxis EARS y escenario BDD por requisito |
| RNF-010 | Interoperabilidad | OpenAPI 3.0.3 válido y CSV UTF-8 |
| RNF-011 | Usabilidad | Menú por rol; SC-009 |
| RNF-012 | Accesibilidad | Etiquetas, teclado y estado no solo por color |
| RNF-013 | Mantenibilidad | Pruebas de dominio y API sin reglas de negocio |

## 8. Criterios de aceptación

Los escenarios Dado–Cuando–Entonces completos están en `spec.md`, en cada historia y en
Escenarios críticos BDD adicionales. La matriz indica el criterio de cada requisito.

## 9. Matriz de trazabilidad

**Estados:**

- **Implementado:** existe código y prueba automatizada.
- **Parcial:** existe código, pero falta una parte o su verificación.
- **Pendiente:** no está implementado.

Ningún requisito figura como "Validado" porque esa validación corresponde al docente y a la UAI.

| Id | Actor | Necesidad | Requisito | Criterio de aceptación | Fuente | Prueba o evidencia | Estado |
|---|---|---|---|---|---|---|---|
| RF-001 | Todos | Acceder con identidad institucional | Autenticar y emitir sesión con expiración | HU-6, esc. 1 | F8 | `test_sso_jwt.py` | Parcial: falta el SSO real de la DTI |
| RF-002 | DTI | Controlar permisos | Asignar y revocar roles | HU-6 | F8 | `test_admin_flow.py`, `test_endpoints_base.py` | Implementado |
| RF-003 | DTI | Adaptarse a cambios orgánicos | Reasignar una recomendación conservando el historial | HU-6, esc. 2 | F8 | Sin prueba | Pendiente |
| RF-004 | Sistema | Recibir avisos | Alertas internas y por correo | HU-6, esc. 3 | F8 | `test_settings_flow.py` | Parcial: sin prueba con el SMTP institucional |
| RF-005 | UAI | Formalizar el informe | Registrar número, fecha, período y documento | HU-1, esc. 1 | F1, F5 | `test_endpoints_base.py` | Implementado |
| RF-006 | UAI | Asignar responsable y plazo | Exigir plazo, prioridad y unidad | HU-1, esc. 2 y 3 | F1, F4 | `test_creation_rules.py`, `test_registration.py` | Implementado |
| RF-007 | Ejecutor | Planificar acciones | Plan con N hitos | HU-2, esc. 1; HU-4, esc. 5 | F1, F5, F9 | `test_vencimientos.py` | Implementado |
| RF-008 | Ejecutor | Demostrar avance | Validar PDF, 30 MB y SHA-256 | HU-2, esc. 2 y 3 | F1, F5 | `test_upload_flow.py`, `test_upload_rules.py` | Implementado |
| RF-009 | UAI | Controlar el ciclo de vida | Flujo de 5 estados | HU-3, esc. 3 | F1, F9 | `test_state_machine_spec.py` | Implementado |
| RF-010 | UAI | Devolver evidencia insuficiente | Observaciones y regreso a En Proceso | HU-3, esc. 2 y 4 | F1, F9 | `test_quickstart.py`, `test_endpoints_base.py` | Implementado |
| RF-011 | Ejecutor, UAI | Actuar antes del vencimiento | Alerta a 15 días o menos | HU-4, esc. 3 | F8 | Sin prueba real | Parcial: falta prueba del job |
| RF-012 | Rectorado, UAI | Conocer lo vencido | Indicador y aviso único | HU-4, esc. 2 y 4 | F4, F9 | `test_vencimientos.py` | Implementado |
| RF-013 | Rectorado | Decidir oportunamente | Semáforo, porcentaje y unidades en mora | HU-4, esc. 1 | F1 | `test_endpoints_base.py` | Implementado |
| RF-014 | UAI, auditor CGE | Reportar a la CGE | Matriz CSV UTF-8 | HU-5, esc. 3 | F5, F6 | `test_quickstart.py`, `test_vencimientos.py` | Parcial: columnas por validar |
| RF-015 | Clientes de la API | Respuestas predecibles | Envoltura universal | Contrato universal | F8 | `test_api_contract.py` | Implementado |
| RF-016 | Clientes de la API | Errores comprensibles | Catálogo de errores | Contrato universal | F2 | `test_foundation.py`, `test_http_semantics.py` | Implementado |
| RF-017 | UAI, auditor CGE | Saber quién hizo qué | Auditar operaciones mutativas | HU-5, esc. 1 | F1 | `test_audit_and_reports.py`, `test_quickstart.py` | Implementado |
| RF-018 | Auditor CGE | Verificar de forma independiente | Consulta de historial e integridad | HU-5, esc. 1 y 2 | F1 | `test_integrity_flow.py`, `test_endpoints_base.py` | Implementado |
| RF-019 | Ejecutor | Proteger datos de otras unidades | 404 y registro del intento | BDD escenario 2 | F7 | `test_evidence_object_authorization.py`, `test_quickstart.py` | Implementado |
| RF-020 | Todos | Evitar estados contradictorios | Operaciones atómicas | Casos límite | F8 | `test_recommendation_locking.py` | Implementado |
| RF-021 | Sistema | Evitar avisos duplicados | Tareas idempotentes | Casos límite | F8 | `test_vencimientos.py` | Implementado |
| RF-022 | Equipo | Contrato confiable | OpenAPI sincronizado | Prueba de contrato | F2 | `test_api_contract.py` | Implementado |
| RF-023 | UAI | Corregir un cierre ante hallazgos | Reapertura con motivo | HU-3, esc. 5 | F9 | `test_archivos_y_reapertura.py` | Implementado |
| RF-024 | UAI, ejecutor | Proteger documentos | Archivos solo autenticados | Requisito RF-024 | F7 | `test_archivos_y_reapertura.py` | Implementado |
| RNF-005 | Rectorado | Consultar con agilidad | Tablero en menos de 3 s | SC-005 | F8 | `test_report_performance.py` solo declara el objetivo | Parcial: sin medición |
| RNF-006 | UAI | Exportar con agilidad | Matriz en menos de 5 s | SC-006 | F8 | `test_report_performance.py` solo declara el objetivo | Parcial: sin medición |
| RNF-010 | Equipo, clientes | Integrarse con otros sistemas | OpenAPI y CSV | Prueba de contrato | F2 | `test_api_contract.py` | Implementado |
| RNF-012 | Todos | Usar el sistema sin barreras | Etiquetas y teclado | Requisito RNF-012 | F8 | Revisión manual | Parcial: sin auditoría de accesibilidad |

## 10. Observaciones y decisiones pendientes

**Decisiones por validar con el docente:**

- Vencimiento como indicador y no como estado.
- Catálogo reducido de 5 estados.
- Reapertura de recomendaciones cumplidas por la UAI.

**Preguntas abiertas:**

- ¿La CGE admite prórrogas formales? ¿Quién las aprueba?
- ¿Los estados y las columnas de la matriz coinciden con el Acuerdo No. 010-CG-2022?
- ¿Cuál es la carga institucional para medir RNF-005 y RNF-006?
- ¿Qué mecanismo SSO proporcionará la DTI?

**Trabajo pendiente detectado:**

- RF-003: reasignación de recomendaciones.
- RF-011: prueba real del job de alertas.
- RNF-005 y RNF-006: medición real de rendimiento.
- El 401 del login no envía `WWW-Authenticate`.
- Obtener el texto oficial de F4 y F5.
