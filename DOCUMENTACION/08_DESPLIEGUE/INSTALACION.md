## Opción A — Instalación local (verificada)

Todos los comandos parten de la raíz del repositorio.

### 1. Clonar

```bash
git clone https://github.com/RCL05/seguimiento_de_recomendaciones_CGE.git
cd seguimiento_de_recomendaciones_CGE
```

### 2. Entorno virtual de Python

```powershell
# Windows PowerShell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt pytest pytest-django
python -m pip install -r docs_server/requirements.txt   # opcional: servidor Quart
cd frontend && npm ci && cd ..
```

### 4. Variables de entorno locales

El backend usa `DJANGO_DEBUG=false` por defecto y exige `DJANGO_SECRET_KEY` en ese caso. Para desarrollo:

```powershell
# Windows PowerShell
$env:DJANGO_DEBUG="true"
$env:DJANGO_SECRET_KEY="development-only-change-me-0123456789"
```

```bash
# macOS / Linux
export DJANGO_DEBUG=true
export DJANGO_SECRET_KEY=development-only-change-me-0123456789
```

`backend/.env.example` documenta el resto de variables (PostgreSQL, SMTP, SSO).

### 5. Base de datos y datos iniciales

```bash
cd backend
python manage.py migrate
python scripts/seed_initial_data.py
cd ..
```

Sin `POSTGRES_DB` se crea `backend/development.sqlite3`. El script de datos es idempotente: crea las unidades `UAI`, `DEP-A`, `DTI`, `RECTORADO` y los usuarios de prueba.

### 6. Almacenamiento de evidencias

El directorio `backend/media/evidencias/` se crea automáticamente en la primera carga (`EvidenceStorage.save_stream` usa `mkdir(parents=True)`). Crearlo a mano es opcional.

### 7. Comprobación

```bash
cd backend && python manage.py check && python -m pytest -q
```

Resultado esperado: `System check identified no issues` y `231 passed`.

## Opción B — Docker Compose (no verificada en esta auditoría)

```bash
docker compose up --build
```

Levanta `db` (PostgreSQL 16), `backend` (aplica migraciones y arranca con Gunicorn en :8000), `scheduler` (evaluación de plazos cada hora) y `frontend` (Vite en :5173). Para los datos iniciales:

```bash
docker compose exec backend python scripts/seed_initial_data.py
```

Los valores por defecto de contraseñas y claves en `docker-compose.yml` son solo para desarrollo; defínalos en un archivo `.env` en la raíz para cualquier otro uso.
