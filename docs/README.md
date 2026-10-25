# Documentación del proyecto

Esta carpeta contiene la documentación que acompaña al sistema SITRA-CGE UNL.
La documentación se mantiene en Markdown para que pueda revisarse con Git y
convertirse posteriormente a PDF.

## Ruta de lectura para cualquier persona

1. [Resumen y hoja de ruta](./hoja-de-ruta.md)
2. [Cómo se reparte el trabajo](./equipo-y-responsabilidades.md)
3. [Cómo se demuestra cada requisito](./trazabilidad.md)
4. [Manual técnico](./manual-tecnico.md)
5. [Manual de usuario](./manual-usuario.md)

## Regla de actualización

Cada cambio funcional debe actualizar, en este orden:

1. La especificación en `specs/001-seguimiento-recomendaciones/spec.md`.
2. La tarea correspondiente en `specs/001-seguimiento-recomendaciones/tasks.md`.
3. El código y las pruebas.
4. La fila correspondiente en [trazabilidad.md](./trazabilidad.md).
5. El manual técnico o de usuario, si el cambio es visible para usuarios.

El PDF es un formato de entrega generado a partir de estos archivos fuente. No se
debe editar el PDF directamente.
