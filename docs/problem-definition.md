# Delimitación del Problema y Alcance - Recomendaciones CGE

## 1. Delimitación del Problema
El problema central radica en la falta de trazabilidad y automatización en el cumplimiento de las recomendaciones emitidas por la Contraloría General del Estado (CGE) a la Universidad Nacional de Loja (UNL). La gestión dispersa actual dificulta el seguimiento formal y el reporte oportuno de los estados de cumplimiento.

## 2. Actores y Necesidades
*   **UAI (Auditoría Interna):** Requiere auditar y validar las evidencias de cumplimiento.
*   **Ejecutores/Responsables de unidades:** Necesitan cargar evidencias y notificar el cumplimiento de sus tareas asignadas.
*   **Máxima Autoridad (Rectorado):** Requiere visualizar el estado general de la institución frente a la CGE.
*   **CGE:** Entidad emisora que requiere los reportes finales (matrices de cumplimiento).

## 3. Alcance Inicial
**Dentro del alcance:**
*   Registro de recomendaciones y asignación de responsables.
*   Carga de evidencias (archivos PDF).
*   Flujo de aprobación y trazabilidad de cambios.

**Fuera del alcance (Explícito):**
*   Interconexión por API en tiempo real o sincronización automática con la base de datos interna de la CGE (se limita a exportación de matrices).
*   Gestión de responsabilidades penales/judiciales asociadas.

## 4. Matriz de Riesgos Tempranos
*   **Riesgo Crítico (Normativo/Lógica de Negocio):** Modelado Incorrecto del Flujo de Estados de Cumplimiento. Si no se alinean las validaciones internas (UAI) con la normativa de la CGE (Acuerdo 010-CG-2022), el sistema podría dar por "cumplida" una recomendación que normativamente aún está rechazada o pendiente.
*   **Riesgos adicionales:** Riesgos operativos de adopción del sistema y seguridad de datos en los documentos PDF cargados.