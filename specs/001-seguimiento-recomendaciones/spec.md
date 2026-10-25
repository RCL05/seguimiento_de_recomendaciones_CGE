# Especificación de Funcionalidad: Seguimiento de Recomendaciones CGE

**Rama de funcionalidad**: `001-seguimiento-recomendaciones`

**Creado**: 2026-10-19

**Estado**: Borrador

**Entrada**: Descripción del usuario: Prompt funcional para especificar SITRA-CGE
UNL, sus actores, requisitos EARS, reglas de dominio, seguridad y escenarios BDD.

## Clarifications

### Session 2026-10-20

- Q: ¿En qué formato debe exportarse oficialmente la matriz institucional de cumplimiento para UAI y auditor CGE? → A: CSV UTF-8.
- Q: ¿Qué canales deben utilizarse para las alertas de vencimiento y mora en la primera versión? → A: Notificación dentro del sistema y correo electrónico institucional.
- Q: ¿Cuál debe ser el tamaño máximo permitido para cada evidencia PDF en la primera versión? → A: 30 MB.
- Q: ¿Qué zona horaria debe utilizarse para calcular vencimientos, alertas y fechas legales de las recomendaciones? → A: America/Guayaquil (UTC-5) para negocio y UTC para auditoría.
- Q: ¿Qué respuesta debe recibir un ejecutor cuando solicita una recomendación perteneciente a otra dependencia? → A: HTTP 404 sin revelar la existencia del recurso y con registro interno del intento.

## Escenarios de Usuario y Pruebas

### Historia de Usuario 1 - Registrar y asignar recomendaciones (Prioridad: P1)

Como integrante de la Unidad de Auditoría Interna (UAI), quiero registrar informes
de examen especial y asignar cada recomendación a una unidad responsable con un plazo
legal, para iniciar un seguimiento formal y trazable.

**Por qué esta prioridad**: Sin un registro oficial, responsable y plazo, no existe
una base confiable para controlar el cumplimiento institucional.

**Prueba independiente**: Registrar un informe, crear una recomendación, asignarla a
una unidad y consultar su estado inicial, plazo y responsable sin depender de otros
flujos.

**Escenarios de aceptación**:

1. **Dado** que la UAI dispone de un informe de examen especial, **cuando** registra
   su número, fecha de notificación, período auditado y documento oficial, **entonces**
   el sistema conserva el informe con un identificador único y una relación auditable.
2. **Dado** que existe un informe registrado, **cuando** la UAI crea una
   recomendación, **entonces** el sistema exige el plazo legal, prioridad y unidad
   ejecutora, y establece el estado `Pendiente`.
3. **Dado** que falta un plazo o una unidad responsable, **cuando** la UAI intenta
   guardar la recomendación, **entonces** el sistema rechaza la operación y comunica
   los campos inválidos sin crear un registro incompleto.

### Historia de Usuario 2 - Gestionar plan de acción y evidencias (Prioridad: P1)

Como responsable de ejecución de una unidad, quiero formular hitos y cargar medios
de verificación, para demostrar el avance de las acciones asignadas.

**Por qué esta prioridad**: La evidencia verificable y el plan de acción son la base
para que la UAI pueda dictaminar el cumplimiento.

**Prueba independiente**: Con una recomendación asignada, crear hitos válidos, cargar
un PDF y consultar su huella de integridad y estado de revisión.

**Escenarios de aceptación**:

1. **Dado** que una recomendación está en `En Planificación`, **cuando** el ejecutor
   registra uno o más hitos con fechas que no exceden el plazo legal, **entonces** el
   sistema guarda el plan y permite avanzar a `En Ejecución`.
2. **Dado** que una recomendación está asignada al ejecutor y en `En Ejecución`,
   **cuando** carga un PDF válido, **entonces** el sistema conserva el archivo,
   calcula su hash SHA-256, registra la operación y envía la recomendación a
   `En Revisión Interna`.
