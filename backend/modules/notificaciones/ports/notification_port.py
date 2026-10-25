from __future__ import annotations

from abc import ABC, abstractmethod


class NotificationPort(ABC):
    @abstractmethod
    def send_internal(self, *, destinatario_id, tipo: str, contenido: dict, clave_idempotencia: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def send_email(self, *, to: str, subject: str, body: str) -> bool:
        raise NotImplementedError
