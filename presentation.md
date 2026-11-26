# SITRA-CGE UNL
## Seguimiento institucional con trazabilidad y control de cumplimiento

**Auditoría ejecutiva y técnica del backend | Unidad 1 / MVP**

---

## 1. Problema: obligación legal, operación universitaria

- Las recomendaciones de la Contraloría General del Estado tienen plazos y resultados que la UNL debe poder demostrar; el flujo operativo necesita responsables, planes y correcciones.
- El proceso manual dispersa informes, responsables, evidencias y decisiones UAI: aumenta el riesgo de omisiones, versiones incongruentes y cumplimiento declarado sin sustento verificable.
- La arquitectura conserva el plazo legal y el historial como hechos; permite gestionar avance, rechazo y reapertura sin reescribir el expediente.

| Presión normativa | Necesidad operativa | Respuesta de diseño |
|---|---|---|
| Plazo y dictamen deben ser defendibles | Dar seguimiento a planes y correcciones | Flujo explícito, con vencimiento como indicador, no estado |
| Evidencia debe poder verificarse | Cargar y revisar documentos | PDF con SHA-256, revisión y conservación de versiones |

---

## 2. Alcance: MVP verificable y evolución

| Unidad 1 / backend implementado | Visión posterior o condicionada |
|---|---|
| Registro de informes y recomendaciones; asignación; planes de acción; carga y dictamen de evidencias; estados; auditoría | Integración real con SSO institucional, operación productiva, evolución de estructura orgánica y capacidades móviles |
| API, roles, control por unidad, notificaciones, tablero y exportación están presentes en el código/contrato | Validación normativa pendiente de estados y matriz; firma electrónica/sello de tiempo no incluidos |

- La especificación funcional abarca más que el MVP inicial descrito en la hoja de ruta; funcionalidades auxiliares ya aparecen implementadas. La presencia de código no equivale a validación institucional ni preparación productiva.
- SSO está simulado en el adaptador; no se debe presentar como integración OIDC/LDAP de producción. La reasignación por cambio orgánico sigue pendiente.
- Fuera de alcance declarado: sincronización automática con CGE, gestión judicial/penal y aplicación móvil nativa.

---

## 3. Actores y niveles de confianza

| Actor | Confianza mínima | Puede hacer | Restricción de seguridad |
|---|---|---|---|
| UAI | Identidad autenticada + rol institucional | Registrar, dictaminar, reabrir y auditar | No omitir evidencia/revisión exigida para cumplimiento |
| Ejecutor DEP-A | JWT válido + unidad vinculada | Planificar y cargar evidencia de su unidad | Acceso a otra unidad se oculta con 404 y queda auditado |
| DTI | Rol administrativo | Gestionar usuarios, roles, configuración y operación | Privilegios administrativos separados del dictamen de negocio |
| Rectorado | Rol de consulta ejecutiva | Consultar riesgo, mora y tablero | Lectura; no altera el expediente operativo |

- El código aplica RBAC y comprobación de unidad en casos de uso; no existe una clase literal llamada `IsEjecutorOwner`. `CGE_AUDITOR` aparece en especificación y contrato como actor de solo lectura.
- Las identidades simuladas y cabeceras de contexto documentadas deben sustituirse/validarse con el proveedor institucional antes del despliegue.

---

## 4. Requisitos que moldean la arquitectura

| Requisito crítico | Decisión técnica | Valor institucional |
|---|---|---|
| Flujo y evidencia no se alteran silenciosamente | Máquina de estados; rechazos y reaperturas conservan rastro | El estado “Cumplida” requiere revisión y evidencia válidas |
| Integridad documental | PDF hasta 30 MB; cabecera `%PDF-`; SHA-256 recalculado/registrado | Detecta sustitución o corrupción; hash no prueba autoría legal |
| Separación de funciones y privacidad | RBAC + autorización por objeto/unidad; 404 ante recurso ajeno | Reduce BOLA/IDOR y exposición de información institucional |
| Reglas comprobables y fallos seguros | Dominio separado; pytest; errores tipados y 500 sanitizados | Cambios de reglas más fáciles de verificar y diagnosticar |

---

## 5. Arquitectura C4 y patrones

| Nivel C4 | Vista del sistema |
|---|---|
| C1 · Contexto | UAI, ejecutores, Rectorado, DTI y auditor CGE usan SITRA; integraciones previstas: SSO, SMTP y almacenamiento |
| C2 · Contenedores | Frontend React/TypeScript; backend Django/DRF; SQLite en desarrollo o PostgreSQL previsto; almacenamiento de archivos y scheduler |
| C3 · Componentes | `core` transversal y módulos de usuarios, informes, recomendaciones/evidencias, notificaciones y reportes |

- **Cuatro capas:** presentación/API, aplicación (casos de uso), dominio (reglas) e infraestructura (Django/DB/servicios). La decisión aísla reglas como transiciones y vencimientos del transporte HTTP.
- **Monolito modular:** transacciones y auditoría consistentes en un despliegue; menor costo operativo para el alcance y equipo actuales. Los límites por módulo dejan abierta una extracción futura si métricas y carga la justifican.
- **Matiz de implementación:** Django/DRF está en modelos y casos de uso; el dominio puro es desacoplado, pero el backend completo no es independiente del framework. La separación es un límite arquitectónico, no ausencia total de dependencias.