3. **Dado** que el ejecutor intenta cargar un archivo que no es PDF, supera el tamaño
   permitido o no coincide con su contenido declarado, **cuando** envía el archivo,
   **entonces** el sistema lo rechaza si supera 30 MB, y no cambia el estado ni crea evidencia válida.

### Historia de Usuario 3 - Revisar, aprobar o devolver evidencias (Prioridad: P1)

Como integrante de la UAI, quiero revisar evidencias y emitir un dictamen, para que
solo las recomendaciones que cumplen las condiciones pasen a `Cumplida`.

**Por qué esta prioridad**: La aprobación institucional es la salvaguarda contra
declarar cumplida una recomendación sin sustento suficiente.

**Prueba independiente**: Revisar una evidencia, aprobarla o rechazarla con
observaciones y comprobar la transición y la bitácora resultantes.

**Escenarios de aceptación**:

1. **Dado** que una recomendación está en `En Revisión Interna` y tiene un PDF válido,
   **cuando** la UAI aprueba la evidencia, **entonces** el sistema permite `Cumplida`
   solo si también se ha cumplido el historial de transición requerido.
2. **Dado** que la UAI considera insuficiente una evidencia, **cuando** la rechaza con
   observaciones, **entonces** el sistema cambia a `Rechazada/Corrección`, conserva
   el archivo y la revisión anterior, y notifica al ejecutor.
3. **Dado** que una recomendación está en `En Ejecución` con un PDF aún no evaluado,
   **cuando** cualquier usuario intenta cambiarla directamente a `Cumplida`,
   **entonces** el sistema mantiene el estado y devuelve HTTP 409.

### Historia de Usuario 4 - Supervisar riesgos y vencimientos (Prioridad: P2)

Como máxima autoridad, quiero consultar un tablero con el riesgo institucional y las
unidades en mora, para tomar decisiones oportunas.

**Por qué esta prioridad**: La supervisión ejecutiva permite escalar retrasos antes
de que afecten el cumplimiento institucional.

**Prueba independiente**: Crear recomendaciones con distintos plazos y estados y
verificar que el tablero consolida porcentajes, prioridades y unidades en mora según
los permisos del usuario.

**Escenarios de aceptación**:

1. **Dado** que existen recomendaciones con diferentes estados y plazos, **cuando**
   la máxima autoridad consulta el tablero, **entonces** observa el porcentaje global
   de cumplimiento, un semáforo de riesgo y las unidades en mora.
2. **Dado** que una recomendación llega a su vencimiento sin evidencia aprobada,
   **cuando** se ejecuta la evaluación de plazos, **entonces** el sistema la marca
   `En Mora` y notifica dentro del sistema y por correo electrónico a la unidad
   responsable, la UAI y la máxima autoridad.
3. **Dado** que faltan 15 días o menos y no existe evidencia presentada que satisfaga
   las condiciones configuradas, **cuando** se evalúan los plazos, **entonces** el
   sistema genera una alerta dentro del sistema y por correo electrónico sin
   confundir evidencia presentada con validada.

### Historia de Usuario 5 - Auditar y exportar el cumplimiento (Prioridad: P2)

Como UAI o auditor externo de la CGE, quiero consultar el historial y exportar la
matriz institucional, para verificar el cumplimiento y entregar reportes formales.

**Por qué esta prioridad**: La trazabilidad completa permite rendición de cuentas y
verificación independiente.

**Prueba independiente**: Consultar una recomendación, verificar eventos y hash de
evidencias y exportar la matriz con datos autorizados.

**Escenarios de aceptación**:

1. **Dado** que existen operaciones mutativas, **cuando** un usuario autorizado
   consulta el historial, **entonces** cada evento incluye actor, fecha UTC,
   solicitud, entidad, estados anterior y nuevo y resultado.
2. **Dado** que existe una evidencia almacenada, **cuando** se verifica su integridad,
   **entonces** el sistema informa si el contenido coincide con el hash registrado.
