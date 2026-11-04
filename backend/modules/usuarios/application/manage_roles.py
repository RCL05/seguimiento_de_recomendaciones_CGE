from __future__ import annotations

from uuid import uuid4

from django.db import transaction

from backend.core.audit.repository import record_audit
from backend.core.shared.domain_types import PermissionDenied
from backend.modules.usuarios.models import Usuario


class ManageRolesUseCase:
    @transaction.atomic
    def assign_role(self, *, actor: Usuario, target: Usuario, new_role: str, request_id=None):
        if actor.rol != Usuario.Rol.DTI:
            raise PermissionDenied("Solo DTI puede asignar o revocar roles.")
        old_role = target.rol
        target.rol = new_role
        target.save(update_fields=["rol"])
        record_audit(
            request_id=request_id or uuid4(),
            user=actor,
            action="ASSIGN_ROLE",
            entity="usuario",
            entity_id=target.id,
            previous_state=old_role,
            new_state=new_role,
            details={"target": target.correo_institucional},
            modulo="usuarios",
        )
        return target

    @transaction.atomic
    def revoke_role(self, *, actor: Usuario, target: Usuario, request_id=None):
        if actor.rol != Usuario.Rol.DTI:
            raise PermissionDenied("Solo DTI puede asignar o revocar roles.")
        old_role = target.rol
        target.rol = Usuario.Rol.EJECUTOR
        target.save(update_fields=["rol"])
        record_audit(
            request_id=request_id or uuid4(),
            user=actor,
            action="REVOKE_ROLE",
            entity="usuario",
            entity_id=target.id,
            previous_state=old_role,
            new_state=target.rol,
            modulo="usuarios",
        )
        return target
