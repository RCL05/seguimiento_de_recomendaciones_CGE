from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Iterable, List, Protocol

from .models import Recomendacion, Usuario


class SemaforoColor(str, Enum):
    VERDE = "verde"
    AMARILLO = "amarillo"
    ROJO = "rojo"
    NEGRO = "negro"


@dataclass(frozen=True)
class AlertaPlazo:
    recomendacion_id: int
    dias_restantes: int
    color: SemaforoColor
    mensaje: str


class EmailGateway(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...


class NotificationEngine:
    def __init__(self, email_gateway: EmailGateway) -> None:
        self._email_gateway = email_gateway

    @staticmethod
    def dias_restantes(hoy: date, fecha_maxima_cumplimiento: date) -> int:
        return (fecha_maxima_cumplimiento - hoy).days

    @classmethod
    def semaforo(cls, hoy: date, fecha_maxima_cumplimiento: date) -> SemaforoColor:
        dias = cls.dias_restantes(hoy, fecha_maxima_cumplimiento)
        if dias < 0:
            return SemaforoColor.NEGRO
        if dias < 15:
            return SemaforoColor.ROJO
        if dias <= 30:
            return SemaforoColor.AMARILLO
        return SemaforoColor.VERDE

    def generar_alerta(self, recomendacion: Recomendacion, hoy: date) -> AlertaPlazo:
        dias = self.dias_restantes(hoy, recomendacion.fecha_maxima_cumplimiento)
        color = self.semaforo(hoy, recomendacion.fecha_maxima_cumplimiento)
        if color is SemaforoColor.NEGRO:
            mensaje = "Recomendación vencida"
        else:
            mensaje = f"Restan {dias} días para el cumplimiento"
        return AlertaPlazo(
            recomendacion_id=recomendacion.id,
            dias_restantes=dias,
            color=color,
            mensaje=mensaje,
        )

    def notificar(
        self,
        recomendaciones: Iterable[Recomendacion],
        destinatarios: Iterable[Usuario],
        hoy: date,
    ) -> List[AlertaPlazo]:
        alertas: List[AlertaPlazo] = []
        for recomendacion in recomendaciones:
            alerta = self.generar_alerta(recomendacion, hoy)
            alertas.append(alerta)
            subject = (
                f"[CGE][{alerta.color.value.upper()}] "
                f"Recomendación {recomendacion.numero_recomendacion}"
            )
            body = (
                f"Estado de plazo: {alerta.color.value}. "
                f"{alerta.mensaje}. Fecha máxima: "
                f"{recomendacion.fecha_maxima_cumplimiento.isoformat()}."
            )
            for destinatario in destinatarios:
                self._email_gateway.send(destinatario.correo, subject, body)

        return alertas