3. **Dado** que la UAI o un auditor CGE solicita la matriz, **cuando** tiene permiso
   de consulta, **entonces** el sistema exporta un reporte consolidado normalizado
   en CSV UTF-8 según el Acuerdo No. 010-CG-2022.

### Historia de Usuario 6 - Administrar identidad y configuración (Prioridad: P3)

Como administrador de la Dirección de Tecnologías de la Información (DTI), quiero
gestionar cuentas, roles, dependencias y notificaciones, para mantener la plataforma
alineada con la estructura institucional.

**Por qué esta prioridad**: La administración de identidad y configuración sostiene
la segregación de funciones y la operación continua.

**Prueba independiente**: Aprovisionar un usuario, asignar un rol, cambiar su
dependencia y comprobar que sus permisos se actualizan sin perder auditoría.

**Escenarios de aceptación**:

1. **Dado** que existe un usuario institucional válido, **cuando** se autentica
   mediante el mecanismo aprobado por la UNL, **entonces** el sistema crea una sesión
   segura y aplica sus roles vigentes.
2. **Dado** que una dependencia cambia su estructura, **cuando** el administrador
   reasigna una recomendación, **entonces** se conserva el historial de asignaciones
   y se aplican los permisos de la nueva dependencia.
3. **Dado** que el administrador actualiza la configuración de notificaciones,
   **cuando** guarda valores válidos, **entonces** las tareas posteriores utilizan
   esa configuración y registran errores de envío.

### Casos límite

- Una recomendación no puede aprobarse si no tiene historial de revisión interna,
  evidencia PDF validada y dictamen de la UAI.
- Una evidencia rechazada no puede eliminarse para ocultar la revisión anterior.
- Un ejecutor no puede consultar ni modificar recomendaciones de otra dependencia.
- Dos usuarios que intentan cambiar simultáneamente el mismo estado no deben producir
  estados contradictorios ni auditorías incompletas.
- Un reintento de una tarea de alertas no debe enviar la misma notificación dos veces.
- Un fallo del correo no debe borrar el cambio de estado ni impedir su reintento.
- Un hash que no coincida con el archivo debe generar una alerta de integridad.
- Un recurso inexistente y un recurso de otra dependencia deben responder HTTP 404
  sin revelar si existe, y el intento no autorizado debe quedar registrado.
- Las respuestas `204 No Content`, `304 Not Modified` y `HEAD` pueden no incluir
  envoltura JSON.

## Requisitos

### Requisitos funcionales

- **RF-001 [DTI - SSO]**: Cuando un usuario ingrese credenciales institucionales,
  el sistema DEBE autenticar la sesión mediante el mecanismo institucional aprobado y
  emitir una sesión o token seguro con expiración.
- **RF-002 [DTI - RBAC]**: El sistema DEBE permitir al administrador DTI asignar y
  revocar los roles `DTI`, `UAI`, `EJECUTOR`, `RECTORADO` y `CGE_AUDITOR`, manteniendo
  segregación de funciones.
- **RF-003 [DTI - Estructura orgánica]**: Si cambia la estructura administrativa,
  el sistema DEBE permitir reasignar una recomendación a otra unidad conservando el
  historial y la bitácora anterior.
- **RF-004 [DTI - SMTP]**: Mientras las notificaciones estén activas, el sistema
  DEBE registrar alertas dentro del sistema y gestionar su entrega por correo
  electrónico institucional respetando la configuración y límites del servicio.
- **RF-005 [UAI - Informe]**: Cuando la UAI reciba un examen especial, el sistema
  DEBE registrar número de informe, fecha de notificación, período auditado y
  documento oficial.
- **RF-006 [UAI - Recomendación]**: Cuando la UAI cree una recomendación, el sistema
  DEBE exigir plazo legal, prioridad y unidad ejecutora e inicializarla en `Pendiente`.
- **RF-007 [Ejecutor - Plan]**: Cuando la recomendación esté en `En Planificación`,
  el sistema DEBE permitir un plan con N hitos y fechas que no excedan el plazo legal.
