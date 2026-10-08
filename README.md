# Seguimiento_de_recomendaciones_CGE
Sistema de información web para la Universidad Nacional de Loja (UNL) que garantice el cumplimiento de las recomendaciones emitidas por la Contraloría General del Estado (CGE) de Ecuador.

## Implementación base incluida

- **Modelo de datos principal** en `src/seguimiento_cge/models.py` para:
  - `InformeCGE`
  - `Recomendacion`
  - `PlanAccion`
  - `MedioVerificacion`
  - `HistorialAuditoria`
- **RBAC + máquina de estados** en `src/seguimiento_cge/rbac.py` con roles:
  - Administrador (UAI/DTI)
  - Máxima Autoridad
  - Responsable/Ejecutor de Unidad
  - Consultor/Observador
- **Motor de notificaciones + semáforo de plazos** en `src/seguimiento_cge/notifications.py`:
  - Verde: `> 30` días
  - Amarillo: `15-30` días
  - Rojo: `< 15` días
  - Negro: vencido (`< 0` días)
- **Módulo de reportes** en `src/seguimiento_cge/reports.py`:
  - Exportación de matriz institucional a **PDF**
  - Exportación de matriz institucional a **Excel (.xlsx)**

## Pruebas

```bash
PYTHONPATH=src python -m unittest discover -s tests -p "test_*.py"
```
