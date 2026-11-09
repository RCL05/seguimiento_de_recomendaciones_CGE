"""Crea datos mínimos para ejecutar SITRA-CGE en desarrollo local."""
import os
import sys
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import django

django.setup()

from modules.usuarios.models import UnidadOrganica, Usuario


UNITS = {
    "UAI": "Auditoría Interna",
    "DEP-A": "Departamento A",
    "DTI": "Dirección de Tecnologías de la Información",
    "RECTORADO": "Rectorado",
}

USERS = (
    ("uai@unl.edu.ec", "Usuario UAI", Usuario.Rol.UAI, "UAI"),
    ("ejecutor@unl.edu.ec", "Usuario Ejecutor", Usuario.Rol.EJECUTOR, "DEP-A"),
    ("dti@unl.edu.ec", "Usuario DTI", Usuario.Rol.DTI, "DTI"),
    ("rectorado@unl.edu.ec", "Usuario Rectorado", Usuario.Rol.RECTORADO, "RECTORADO"),
)


def main() -> None:
    units = {
        code: UnidadOrganica.objects.update_or_create(
            codigo=code,
            defaults={"nombre": name, "activo": True},
        )[0]
        for code, name in UNITS.items()
    }

    for email, name, role, unit_code in USERS:
        Usuario.objects.update_or_create(
            correo_institucional=email,
            defaults={
                "nombres": name,
                "rol": role,
                "unidad_org": units[unit_code],
                "activo": True,
            },
        )

    print(f"Datos iniciales listos: {len(units)} unidades y {len(USERS)} usuarios.")


if __name__ == "__main__":
    main()
