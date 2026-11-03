from __future__ import annotations


class SsoAdapter:
    def authenticate(self, *, token: str) -> dict:
        # Simulado para entorno de pruebas
        if token == "valid-sso-token":
            return {
                "correo": "uai@unl.edu.ec",
                "nombres": "Auditoría Interna",
                "rol": "UAI",
                "unidad_codigo": "UAI",
            }
        if token == "dti-sso-token":
            return {
                "correo": "dti@unl.edu.ec",
                "nombres": "DTI",
                "rol": "DTI",
                "unidad_codigo": "DTI",
            }
        return {}
