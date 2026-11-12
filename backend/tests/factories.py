"""Datos de prueba creados directamente con el ORM (sin pasar por la API)."""

from __future__ import annotations

from datetime import timedelta
from itertools import count

from django.utils import timezone

from backend.modules.recomendaciones.models import Evidencia, InformeCGE, Recomendacion
from backend.modules.usuarios.models import UnidadOrganica, Usuario

_secuencia = count(1)


def unidad(codigo: str = "DEP-A") -> UnidadOrganica:
    return UnidadOrganica.objects.get_or_create(codigo=codigo, defaults={"nombre": codigo})[0]


def usuario(rol: str, clave: str, codigo_unidad: str | None = None) -> Usuario:
    return Usuario.objects.get_or_create(
        correo_institucional=f"{clave}@unl.edu.ec",
        defaults={
            "nombres": clave,
            "rol": rol,
            "unidad_org": unidad(codigo_unidad) if codigo_unidad else None,
            "activo": True,
        },
    )[0]


def recomendacion(
    *,
    dias_para_vencer: int = 30,
    estado: str = Recomendacion.Estado.EN_PROCESO,
    codigo_unidad: str = "DEP-A",
) -> Recomendacion:
    n = next(_secuencia)
    informe = InformeCGE.objects.create(
        numero_informe=f"INF-F-{n}",
        periodo_auditado="2026",
        fecha_notificacion=timezone.localdate(),
        pdf_informe_url="https://example.test/inf.pdf",
        creado_por=usuario(Usuario.Rol.UAI, "uai-factory", "UAI"),
    )
    return Recomendacion.objects.create(
        informe=informe,
        numero_recomendacion=f"R-{n}",
        descripcion="Recomendación de prueba",
        prioridad="MEDIA",
        unidad_responsable=unidad(codigo_unidad),
        plazo_legal_dias=max(dias_para_vencer, 1),
        fecha_vencimiento_legal=timezone.localdate() + timedelta(days=dias_para_vencer),
        estado=estado,
    )


def evidencia(rec: Recomendacion, *, validada: bool = False, tipo: str = Evidencia.Tipo.FINAL) -> Evidencia:
    return Evidencia.objects.create(
        recomendacion=rec,
        nombre_archivo="evidencia.pdf",
        tamano_bytes=10,
        url_almacenamiento="https://example.test/evidencia.pdf",
        hash_sha256="a" * 64,
        subido_por=usuario(Usuario.Rol.EJECUTOR, "ejecutor-factory", rec.unidad_responsable.codigo),
        tipo=tipo,
        validada=validada,
    )