- **RF-008 [Ejecutor - PDF]**: Cuando el ejecutor cargue un medio de verificación,
  el sistema DEBE validar que sea PDF, verificar que no supere 30 MB, comprobar su
  contenido, almacenarlo y calcular SHA-256.
- **RF-009 [UAI - Estados]**: El sistema DEBE gestionar el flujo `Pendiente`,
  `En Planificación`, `En Ejecución`, `En Revisión Interna`, `Cumplida`,
  `Rechazada/Corrección` y `En Mora`, con transiciones y roles explícitos.
- **RF-010 [UAI - Dictamen]**: Cuando la UAI considere insuficiente una evidencia, el
  sistema DEBE registrar observaciones, cambiar a `Rechazada/Corrección` y conservar
  los archivos y revisiones previas.
- **RF-011 [Sistema - Alertas]**: Cuando falten 15 días o menos para el vencimiento
  y no exista evidencia presentada que cumpla las condiciones, el sistema DEBE
  notificar al ejecutor y a la UAI.
- **RF-012 [Sistema - Mora]**: Si vence el plazo sin evidencia aprobada, el sistema
  DEBE cambiar a `En Mora` únicamente al cumplirse las condiciones temporales y de
  negocio, y notificar a la máxima autoridad.
- **RF-013 [Rectorado - Tablero]**: Mientras la máxima autoridad consulte el tablero,
  el sistema DEBE presentar semáforo de riesgo, porcentaje global y unidades en mora.
- **RF-014 [UAI/CGE - Matriz]**: Cuando un usuario autorizado solicite la matriz,
  el sistema DEBE exportar un archivo CSV UTF-8 con columnas normalizadas y
  contenido consolidado según el Acuerdo No. 010-CG-2022.
- **RF-015 [Todos - API]**: El sistema DEBE exponer respuestas JSON con `success`,
  `message`, `data`, `errors` y `meta`, incluyendo `request_id` UUID v4 y timestamp
  ISO-8601 UTC, salvo las excepciones HTTP definidas.
- **RF-016 [Todos - Errores]**: El sistema DEBE clasificar errores como
  `VALIDATION_ERROR`, `AUTHENTICATION_REQUIRED`, `PERMISSION_DENIED`,
  `RESOURCE_NOT_FOUND`, `BUSINESS_RULE_VIOLATION`, `CONFLICT` o `INTERNAL_ERROR`,
  sin exponer detalles internos.
- **RF-017 [Todos - Auditoría]**: El sistema DEBE registrar toda operación mutativa
  con usuario, fecha UTC, IP disponible, `request_id`, entidad, identificador,
  operación, estado anterior, estado nuevo y resultado.
- **RF-018 [CGE - Consulta]**: El sistema DEBE proporcionar al auditor CGE acceso de
  solo lectura al historial, eventos y verificación de integridad permitidos por su
  rol.
- **RF-019 [Seguridad de objeto]**: Si un ejecutor solicita una recomendación de
  otra unidad, entonces el sistema DEBE responder HTTP 404 sin revelar la existencia
  del recurso y registrar internamente el intento.
- **RF-020 [Concurrencia]**: El sistema DEBE ejecutar cambios de estado, cargas de
  evidencia y ajustes de plazos como operaciones atómicas que impidan actualizaciones
  perdidas y transiciones contradictorias.
- **RF-021 [Jobs]**: Las tareas de plazos DEBEN ser idempotentes, tolerantes a
  reintentos, observables, resistentes a duplicados y deben registrar ejecuciones y
  errores.
- **RF-022 [OpenAPI]**: Si el proyecto adopta el contrato OpenAPI, la especificación
  DEBE mantenerse sincronizada con el comportamiento publicado y verificarse
  automáticamente.

### Requisitos no funcionales

- **RNF-001 - Integridad documental**: La verificación de cada evidencia PDF DEBE
  detectar modificaciones mediante SHA-256, controles de almacenamiento y auditoría.
  El hash no constituye autenticidad por sí solo.
