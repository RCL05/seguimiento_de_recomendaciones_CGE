from typing import Protocol

from backend.core.shared.domain_types import AuditEvent


class AuditRepository(Protocol):
    def record(self, event: AuditEvent) -> None:
        ...
