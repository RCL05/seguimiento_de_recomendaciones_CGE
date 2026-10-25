import os
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

MIME_PDF = "application/pdf"
TAMANO_MAXIMO_BYTES = 10 * 1024 * 1024
FIRMA_PDF = b"%PDF-"


def validar_archivo_pdf(archivo):
    if archivo is None:
        raise ValidationError("Debe adjuntar un archivo de evidencia.")

    if archivo.size > TAMANO_MAXIMO_BYTES:
        limite_mb = TAMANO_MAXIMO_BYTES // (1024 * 1024)
        raise ValidationError(f"El archivo supera el tamaño máximo permitido ({limite_mb} MB).")

    nombre = (archivo.name or "").lower()
    if not nombre.endswith(".pdf"):
        raise ValidationError("El formato admitido es PDF (.pdf).")

    if getattr(archivo, "content_type", None) not in (MIME_PDF, "application/x-pdf", None):
        raise ValidationError("El tipo MIME del archivo no corresponde a un PDF.")

    posicion_inicial = archivo.tell() if hasattr(archivo, "tell") else None
    cabecera = archivo.read(5)
    if posicion_inicial is not None:
        archivo.seek(posicion_inicial)

    if cabecera != FIRMA_PDF:
        raise ValidationError("El archivo no contiene una cabecera PDF válida.")


@deconstructible
class RutaEvidenciaPDF:
    def __call__(self, instancia, filename):
        extension = os.path.splitext(filename)[1].lower() or ".pdf"
        return os.path.join("evidencias", f"{uuid4().hex}{extension}")
