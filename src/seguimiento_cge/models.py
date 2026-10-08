from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import Enum
from typing import Optional


class Rol(str, Enum):
    ADMINISTRADOR = "administrador"
    MAXIMA_AUTORIDAD = "maxima_autoridad"
    RESPONSABLE_EJECUTOR = "responsable_ejecutor"
    CONSULTOR_OBSERVADOR = "consultor_observador"


class EstadoRecomendacion(str, Enum):
    REGISTRADA = "registrada"
    EN_PLANIFICACION = "en_planificacion"
    EN_EJECUCION = "en_ejecucion"
    EN_REVISION_UAI = "en_revision_uai"
    CERRADA = "cerrada"
    NO_APLICABLE = "no_aplicable"


@dataclass(frozen=True)
class Usuario:
    id: int
    nombre: str
    correo: str
    rol: Rol


@dataclass
class InformeCGE:
    id: int
    numero_informe: str
    titulo_examen: str
    fecha_emision: date
    periodo_auditado: str
    unidad_auditada: str


@dataclass
class Recomendacion:
    id: int
    informe_id: int
    numero_recomendacion: str
    descripcion_texto: str
    estado_actual: EstadoRecomendacion
    fecha_maxima_cumplimiento: date


@dataclass
class PlanAccion:
    id: int
    recomendacion_id: int
    descripcion_accion: str
    responsable_usuario_id: int
    fecha_inicio: date
    fecha_fin: date
    es_no_aplicable: bool = False


@dataclass
class MedioVerificacion:
    id: int
    plan_accion_id: int
    tipo_documento: str
    ruta_archivo_pdf: str
    fecha_carga: datetime
    valido_uai: bool = False


@dataclass
class HistorialAuditoria:
    id: int
    entidad_afectada: str
    registro_id: int
    usuario_id: int
    accion_realizada: str
    valor_anterior: Optional[str]
    valor_nuevo: Optional[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
