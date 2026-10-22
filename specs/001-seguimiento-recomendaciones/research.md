# Investigación y Decisiones: Seguimiento de Recomendaciones CGE

**Fecha**: 2026-10-19

## Decisión 1: Stack inicial

- **Decisión**: adoptar Python 3.10 como mínimo compatible validado y Python 3.12
  como objetivo, junto con Django 5.2, Django REST Framework y PostgreSQL,
  junto con React, TypeScript y Vite para el frontend.
- **Razón**: el dominio es transaccional, relacional y requiere un ORM maduro,
  validación de datos, autenticación institucional, tareas y pruebas de integración.
  El prompt también menciona `transaction.atomic` y `select_for_update`.
- **Alternativas consideradas**: NestJS/TypeScript y otro framework REST. Se reservan
  como alternativas si el equipo confirma experiencia o infraestructura distinta.
- **Criterio operativo**: CI debe validar el mínimo 3.10 y el objetivo 3.12 hasta
  que DTI apruebe retirar el mínimo.

## Decisión 2: Identidad institucional

- **Decisión**: definir un puerto de autenticación institucional y permitir un
  adaptador LDAP/CAS o el mecanismo SSO que la UNL apruebe.
- **Razón**: evita acoplar dominio y casos de uso a un proveedor concreto y mantiene
  la autorización en el servidor.
- **Alternativas consideradas**: usuarios locales, OAuth2/OIDC y tokens propios.
- **Pendiente**: confirmar proveedor, protocolo, claims, rotación y expiración.

## Decisión 3: Persistencia de PDF

- **Decisión**: almacenar metadatos y hash en PostgreSQL y el contenido mediante un
  puerto de almacenamiento seguro.
- **Razón**: separa datos transaccionales de binarios, facilita controles de acceso y
  permite verificar el contenido después.
- **Alternativas consideradas**: almacenar binarios en PostgreSQL o usar un servicio
  de objetos institucional.
- **Pendiente**: confirmar proveedor, retención, cifrado, tamaño máximo y recuperación.

## Decisión 4: Concurrencia

- **Decisión**: transacción atómica con bloqueo de la recomendación mediante
  `SELECT ... FOR UPDATE` para transiciones, dictámenes y ajustes de plazos.
- **Razón**: la regla de estado y la auditoría deben confirmarse juntas y no pueden
  aceptar actualizaciones perdidas.
- **Alternativas consideradas**: control optimista con versión de fila. Puede añadirse
  para lecturas largas, pero no sustituye el control transaccional crítico inicial.

## Decisión 5: Alertas

- **Decisión**: evaluar vencimientos de forma idempotente; alertar a 15 días o menos
  y marcar `En Mora` solo al cumplirse plazo y ausencia de evidencia aprobada.
  Las alertas se persisten dentro del sistema y también se intentan entregar por
  correo institucional; un fallo SMTP no elimina la alerta interna.
- **Razón**: coincide con la constitución y evita confundir evidencia presentada con
  evidencia validada.
- **Alternativas consideradas**: umbrales 30/15/5 del texto de referencia. Se dejan
  como configuración futura y requieren aprobación normativa.

## Decisión 6: Contrato API

- **Decisión**: REST bajo `/api/v1/`, OpenAPI 3.1 y envoltura universal. La matriz
  se solicita mediante `POST /reportes/matriz-cge` y se devuelve exclusivamente
  como CSV UTF-8. No se incorpora `QUERY`.
- **Razón**: conserva semántica HTTP estándar y un contrato comprobable.
- **Alternativas consideradas**: `POST` para búsquedas complejas y GraphQL.

## Decisión 7: Política de autorización de objeto

- **Decisión**: un ejecutor que solicite una recomendación de otra dependencia
  recibe HTTP 404, sin confirmar si el recurso existe; el intento se audita.
- **Razón**: reduce la divulgación de información y hace determinista la prueba
  BOLA/IDOR.
- **Alternativas consideradas**: HTTP 403 o una política mixta para consultas y
  modificaciones. Se descartan para esta versión.

## Decisión 8: Carga de referencia para rendimiento

- **Decisión**: validar p95 con 1.000 recomendaciones, 200 usuarios y 20 consultas
  concurrentes; el tablero debe responder en menos de 3 segundos y la matriz CSV
  en menos de 5 segundos.
- **Razón**: convierte los objetivos relativos de la especificación en pruebas
  reproducibles sin fijar todavía el límite máximo de producción.
- **Alternativas consideradas**: dejar la carga abierta hasta producción. Se
  descarta porque impediría validar el rendimiento durante desarrollo.
