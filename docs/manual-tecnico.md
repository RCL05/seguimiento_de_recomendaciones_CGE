# Manual técnico de SITRA-CGE UNL

**Estado**: guía viva de desarrollo  
**Versión**: 0.1.0  
**Última actualización**: 2026-10-20

## 1. Propósito

Este manual explica cómo instalar, entender, probar y mantener SITRA-CGE UNL.
Describe el sistema para desarrolladores y responsables técnicos, no para usuarios
finales.

## 2. Arquitectura

El backend se divide en Presentación/API, Aplicación, Dominio e Infraestructura.
Las reglas de recomendaciones viven en el dominio y no deben depender del ORM,
PostgreSQL o el proveedor de archivos.

```mermaid
flowchart TB
    UI[Frontend React] --> API[API REST]
    API --> APP[Casos de uso]
    APP --> DOM[Dominio y estados]
    APP --> DB[(PostgreSQL)]
    APP --> FILES[(Almacenamiento PDF)]
    APP --> SMTP[SMTP institucional]
    APP --> AUDIT[Auditoría]
```

## 3. Instalación local

El bloque ejecutable actual usa SQLite para desarrollo rápido; PostgreSQL queda
como adaptador de persistencia del siguiente tramo. Para levantar la API y la
vista de demostración:

```powershell
Set-Location backend
python -m pip install -e ".[test]"
python manage.py check
python manage.py migrate
python -m pytest -q
python manage.py runserver
```

Luego abrir `http://127.0.0.1:8000/`. La vista HTML consulta el endpoint
`/api/v1/recomendaciones`; el endpoint `/health/` sirve como comprobación rápida.
El login actual es un adaptador de desarrollo y no reemplaza el SSO institucional.
Las evidencias PDF tienen un límite de 30 MB por archivo.

Nunca se deben colocar contraseñas reales en este archivo ni en Git.

## 4. Contrato y seguridad

La API usa `/api/v1/`, la envoltura universal y `request_id`. Todo endpoint debe
validar autenticación, rol y pertenencia a la dependencia. El contrato completo se
encuentra en [`openapi.yaml`](../specs/001-seguimiento-recomendaciones/contracts/openapi.yaml).

## 5. Pruebas

La validación mínima incluye:

- reglas de la máquina de estados;
- carga y hash de PDF;
- autorización BOLA entre dependencias;
- auditoría;
- concurrencia;
- respuestas de error;
- escenarios completos del [quickstart](../specs/001-seguimiento-recomendaciones/quickstart.md).

## 6. Mantenimiento

Antes de modificar una regla:

1. localizar el RF/RNF en la especificación;
2. revisar la tarea y el contrato afectados;
3. actualizar prueba;
4. implementar;
5. actualizar esta documentación;
6. registrar la decisión si cambia la arquitectura.
