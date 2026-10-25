# Organización para cuatro integrantes

La distribución asigna una responsabilidad principal a cada integrante, pero todos
deben revisar la integración y conocer el flujo completo.

## Integrante 1 — Backend y dominio

**Responsabilidad**: reglas institucionales y casos de uso.

- Máquina de estados.
- Recomendaciones, planes y dictámenes.
- Validaciones de negocio.
- Transacciones y concurrencia.
- Pruebas unitarias del dominio.

**Tareas iniciales**: T008, T019, T023-T027, T033-T035, T044-T047.

## Integrante 2 — Persistencia, seguridad y auditoría

**Responsabilidad**: datos confiables y control de acceso.

- PostgreSQL y migraciones.
- Usuarios, roles y dependencias.
- RBAC y autorización por dependencia.
- Auditoría inmutable.
- Hash e integridad de archivos.
- Pruebas de seguridad y concurrencia.

**Tareas iniciales**: T014-T020, T036-T038, T043, T052, T063-T067, T073-T080.

## Integrante 3 — Frontend y experiencia de usuario

**Responsabilidad**: pantallas comprensibles para cada actor.

- Inicio de sesión.
- Bandejas de UAI y ejecutores.
- Formularios y carga de evidencia.
- Dashboard de Rectorado.
- Mensajes de error y estados visibles.
- Pruebas de componentes y accesibilidad.

Las tareas frontend se agregan al plan cuando el backend estabilice los contratos
OpenAPI. No debe duplicar reglas de negocio del backend.

## Integrante 4 — Calidad, integración y documentación

**Responsabilidad**: demostrar que el sistema funciona y puede ser entendido.

- Contratos OpenAPI.
- Pruebas de integración y Playwright.
- Alertas, reportes y exportaciones.
- CI, lint y detección de secretos.
- Manual técnico y manual de usuario.
- Preparación de demostraciones y PDF final.

**Tareas iniciales**: T055-T062, T068-T072, T081-T088.

## Reglas de coordinación

- Cada integrante trabaja en una rama `feature/<nombre-corto>`.
- Una tarea solo pasa a “En revisión” cuando incluye prueba.
- Todo Pull Request debe indicar los RF/RNF afectados.
- Ningún integrante integra directamente a `main`.
- Al menos otra persona revisa cada Pull Request.
- Las decisiones que afecten arquitectura o alcance se registran en `docs/decisiones/`
  y se comunican al equipo.

## Reunión semanal de 30 minutos

1. Qué se terminó.
2. Qué se demostrará.
3. Qué está bloqueado.
4. Qué requisito o tarea se actualizará.
5. Qué documentación debe cambiar.
