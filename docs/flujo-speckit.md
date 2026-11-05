# Flujo Spec Kit del proyecto

Este proyecto usa una secuencia repetible para que el equipo pueda avanzar sin
perder la relación entre necesidad institucional, código y pruebas:

```text
specify -> clarify -> plan -> tasks -> implement -> converge
```

## Hooks opcionales

La configuración vive en [`../.specify/extensions.yml`](../.specify/extensions.yml).
Los hooks no se ejecutan automáticamente ni bloquean el trabajo; después de cada
fase muestran una acción sugerida:

| Momento | Comando sugerido | Propósito |
|---|---|---|
| Después de aclarar | `/speckit-analyze` | Detectar contradicciones en la especificación |
| Después del plan | `/speckit-analyze` | Revisar cobertura de arquitectura y contratos |
| Después de tareas | `/speckit-analyze` | Revisar dependencias y preparación |
| Después de implementar | `/speckit-converge` | Detectar trabajo todavía no construido |

## Secuencia práctica actual

1. Ejecutar `/speckit-analyze` para revisar el estado actual.
2. Ejecutar `/speckit-tasks` si cambió la especificación o el plan.
3. Ejecutar `/speckit-implement` para el siguiente bloque.
4. Ejecutar `/speckit-converge` después de una implementación verificable.
5. Repetir hasta que las tareas críticas estén completas.

Los hooks son recordatorios de trazabilidad, no sustituyen las pruebas ni la
revisión del equipo. Las tareas solo deben marcarse como completadas cuando exista
código y una validación reproducible.
