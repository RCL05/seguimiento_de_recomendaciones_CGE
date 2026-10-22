from ..shared.domain_types import AuditEvent


class AuditLog:
    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def record(self, event: AuditEvent) -> None:
        self._events.append(event)

    def all(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events)
