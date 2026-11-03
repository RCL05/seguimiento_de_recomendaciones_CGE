from __future__ import annotations

from abc import ABC, abstractmethod


class SsoPort(ABC):
    @abstractmethod
    def authenticate(self, *, token: str) -> dict:
        raise NotImplementedError