- **RNF-002 - Auditoría**: La bitácora DEBE ser consultable solo por roles autorizados
  y estar protegida contra modificación o eliminación no autorizada.
- **RNF-003 - Autorización**: Las comprobaciones RBAC y a nivel de objeto DEBEN
  ejecutarse en servidor para cada recurso y operación.
- **RNF-004 - Contrato**: Las respuestas exitosas DEBEN mantener `errors=null`; las
  fallidas DEBEN mantener `data=null` y un código 4xx/5xx.
- **RNF-005 - Rendimiento**: Al menos el 95% de las consultas ordinarias del tablero
  DEBE mostrar resultados en menos de 3 segundos bajo la carga institucional definida.
- **RNF-006 - Exportación**: El 95% de las solicitudes de matriz dentro del volumen
  institucional acordado DEBE completarse en menos de 5 segundos.
- **RNF-007 - Disponibilidad**: Un fallo de correo DEBE registrarse y reintentarse sin
  revertir transacciones de negocio confirmadas; la alerta dentro del sistema debe
  permanecer disponible aunque el correo no se entregue.
- **RNF-008 - Privacidad**: Las respuestas, registros y exportaciones NO DEBEN exponer
  credenciales, tokens, contraseñas, trazas, SQL ni datos no autorizados.
- **RNF-009 - Requisitos**: Los requisitos DEBEN usar sintaxis EARS y cada uno DEBE
  tener por lo menos un escenario BDD `Given / When / Then`.

### Catálogo de estados

| Estado | Entrada permitida | Condición mínima |
| --- | --- | --- |
| Pendiente | Registro inicial | Recomendación registrada con plazo y responsable |
| En Planificación | Inicio de planificación | Unidad responsable y plan en elaboración |
| En Ejecución | Plan aprobado | Hitos y fechas dentro del plazo |
| En Revisión Interna | Evidencia presentada | Evidencia disponible para dictamen UAI |
| Cumplida | Dictamen favorable UAI | Revisión previa y PDF validado |
| Rechazada/Corrección | Dictamen desfavorable UAI | Observaciones registradas y archivo conservado |
| En Mora | Vencimiento aplicable | Plazo vencido sin evidencia aprobada |

Las transiciones, autorizaciones y eventos DEBEN validarse en el dominio y auditarse
transaccionalmente.

### Contrato universal de respuesta

```json
{
  "success": true,
  "message": "Mensaje claro y descriptivo para el cliente",
  "data": {},
  "errors": null,
  "meta": {
    "request_id": "UUID-v4",
    "timestamp": "ISO-8601 UTC",
    "version": "v1",
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total_items": 100,
      "total_pages": 10
    }
  }
}
```

### Escenarios críticos BDD adicionales

#### Escenario 1: Salto ilegal a `Cumplida`

- **Given** una recomendación en `En Ejecución` con un PDF cargado pero no evaluado,
- **When** se solicita cambiarla directamente a `Cumplida`,
- **Then** el sistema mantiene `En Ejecución`, devuelve HTTP 409 y explica que
  requiere revisión previa de la UAI.

#### Escenario 2: Protección contra BOLA/IDOR

- **Given** un ejecutor de la Facultad Jurídica,
- **When** intenta consultar o cargar evidencia en una recomendación de la Facultad
  de la Salud,
- **Then** el sistema responde HTTP 404 sin revelar la existencia del recurso y
  registra el intento no autorizado.

#### Escenario 3: Carga válida de evidencia

- **Given** una recomendación asignada al ejecutor en `En Ejecución`,
- **When** carga `evidencia_01.pdf` válido,
- **Then** el sistema lo conserva, calcula SHA-256, registra auditoría, cambia a
  `En Revisión Interna` y devuelve HTTP 201 con la envoltura universal.

## Entidades principales