---

## 6. Contrato OpenAPI y semántica REST

- La envoltura `success`, `message`, `data`, `errors`, `meta` estandariza consumo entre clientes y correlación mediante `request_id` y timestamp; los errores usan códigos estables y no filtran trazas.
- Las transiciones de negocio inválidas producen `409 Conflict`: se distinguen de datos mal formados (`400`) y permisos/autenticación (`403/401`). Recurso ajeno para ejecutor se responde como `404`.
- No hay operación `DELETE` en OpenAPI; la eliminación de evidencia es lógica y auditable. Los recursos se corrigen mediante operaciones de negocio explícitas.

| Hallazgo de contrato | Estado real observado |
|---|---|
| `PATCH` para cambios parciales | Presente para recomendación, evidencia y usuario |
| `PUT` | También aparece para configuración y preferencias de notificación; por tanto, el contrato no usa PATCH exclusivamente |
| `DELETE` | Ausente en el OpenAPI inspeccionado |

**Decisión para cerrar:** unificar `PUT`/`PATCH` conforme a la semántica elegida y regenerar/validar el contrato. No describir “PATCH exclusivo” como realidad actual.

---

## 7. Seguridad: defensa en profundidad

| Riesgo (STRIDE) | Controles observados |
|---|---|
| Suplantación / elevación | Autenticación Bearer JWT y RBAC; SSO institucional de producción aún pendiente |
| Manipulación / repudio | Transacciones, auditoría append-only en modelo y SHA-256 de evidencia |
| Divulgación / acceso indebido | Autorización por rol y unidad; 404 para ocultar objetos ajenos; control antes de descargar |
| Denegación de servicio | Límite de 30 MB y validación binaria básica del PDF |

- La carga calcula hash y guarda evidencia, transición y auditoría dentro de `transaction.atomic()` con bloqueo del registro. Al fallar la operación intenta retirar el archivo almacenado.
- La firma `%PDF-` valida estructura mínima, no malware ni autenticidad del documento. Aunque la documentación menciona análisis antimalware, no se encontró evidencia de escáner integrado en el flujo auditado.
- `AuditLog` bloquea update/delete en modelo y queryset; la prohibición a nivel de permisos SQL/DB es una decisión documentada, no demostrada por el modelo.

---

## 8. Pruebas y calidad: Spec-Driven Development

- `spec.md` aporta reglas, escenarios y requisitos; `tasks.md`, OpenAPI, casos de uso y pruebas conectan especificación con ejecución.
- Las pruebas unitarias de dominio con pytest ejercitan estados y vencimientos sin cliente HTTP ni base de datos. El repositorio también contiene suites API, integración, seguridad y concurrencia: la estrategia no se limita a pruebas en memoria.
- La pirámide es adecuada al riesgo: muchas reglas puras; integración para persistencia/transacciones y archivos; API/contrato para códigos, envolturas y métodos; seguridad/concurrencia para controles críticos.
- OpenAPI se contrasta mediante pruebas de contrato; el propio contrato debe mantenerse sincronizado con rutas y comportamiento (incluido el hallazgo `PUT`).

---

## 9. Entorno, secretos y exposición de errores

- Configuración mediante variables de entorno y `.env` local ignorado por Git; `.env.example` sirve de plantilla. Producción exige `DEBUG=false`, clave secreta y hosts explícitos.
- El manejador global devuelve mensaje genérico `INTERNAL_ERROR` ante fallos no controlados y registra el detalle con `request_id`; evita devolver stack traces al cliente.
- CORS usa orígenes explícitos por entorno: Vite local en desarrollo y ninguno por defecto fuera de DEBUG; cubre rutas API/health y limita headers expuestos.
- La configuración acepta SQLite por defecto y PostgreSQL mediante variables; secretos de SSO/SMTP/S3 están parametrizados. El despliegue productivo requiere proveedor SSO real, secretos gestionados y endurecimiento operativo.

---

## 10. Auditoría y evolución: evidencia de decisiones

- `AuditLog` es **append-only**: guarda actor, instante UTC, IP disponible, `request_id`, entidad, estados y resultado; el modelo prohíbe actualización y eliminación. La evidencia anulada conserva el registro.
- ADRs principales: **0001** monolito modular y capas; **0002** JWT/RBAC; **0003** base relacional; **0004** concurrencia; **0005/0011** almacenamiento y supuestos PDF; **0006** auditoría inmutable; **0007** envoltura universal; **0008/0009** entorno y flujo CI.
- Lección de ingeniería: separar obligaciones normativas de decisiones técnicas reversibles, registrar supuestos y revelar pendientes. SHA-256 da integridad del contenido frente al hash registrado, no firma ni validez probatoria por sí sola.

### Lectura ejecutiva

SITRA ya materializa un núcleo de seguimiento auditable: estados gobernados, evidencias verificables, aislamiento por unidad y decisiones registradas. La madurez siguiente depende de validar reglas con UAI, cerrar discrepancias OpenAPI-código, integrar SSO real y demostrar controles de producción sobre almacenamiento, secretos y base de datos.
