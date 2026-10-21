# ADR-0011 — Módulo de Evidencias PDF (F-003) con supuestos para CL-05/CL-07

- **Estado:** Aceptado (supuestos explícitos sujetos a validación)
- **Fecha:** 2026-10-21
- **Relacionado con:** `specify.md` §3.4/§4 HU-05 (CA-05.1..05.4) y §5 RNF-03; `plan.md` §3.1; `clarify.md` CL-05, CL-07; ADR-0005, ADR-0010
- **Decisores:** Equipo de desarrollo CGE

## Contexto

La Fase 4 de `tasks.md` (T027–T032) está marcada **[BLOQUEADA]** por CL-05 (manejo/anulación de evidencia) y CL-07 (validez probatoria de evidencia digital), que siguen **pendientes de validación**. El requirente pidió avanzar con la segunda funcionalidad, que corresponde a **F-003 — Carga de Evidencias PDF (HU-05)**.

Implementar sin reglas validadas exige fijar supuestos explícitos y reversibles, en lugar de decidir silenciosamente sobre requisitos normativos.

## Decisión

Implementar el módulo de evidencias con el alcance verificable de HU-05 y los siguientes **supuestos provisionales**:

1. **Solo PDF (Fase 1)** — conforme a `specify.md` §7.h ("Las evidencias se gestionan exclusivamente en formato PDF en la Fase 1").
2. **Validación técnica (RNF-03):** extensión `.pdf`, MIME `application/pdf` y **cabecera real `%PDF-`**; tamaño máximo **10 MB**. Rechazo con mensaje del formato/límite admitido (CA-05.2, CA-05.3).
3. **Tipo de evidencia:** `BORRADOR` (avance) vs `FINAL` (entrega), distinguiendo su carácter en el registro (CA-05.4).
4. **Anulación lógica (supuesto CL-05, opción 4.A):** la evidencia **no se elimina físicamente**; pasa a estado `ANULADA` con motivo, actor y fecha, conservando el rastro (Constitución §VIII, `specify.md` §3.4). Se adopta la opción A por ser la más conservadora y compatible con la preservación de historial.
5. **Integridad:** se calcula **hash SHA-256** y se registran MIME y tamaño; el archivo se almacena con **nombre UUID** bajo `MEDIA_ROOT/evidencias/`, fuera de rutas estáticas/ejecutables (ADR-0005).
6. **Vinculación:** `Evidencia.recomendacion` con `on_delete=PROTECT` para impedir borrados en cascada que destruyan el expediente.
7. **Validez probatoria (CL-07):** se asume que **no se requieren** firma electrónica ni sellos de tiempo en Fase 1; queda pendiente confirmar contra el reglamento aplicable.

## Consecuencias

- **Positivas:** F-003 queda funcional y verificable; CA-05.1..05.4 cubiertos; base para T031 (transición atómica `En Proceso → En Validación`).
- **Negativas/riesgo:** los puntos 4 y 7 pueden cambiar si CL-05/CL-07 se resuelven de otro modo; el límite de 10 MB y la exclusividad PDF son parámetros ajustables.
- **Reversibilidad:** el estado de evidencia y el tipo están modelados como `TextChoices`; anulación y validación están aisladas en `validators.py`/`models.py`, facilitando el cambio sin rediseño.

## Trazabilidad a pruebas

- `test_acepta_pdf_valido`, `test_rechaza_extension_no_pdf`, `test_rechaza_mime_incorrecto`, `test_rechaza_archivo_sin_cabecera_pdf`, `test_rechaza_archivo_demasiado_grande` → RNF-03, CA-05.2/05.3.
- `test_calcula_tamano_y_hash` → integridad.
- `test_anulacion_logica_conserva_registro`, `test_no_se_puede_anular_dos_veces` → CL-05 (supuesto 4), `specify.md` §3.4.

## Pendientes

- Validar CL-05 y CL-07 con el requirente y actualizar este ADR si cambian los supuestos.
- Implementar T031 (transición atómica con cambio de estado) e historial append-only (T034) para cumplir CA-05.1 y CA-07.1/07.3 completos.
