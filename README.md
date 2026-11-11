# SITRA-CGE UNL

Sistema para registrar, asignar, dar seguimiento y mantener la trazabilidad de
las recomendaciones emitidas por la Contraloría General del Estado (CGE) para
la Universidad Nacional de Loja (UNL).

## Arquitectura resumida

- **Backend:** Django 5, Django REST Framework, JWT y SQLite para desarrollo.
- **Frontend:** React, TypeScript y Vite.
- **Documentación:** Swagger UI en Django y servidor Quart para la documentación
  Markdown y el diagrama de arquitectura C4.
- **Evidencias:** archivos PDF almacenados en `backend/media/evidencias/`.
- **Autenticación local:** tokens SSO simulados que devuelven un JWT de
  desarrollo.

La documentación técnica ampliada se encuentra en [`docs/`](docs/) y la
arquitectura en [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md).

## Requisitos previos

Instale las siguientes herramientas:

- Python **3.10 o superior**
- Node.js **18 o superior** y npm
- Git

Los comandos de esta guía se muestran para Windows PowerShell y bash. Todas las
rutas relativas parten de la raíz del repositorio.

## Instalación y configuración del entorno

### 1. Clonar el repositorio

```bash
git clone https://github.com/RCL05/seguimiento_de_recomendaciones_CGE.git
cd seguimiento_de_recomendaciones_CGE
```

### 2. Crear y activar `.venv` en la raíz

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Compruebe que el entorno está activo antes de continuar:

```bash
python --version
python -m pip install --upgrade pip
```

### 3. Instalar dependencias del backend y documentación

```bash
python -m pip install -r backend/requirements.txt
python -m pip install django-cors-headers drf-spectacular quart markdown
```

`django-cors-headers` y `drf-spectacular` también están declarados en los
requisitos del backend; el segundo comando deja explícitas las dependencias
necesarias para CORS, Swagger y el servidor Quart.

### 4. Ejecutar migraciones Django

Ejecute ambos comandos desde `backend/`:

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
cd ..
```

`makemigrations` no debería generar cambios en un clon limpio. Si genera una
migración porque se modificaron modelos localmente, revísela antes de
confirmarla.

### 5. Poblar datos iniciales

El script crea de forma idempotente las unidades `UAI`, `DEP-A`, `DTI` y
`RECTORADO`, además de los usuarios de prueba. Ejecútelo desde `backend/`:

```bash
cd backend
python scripts/seed_initial_data.py
cd ..
```

Los usuarios se pueden volver a crear sin duplicados. El adaptador SSO de
desarrollo también puede completar la identidad al iniciar sesión por primera
vez.

### 6. Crear el almacenamiento de evidencias

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force backend\media\evidencias
```

macOS/Linux:

```bash
mkdir -p backend/media/evidencias
```

### 7. Instalar dependencias del frontend

```bash
cd frontend
npm install
cd ..
```

## Guía de ejecución del sistema

Inicie los tres procesos en **tres terminales independientes**. En cada
terminal active `.venv` antes de ejecutar el comando Python.

### Terminal 1: Backend Django — puerto 8000

Desde la raíz del proyecto:

```bash
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
cd backend
python manage.py runserver
```

En macOS/Linux, active con `source .venv/bin/activate` y use el mismo comando
`python manage.py runserver`.

### Terminal 2: Servidor Quart de documentación — puerto 8001

**Debe ejecutarse estrictamente desde la raíz del proyecto**, no desde
`backend/`, `frontend/` ni `docs_server/`:

```bash
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
python docs_server/app.py
```

El servidor busca los archivos Markdown en `docs/` relativo a la raíz del
repositorio.

### Terminal 3: Frontend React — puerto 5173

```bash
cd frontend
npm run dev
```

### Evaluación periódica de plazos (opcional)

Las alertas de vencimiento y el registro de mora se ejecutan con un comando
idempotente. Desde la raíz y con `.venv` activo:

```bash
python backend/manage.py evaluar_plazos
```

En producción puede programarse con cron o con el servicio `scheduler` de
`docker-compose.yml` (frecuencia en `SCHEDULER_INTERVAL_SECONDS`). El endpoint
manual equivalente es `POST /api/v1/evaluaciones-plazos` (solo DTI).

## Puntos de acceso

