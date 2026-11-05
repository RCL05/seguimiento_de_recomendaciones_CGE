# SITRA-CGE UNL

Sistema para la gestión, seguimiento y trazabilidad de las recomendaciones
emitidas por la Contraloría General del Estado (CGE) para la Universidad
Nacional de Loja (UNL).

## Alcance

SITRA-CGE permite registrar informes y recomendaciones, asignar unidades
responsables, gestionar planes de acción, adjuntar evidencias PDF, revisar
dictámenes, consultar auditoría y exportar la matriz de cumplimiento.

- Backend: Django 5, API REST y SQLite para desarrollo local.
- Frontend: React, TypeScript y Vite.
- Autenticación local de desarrollo: credenciales SSO simuladas que emiten JWT.
- Evidencias: archivos PDF almacenados en `backend/media/evidencias/`.

La planificación y trazabilidad se encuentran en
[`specs/001-seguimiento-recomendaciones/`](specs/001-seguimiento-recomendaciones/).
La documentación complementaria está en [`docs/`](docs/).

## Requisitos previos

- Python 3.10 o superior
- Node.js 20 o superior y npm
- Git
- Visual Studio Code (opcional)

## Puesta en marcha local

Los comandos siguientes se ejecutan desde la raíz del repositorio. En Windows
PowerShell se recomienda usar `py` para seleccionar Python; en macOS/Linux se
puede usar `python3`.

### 1. Clonar el repositorio

```bash
git clone https://github.com/RCL05/seguimiento_de_recomendaciones_CGE.git
cd seguimiento_de_recomendaciones_CGE
```

### 2. Crear y activar el entorno virtual

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación para el usuario actual:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias del backend

```bash
python -m pip install --upgrade pip
python -m pip install -e "backend[test]"
```

También puede instalarse el archivo de dependencias:

```bash
python -m pip install -r backend/requirements.txt
```

### 4. Configurar variables de entorno

Copie `backend/.env.example` como referencia y configure, como mínimo:

```text
DJANGO_DEBUG=true
DJANGO_SECRET_KEY=clave-local-de-al-menos-32-caracteres
JWT_SIGNING_KEY=clave-jwt-local-de-al-menos-32-caracteres
DJANGO_MEDIA_ROOT=./media
```

En desarrollo, si `POSTGRES_DB` está vacío, Django utiliza
`backend/development.sqlite3`. No incluya credenciales institucionales ni
secretos reales en el repositorio.

### 5. Ejecutar migraciones Django

```bash
python backend/manage.py migrate
```

### 6. Crear datos iniciales

El siguiente comando crea unidades base para los usuarios de prueba. Los
usuarios se crean automáticamente al iniciar sesión con un token SSO de
desarrollo.

```bash
python backend/manage.py shell -c "from backend.modules.usuarios.models import UnidadOrganica; [UnidadOrganica.objects.get_or_create(codigo=codigo, defaults={'nombre': nombre}) for codigo, nombre in [('UAI', 'Auditoría Interna'), ('DEP-A', 'Departamento A'), ('DTI', 'Dirección de Tecnologías de la Información'), ('RECTORADO', 'Rectorado')]]"
```

### 7. Preparar el almacenamiento de evidencias

```bash
mkdir -p backend/media/evidencias
```

En Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force backend\media\evidencias
```

### 8. Iniciar el backend

```bash
python backend/manage.py runserver 127.0.0.1:8000
```

Comprobación de salud:

```text
http://127.0.0.1:8000/health/
```

### 9. Instalar y ejecutar el frontend

En otra terminal, desde la raíz:

```bash
cd frontend
npm ci
npm run dev
```

La aplicación estará disponible normalmente en
`http://127.0.0.1:5173/`. Para apuntar a otro backend, configure
`VITE_API_BASE` antes de iniciar Vite.

## Credenciales SSO de prueba

Con `DJANGO_DEBUG=true`, el backend reconoce estos tokens en
`backend/modules/usuarios/infrastructure/sso_adapter.py`. Al autenticarse,
el backend devuelve un JWT Bearer temporal de una hora; el token SSO no debe
usarse como encabezado `Authorization`.

| Token SSO | Rol | Unidad | Permisos principales | Estado |
|---|---|---|---|---|
| `uai-sso-token` | `UAI` | `UAI` | Registrar informes y recomendaciones, consultar unidades, revisar/aprobar o rechazar evidencias, consultar auditoría y exportar matrices. | Disponible |
| `ejecutor-sso-token` | `EJECUTOR` | `DEP-A` | Consultar recomendaciones de su unidad, registrar planes de acción y cargar evidencias PDF. | Disponible |
| `dti-sso-token` | `DTI` | `DTI` | Administrar usuarios/unidades, configurar notificaciones y ejecutar jobs internos de vencimiento. | Disponible |
| `rectorado-sso-token` | `RECTORADO` | `RECTORADO` | Consultar tablero ejecutivo y exportar matrices. | Disponible |

Para probar el login:

