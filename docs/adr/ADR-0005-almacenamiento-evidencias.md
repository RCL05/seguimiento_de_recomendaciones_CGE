# ADR-0005 — Almacenamiento seguro de evidencias (metadata en BD, archivo en almacenamiento controlado)

- **Estado:** Aceptado
- **Fecha:** 2026-10-21
- **Relacionado con:** Constitución §VI y §VII; `plan.md` §3.4; `specify.md` RNF-03
- **Decisores:** Equipo de desarrollo CGE

## Contexto

Las evidencias (PDF) son el acervo probatorio del sistema. Deben almacenarse de forma segura, no ejecutarse, y su metadata debe ser consultable e íntegra. Los archivos pueden ser pesados y no conviene almacenarlos como blobs dentro del motor transaccional.

## Decisión

Mantener la **metadata** (mime, tamaño, hash, ruta lógica, estado, tipo) en la base de datos y almacenar el **archivo físico** en un almacenamiento controlado, accedido mediante un puerto del dominio (`AlmacenEvidencias`). En F1 se usa un volumen controlado; el puerto permite sustituirlo por almacenamiento de objetos sin cambiar el dominio.

## Consecuencias

- **Positivas:** separa el ciclo de vida del archivo del transaccional; permite escalar el almacenamiento; nombres internos (UUID) evitan path traversal.
- **Negativas:** requiere coordinar la atomicidad entre la escritura del archivo y el registro en BD (transacción + compensación si falla la escritura).

## Alternativas consideradas

- **Blob en la base de datos:** rechazada por impacto en rendimiento y respaldo.
- **Sistema de archivos con nombre original:** rechazada por riesgo de seguridad (colisiones, path traversal).
