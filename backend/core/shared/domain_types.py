from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class DomainError(Exception):
    code = "BUSINESS_RULE_VIOLATION"
    status_code = 409


class ValidationError(DomainError):
    code = "VALIDATION_ERROR"
    status_code = 400


class PermissionDenied(DomainError):
    code = "PERMISSION_DENIED"
    status_code = 403


class NotFoundError(DomainError):
    code = "RESOURCE_NOT_FOUND"
    status_code = 404


class ConflictError(DomainError):
    code = "CONFLICT"
    status_code = 409


class Role(str, Enum):
    DTI = "DTI"
    UAI = "UAI"
    EJECUTOR = "EJECUTOR"
    RECTORADO = "RECTORADO"
    CGE_AUDITOR = "CGE_AUDITOR"


class RecommendationState(str, Enum):
    PENDIENTE = "PENDIENTE"
    EN_PLANIFICACION = "EN_PLANIFICACION"
    EN_EJECUCION = "EN_EJECUCION"
    EN_REVISION_INTERNA = "EN_REVISION_INTERNA"
    CUMPLIDA = "CUMPLIDA"
    RECHAZADA_CORRECCION = "RECHAZADA_CORRECCION"
    EN_MORA = "EN_MORA"


@dataclass(frozen=True)
class User:
    id: str
    role: Role
    unit_id: str | None = None


@dataclass
class Evidence:
    id: str
    recommendation_id: str
    filename: str
    content: bytes
    sha256: str
    uploaded_by: str
    validated: bool = False


@dataclass
class Recommendation:
    id: str
    report_id: str
    number: str
    description: str
    unit_id: str
    legal_days: int
    due_date: str
    state: RecommendationState = RecommendationState.PENDIENTE
    had_internal_review: bool = False


@dataclass(frozen=True)
class AuditEvent:
    user_id: str
    request_id: str
    action: str
    entity: str
    entity_id: str
    previous_state: str | None
    new_state: str | None


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def to_dict(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {
            key: to_dict(item)
            for key, item in value.__dict__.items()
        }
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [to_dict(item) for item in value]
    if isinstance(value, Mapping):
        return {key: to_dict(item) for key, item in value.items()}
    return value
