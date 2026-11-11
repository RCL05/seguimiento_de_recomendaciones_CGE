# ACD 3 - Revision individual del contrato API

**Integrante:** Derick Paul Vargas Vasquez

## Decision analizada
Revisar el uso del codigo HTTP 201 Created y la cabecera Location en el registro de recomendaciones.

## Alternativa considerada
Utilizar 200 OK en lugar de 201 Created al registrar una nueva recomendacion.

## Justificacion
Se considera adecuado utilizar 201 Created porque la operacion POST crea un nuevo recurso. La cabecera Location permite identificar la ruta de la recomendacion creada.

La prueba test_201_incluye_location_del_recurso_creado comprueba que la respuesta utiliza 201, incluye Location y permite consultar el recurso mediante GET con resultado 200.

## Observacion recibida
No se ha registrado una observacion del docente o del equipo sobre esta decision.

## Resultado de la revision
Se recomienda mantener el contrato HTTP existente. No se requieren modificaciones funcionales.

## Evidencia tecnica
Archivo revisado: backend/tests/api/test_http_semantics.py

Prueba revisada: test_201_incluye_location_del_recurso_creado

Nota: Se reviso el codigo de la prueba; no se afirma haber ejecutado las pruebas automatizadas.