- **Usuario**: identidad institucional, estado, roles y dependencia.
- **Rol**: conjunto de permisos institucionales.
- **Dependencia**: unidad orgánica responsable de ejecutar recomendaciones.
- **Informe CGE**: examen especial, número, período, notificación y documento oficial.
- **Recomendación**: obligación emitida por la CGE, con prioridad, plazo, estado,
  unidad responsable y relación con un informe.
- **Plan de Acción**: conjunto ordenado de hitos y fechas de compromiso.
- **Hito**: acción verificable dentro del plan.
- **Evidencia**: PDF, metadatos, hash, estado de revisión y observaciones.
- **Revisión**: dictamen de la UAI, usuario, fecha, resultado y observaciones.
- **Evento de Auditoría**: operación, actor, solicitud, entidad, estados y resultado.
- **Notificación**: alerta dentro del sistema y correo electrónico, con destinatario,
  motivo, fecha, estado de entrega y reintentos.
- **Matriz de Cumplimiento**: reporte consolidado exportable como CSV UTF-8, con
  encabezados y columnas normalizadas.

## Criterios de Éxito

### Resultados medibles

- **SC-001**: El 100% de las recomendaciones nuevas conserva responsable, plazo,
  estado inicial y vínculo con un informe.
- **SC-002**: El 100% de las transiciones a `Cumplida` verificadas posee revisión
  interna y al menos una evidencia PDF validada por la UAI.
- **SC-003**: El 100% de las operaciones mutativas produce un evento de auditoría
  con los campos mínimos definidos.
- **SC-004**: El 100% de los intentos de acceso de un ejecutor a otra dependencia es
  rechazado y queda registrado.
- **SC-005**: Al menos el 95% de las consultas ordinarias del tablero se completa en
  menos de 3 segundos con la carga institucional definida.
- **SC-006**: Al menos el 95% de las exportaciones de matriz se completa en menos de
  5 segundos dentro del volumen institucional acordado.
- **SC-007**: El 100% de las evidencias modificadas después de su almacenamiento
  produce una discrepancia detectable al verificar su hash.
- **SC-008**: El 100% de los vencimientos aplicables sin evidencia aprobada se marca
  `En Mora` y notifica a los roles definidos sin duplicar mensajes por reintento.
- **SC-009**: Al menos el 90% de los usuarios representativos completa su tarea
  principal sin asistencia en una evaluación de aceptación.
- **SC-010**: Toda versión publicada conserva trazabilidad desde requisito hasta
  prueba automatizada y documentación asociada.

## Supuestos

- La UNL proporcionará el mecanismo institucional de autenticación y el directorio
  actualizado de usuarios, roles y dependencias.
- La UAI será la autoridad responsable de validar evidencias y dictaminar cumplimiento.
- Los documentos de evidencia serán PDF de hasta 30 MB por archivo.
- El marco legal se verificará antes de implementar interpretaciones jurídicas
  específicas; esta especificación no sustituye asesoría legal.
- Los vencimientos, alertas y fechas legales se calcularán en la zona horaria
  `America/Guayaquil` (UTC-5); la auditoría conservará timestamps en UTC.
- La configuración de alertas, escalamiento y retención se confirmará durante la
  planificación con las áreas responsables; la primera versión usará alertas dentro
  del sistema y correo electrónico institucional.
- La integración en tiempo real con la base de datos de la CGE y las responsabilidades
  penales o judiciales están fuera de esta versión.
- El mecanismo concreto de persistencia, almacenamiento, correo y despliegue se
  decidirá en el plan técnico sin alterar estos requisitos de negocio.
- La exportación oficial de esta versión es CSV UTF-8; Excel o PDF quedan fuera del
  alcance hasta que exista una plantilla institucional aprobada.

## Fuera de alcance

- Sincronización automática en tiempo real con sistemas internos de la CGE.
- Gestión de responsabilidades penales o judiciales.
- Interpretación automática de normas o sustitución del dictamen de la UAI.
- Modificación o eliminación de evidencias aprobadas para ocultar su historial.
