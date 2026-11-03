# Guía de Validación: Seguimiento de Recomendaciones CGE

## Prerrequisitos

- Stack aprobado y entorno de ejecución configurado.
- PostgreSQL disponible con una base de pruebas.
- Mecanismo SSO de pruebas o adaptador simulado.
- Almacenamiento de archivos de pruebas y servidor SMTP simulado.
- Dependencias de desarrollo instaladas según el manifiesto que se apruebe.

## Preparación

1. Crear una base de datos de prueba y aplicar migraciones.
2. Crear usuarios de prueba con roles DTI, UAI, EJECUTOR, RECTORADO y CGE_AUDITOR.
3. Crear dos dependencias distintas y asignar el ejecutor a la primera.
4. Cargar datos de un informe y una recomendación con plazo conocido.
5. Configurar un reloj controlable para probar vencimientos e idempotencia.

## Escenarios de validación

### Flujo principal

1. Autenticar un usuario UAI.
2. Registrar un informe y una recomendación.
3. Asignar la recomendación a la dependencia del ejecutor.
4. Crear el plan de acción y sus hitos.
5. Autenticar al ejecutor y cargar un PDF válido.
6. Confirmar HTTP 201, `request_id`, hash SHA-256 y estado `En Revisión Interna`.
7. Autenticar a la UAI, revisar y aprobar la evidencia.
8. Confirmar `Cumplida` solo después del historial de revisión.
9. Consultar la bitácora y verificar la cadena completa de eventos.

### Rechazo y corrección

1. Cargar evidencia insuficiente.
2. Rechazarla con observaciones desde UAI.
3. Confirmar `Rechazada/Corrección`, conservación del archivo y notificación.
4. Cargar una nueva evidencia y repetir la revisión.

### Seguridad BOLA/IDOR

1. Autenticar un ejecutor de la dependencia A.
2. Solicitar una recomendación de la dependencia B.
3. Confirmar HTTP 404 sin revelar la existencia del recurso.
4. Confirmar un evento de seguridad con `request_id`.

### Concurrencia

1. Enviar dos cambios de estado simultáneos para la misma recomendación.
2. Confirmar que solo una transición válida se confirma.
3. Confirmar que el estado final y el audit log son consistentes.
4. Repetir una tarea de alerta y confirmar que no se duplica la notificación.

### Integridad documental

1. Cargar un PDF válido y conservar el hash inicial.
2. Modificar el contenido en el almacenamiento de prueba.
3. Ejecutar la verificación.
4. Confirmar que se detecta la discrepancia sin tratar el hash como prueba única de
   autenticidad.

### Plazos y reportes

1. Fijar el reloj a 15 días antes del vencimiento sin evidencia presentada válida.
2. Ejecutar la tarea y confirmar una alerta idempotente.
3. Fijar el reloj después del vencimiento sin evidencia aprobada.
4. Confirmar `En Mora`, auditoría y notificación a la máxima autoridad.
5. Exportar la matriz CSV UTF-8 con usuario UAI y auditor CGE.
6. Confirmar que un ejecutor no puede exportar información no autorizada.

## Resultados esperados

- Las respuestas siguen el contrato de [openapi.yaml](./contracts/openapi.yaml).
- Los datos y reglas corresponden a [data-model.md](./data-model.md).
- Todos los requisitos RF/RNF tienen prueba o una tarea explícita para crearla.
- Ningún escenario expone secretos, SQL, trazas internas o datos de otra dependencia.
- Las pruebas de rendimiento usan 1.000 recomendaciones, 200 usuarios y 20
  consultas concurrentes como carga de referencia.

## Verificación de criterios SC (2026-10-26)

Comandos ejecutados:

```powershell
# Backend
cd backend
..\.venv\Scripts\python.exe manage.py check
..\.venv\Scripts\pytest -q

# Frontend
cd frontend
npm run lint
npm test
npm run build
npm run format:check
npx playwright test
```

Resultados obtenidos: `manage.py check` sin incidencias; 59 pruebas backend
aprobadas; 6 pruebas frontend aprobadas; 1 prueba E2E aprobada; build, lint y
formato sin errores.

| Criterio | Resultado | Evidencia / brecha |
| --- | --- | --- |
| SC-001 | CUMPLE | `tests/integration/recomendaciones/test_registration.py` y flujo principal de `test_quickstart.py` conservan responsable, plazo, estado inicial e informe. |
| SC-002 | CUMPLE | `tests/integration/evidencias/test_dictamen_flow.py` exige revisión interna y evidencia validada antes de `Cumplida`. |
| SC-003 | PARCIAL | La cadena de auditoría del flujo principal está cubierta; falta una prueba exhaustiva por cada operación mutativa publicada. |
| SC-004 | CUMPLE | `test_quickstart.py` y `test_evidence_object_authorization.py` verifican 404, ausencia de filtración y evento `ACCESS_DENIED`. |
| SC-005 | NO VERIFICADO | Solo existen umbrales declarados; falta benchmark p95 con 1.000 recomendaciones y 20 consultas concurrentes (T139). |
| SC-006 | NO VERIFICADO | La exportación CSV tiene prueba funcional, pero no medición p95 de 5 segundos con volumen institucional (T139). |
| SC-007 | CUMPLE | `tests/integration/evidencias/test_integrity_flow.py` detecta contenido alterado comparando SHA-256 almacenado y recalculado. |
| SC-008 | PARCIAL | La transición a `En Mora` e idempotencia básica están cubiertas; falta una prueba integral de notificación a todos los roles sin duplicados por reintento. |
| SC-009 | NO VERIFICADO | No existe evaluación de aceptación con usuarios representativos. |
| SC-010 | PARCIAL | La matriz RF/RNF de `plan.md` enlaza componentes, contratos y pruebas; no hay verificador automático de trazabilidad en CI. |

Las brechas SC-003, SC-005, SC-006, SC-008, SC-009 y SC-010 quedan asociadas a
las tareas de convergencia T139 y posteriores; no se declaran como cumplidas.
