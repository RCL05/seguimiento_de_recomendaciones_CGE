| Síntoma | Causa probable | Solución |
|---|---|---|
| `ModuleNotFoundError: No module named 'corsheaders'` (u otro paquete) | `.venv` inactivo o dependencias sin instalar | Activar `.venv` y `python -m pip install -r backend/requirements.txt` |
| `ECONNREFUSED 127.0.0.1:8000` en la consola de Vite | La API no está en ejecución | Iniciar `python manage.py runserver` en `backend/` y comprobar `/health/` |
| `Errno 2 No such file or directory` al iniciar Quart | Se ejecutó desde una carpeta distinta de la raíz | `python docs_server/app.py` desde la raíz |
| `sqlite3.OperationalError: no such column` | Base local desalineada con los modelos | `python manage.py migrate`; en una base descartable, borrar `backend/development.sqlite3`, migrar y volver a sembrar datos |
| `RuntimeError: DJANGO_SECRET_KEY es obligatorio…` | `DJANGO_DEBUG=false` sin clave | Definir `DJANGO_SECRET_KEY` |
| `RuntimeError: JWT_SIGNING_KEY debe tener al menos 32 caracteres` | Clave corta | Usar una clave aleatoria de 32+ caracteres |
| 401 tras reiniciar el backend | Con `DEBUG` y sin `DJANGO_SECRET_KEY` la clave cambia en cada arranque | Definir `JWT_SIGNING_KEY` fija o volver a iniciar sesión |
| 401 "Los permisos del token ya no coinciden…" | La DTI cambió el rol o la unidad del usuario | Iniciar sesión de nuevo |
| El token de desarrollo no funciona | `DJANGO_DEBUG=false` | Es el comportamiento esperado; usar SSO real o `DEBUG=true` en local |
| 404 al consultar una recomendación existente como ejecutor | Pertenece a otra unidad (protección BOLA) | Usar un ejecutor de la unidad responsable |
| 409 "Debe registrar primero el Plan de acción…" al cargar evidencia | Estado `PENDIENTE` | Registrar al menos un hito |
| 409 al emitir dictamen | La recomendación no está `EN_VALIDACION` o ya se dictaminó | Verificar el estado |
| 413 al cargar PDF | Supera `MAX_PDF_SIZE_BYTES` (30 MB) | Reducir el archivo |
| No llegan correos en desarrollo | Sin `EMAIL_HOST`, el backend de correo es la consola | Revisar la salida del servidor o configurar SMTP |
| Notificación en estado `FALLIDA` | Error SMTP transitorio o definitivo; se reintenta en cada ejecución hasta 3 intentos | Corregir SMTP; la alerta interna sigue visible y el job reintenta las fallidas |
| `npm run build` deja cambios en `git status` | Se modifica `frontend/tsconfig.tsbuildinfo` | `git checkout -- frontend/tsconfig.tsbuildinfo` (H-20) |
| PowerShell no permite activar `.venv` | Política de ejecución | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `quarto: command not found` | Quarto no instalado | Instalar desde quarto.org o usar el workflow de GitHub Actions |