| Servicio | URL |
|---|---|
| Frontend Web | [http://localhost:5173/](http://localhost:5173/) |
| Swagger UI API Docs | [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/) |
| Servidor de Arquitectura C4 Quart | [http://localhost:8001/](http://localhost:8001/) |
| Django Admin | [http://localhost:8000/admin/](http://localhost:8000/admin/) |
| Health check | [http://localhost:8000/health/](http://localhost:8000/health/) |

## Credenciales y tokens SSO de prueba

Con `DJANGO_DEBUG=true` (valor predeterminado local), use estos tokens en la
pantalla de inicio de sesión:

| Token SSO | Rol | Unidad | Uso |
|---|---|---|---|
| `uai-sso-token` | UAI — Auditor | UAI | Registrar recomendaciones, revisar evidencias, dictaminar y consultar auditoría |
| `ejecutor-sso-token` | EJECUTOR | DEP-A | Gestionar planes de acción y cargar evidencias |
| `dti-sso-token` | DTI — Admin | DTI | Administrar usuarios, unidades, configuración y notificaciones |
| `rectorado-sso-token` | RECTORADO — Autoridad | RECTORADO | Consultar indicadores y reportes institucionales |

Estos tokens son únicamente para desarrollo. La aplicación los intercambia por
un JWT temporal; no los envíe como encabezado `Authorization`.

## Máquina de estados y secuencia de recomendaciones

Flujo principal:

```text
PENDIENTE
    │ La UAI registra la recomendación
    ▼
EN_PROCESO
    │ El Ejecutor registra hitos y carga evidencia PDF
    ▼
EN_VALIDACION
    ├── UAI aprueba el dictamen ──► CUMPLIDA
    └── UAI rechaza el dictamen ──► EN_PROCESO
```

Reglas:

1. **PENDIENTE:** la recomendación existe, pero el Ejecutor debe registrar el
   plan de acción.
2. **EN_PROCESO:** la unidad responsable puede registrar hitos y cargar
   evidencia PDF válida.
3. **EN_VALIDACION:** la evidencia espera revisión de la UAI; el Ejecutor no
   puede aprobar su propio cumplimiento.
4. **CUMPLIDA:** solo se alcanza con evidencia validada y dictamen aprobado por
   la UAI.
5. Una evidencia rechazada devuelve la recomendación a `EN_PROCESO`.
6. La UAI puede reabrir una recomendación cumplida por un hallazgo justificado:
   `CUMPLIDA -> REABIERTA -> EN_PROCESO`.
7. El vencimiento es un indicador independiente del estado. Una recomendación
   puede estar `EN_PROCESO` y vencida; el estado no cambia automáticamente.
8. Toda transición no definida por estas reglas debe ser rechazada por la API.

## Solución de problemas comunes

### `ModuleNotFoundError: No module named 'corsheaders'`

El entorno virtual no tiene instaladas todas las dependencias o no está
activo. Desde la raíz:

```bash
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
python -m pip install -r backend/requirements.txt
python -m pip install django-cors-headers drf-spectacular quart markdown
```

Reinicie el servidor Django después de instalar.

### `ECONNREFUSED 127.0.0.1:8000` en Vite

El frontend no puede conectarse al backend. Verifique que la Terminal 1 siga
ejecutando `python manage.py runserver` dentro de `backend/` y que la URL
`http://localhost:8000/health/` responda. Después recargue el frontend.

### `Errno 2 No such file or directory` al iniciar Quart

Quart se inició desde una carpeta incorrecta o no encuentra la documentación.
Detenga el proceso y ejecútelo estrictamente desde la raíz:

```bash
python docs_server/app.py
```

Compruebe que la ruta actual contiene las carpetas `docs/` y `docs_server/`.

### `sqlite3.OperationalError: no such column`

La base de datos no está alineada con los modelos actuales. Desde `backend/`:

```bash
python manage.py makemigrations
python manage.py migrate
```

Si el error persiste en una instalación local descartable, detenga Django,
elimine únicamente `backend/development.sqlite3`, vuelva a ejecutar las
migraciones y el script de datos iniciales. No haga esto con una base de datos
que contenga información real.

## Pruebas y calidad

Frontend:

```bash
cd frontend
npm test
npm run lint
npm run build
```

Backend (con `.venv` activo, desde la raíz):

```bash
python -m pytest backend -q
```

La integración continua definida en `.github/workflows/ci.yml` ejecuta
`manage.py check`, la suite de pytest, el lint, las pruebas y el build del
frontend en cada push y pull request.

## Estructura principal

```text
backend/      API Django, modelos, migraciones y almacenamiento local
frontend/     Aplicación React + TypeScript + Vite
docs/         Documentación técnica, ADR y arquitectura
docs_server/  Servidor Quart para visualizar Markdown
```
