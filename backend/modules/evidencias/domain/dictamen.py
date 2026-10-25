from enum import Enum

from django.db import models


class ResultadoDictamen(str, Enum):
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"


class DictamenUAI:
    class Resultado(models.TextChoices):
        APROBADO = "APROBADO", "Aprobado"
        RECHAZADO = "RECHAZADO", "Rechazado"