1. Abra la aplicación frontend.
2. Introduzca uno de los tokens disponibles.
3. Use el JWT devuelto por la aplicación para las peticiones protegidas.

Una credencial SSO inválida responde `401 AUTHENTICATION_REQUIRED`.

## Máquina de estados

Flujo principal:

```text
PENDIENTE
    │ Registrar plan de acción
    ▼
EN_PROCESO
    │ Cargar evidencia PDF y notificar cumplimiento
    ▼
EN_VALIDACION
    ├── Dictamen aprobado por UAI ─────► CUMPLIDA
    └── Dictamen rechazado por UAI ────► EN_PROCESO
```

Reapertura:

```text
CUMPLIDA ─ Hallazgo y reapertura UAI (PATCH, con motivo) ─► REABIERTA
REABIERTA ─ Nuevo plan por EJECUTOR ──────────────────────► EN_PROCESO
```

Vencimiento (indicador, no estado): una recomendación está **vencida** cuando no
está `CUMPLIDA`, ya pasó su fecha de vencimiento legal y no tiene una evidencia
entregada a tiempo pendiente de dictamen. El estado de cumplimiento no cambia:
puede estar `EN_PROCESO` y vencida, y cumplirse tarde. El job de plazos registra
y notifica el vencimiento una sola vez (`vencimiento_registrado_en`).

Reglas:

- `PENDIENTE`: la UAI registra la recomendación; el Ejecutor debe crear el
  plan de acción.
- `EN_PROCESO`: el Ejecutor puede avanzar y adjuntar una evidencia PDF válida.
- `EN_VALIDACION`: la UAI revisa la evidencia; el Ejecutor no puede aprobar su
  propio cumplimiento.
- `CUMPLIDA`: solo se alcanza con dictamen aprobado y evidencia validada.
- Vencida: con el plazo legal vencido, los nuevos hitos deben tener fecha de hoy
  en adelante; la API expone `vencida` y el filtro `?vencida=true|false`.
- `REABIERTA`: la UAI puede reabrir una recomendación cumplida cuando exista
  un hallazgo que lo justifique.
- Toda transición no definida por la máquina de estados debe rechazarse.

## Guía de usuario

### Auditor UAI

1. Inicie sesión con `uai-sso-token`.
2. En **Recomendaciones**, complete el número del informe, período y fecha de
   notificación.
3. Adjunte el **Informe CGE** usando el selector de archivo PDF.
4. Seleccione la **Unidad responsable** en el menú desplegable.
5. Complete número, descripción, prioridad y fecha de vencimiento.
6. Guarde el formulario. La recomendación se crea en `PENDIENTE` y la lista se
   actualiza sin recargar la página.
7. En **Revisión de evidencias**, seleccione una recomendación en
   `EN_VALIDACION`.
8. Abra o descargue la evidencia, revise su tipo, estado y hash SHA-256.
9. Seleccione la evidencia y emita **Aprobar** o **Rechazar**. Al rechazar,
   registre observaciones claras.
10. Consulte **Auditoría** o exporte la matriz cuando necesite verificar la
    trazabilidad o reportar resultados.

### Ejecutor DEP-A

1. Inicie sesión con `ejecutor-sso-token`.
2. En **Planes de acción**, seleccione una recomendación de `DEP-A`.
3. En estado `PENDIENTE`, registre la descripción del hito y la fecha de
   compromiso.
4. Cuando la recomendación esté `EN_PROCESO`, seleccione un archivo PDF de
   evidencia de hasta 30 MB.
5. Elija el tipo de evidencia, si la pantalla lo solicita, y espere el mensaje
   de carga exitosa.
6. La lista se actualiza automáticamente y la recomendación pasa a revisión
   de la UAI.
7. Si la recomendación está en `EN_VALIDACION`, `CUMPLIDA` o en otro estado no
   editable, los controles aparecen deshabilitados con una explicación.
8. Una evidencia rechazada permite corregir el avance cuando la recomendación
   vuelva a `EN_PROCESO`.

Las notificaciones de éxito o error se cierran automáticamente después de
cuatro segundos; también pueden cerrarse con el botón **X**.

## Comandos estándar de Git

Consulte la rama actual y el estado de trabajo:

```bash
git branch --show-current
git status
```

Crear o cambiar a una rama de trabajo:

```bash
git switch -c feature/nombre-del-cambio
```

Añadir cambios:

```bash
git add README.md
git add .
```

Revisar lo que se va a confirmar y crear el commit:

```bash
git diff --cached
git commit -m "docs: actualizar documentación oficial de SITRA-CGE"
```

Publicar la rama:

```bash
git push -u origin feature/nombre-del-cambio
```

Para una rama ya existente:

```bash
git switch feature/nombre-del-cambio
git add .
git commit -m "tipo: descripción breve del cambio"
git push
```

Antes de fusionar a `develop` o `main`, abra un Pull Request y solicite la
revisión de otra persona del equipo.

## Pruebas y comandos de calidad

Backend:

```bash
python -m pytest backend/tests -q
```

Frontend:

```bash
cd frontend
npm test -- --run
npm run build
npm run lint
```
