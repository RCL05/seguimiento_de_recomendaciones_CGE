from __future__ import annotations

from uuid import uuid4

from django.db import transaction

from backend.core.audit.repository import record_audit
from backend.core.shared.domain_types import PermissionDenied
from backend.modules.usuarios.models import UnidadOrganica, Usuario


class ManageUnitsUseCase:
    @transaction.atomic
    def create_or_update_unit(
        self,
        *,
        actor: Usuario,
        codigo: str,
        nombre: str,
        padre_id=None,
        request_id=None,
    ):
        if actor.rol != Usuario.Rol.DTI:
            raise PermissionDenied("Solo DTI puede gestionar unidades.")
        unit, created = UnidadOrganica.objects.get_or_create(
            codigo=codigo,
            defaults={"nombre": nombre},
        )
        if not created:
            unit.nombre = nombre
            if padre_id:
                unit.padre_id = padre_id
            unit.save(update_fields=["nombre", "padre_id"] if padre_id else ["nombre"])
        record_audit(
            request_id=request_id or uuid4(),
            user=actor,
            action="MANAGE_UNIT",
            entity="unidad_organica",
            entity_id=unit.id,
            details={"created": created},
            modulo="usuarios",
        )
        return unit

    @transaction.atomic
    def reassign_user(
        self,
        *,
        actor: Usuario,
        target: Usuario,
        unidad: UnidadOrganica,
        request_id=None,
    ):
        if actor.rol != Usuario.Rol.DTI:
            raise PermissionDenied("Solo DTI puede reasignar usuarios.")
        old_unit = str(target.unidad_org_id) if target.unidad_org_id else None
        target.unidad_org = unidad
        target.save(update_fields=["unidad_org"])
        record_audit(
            request_id=request_id or uuid4(),
            user=actor,
            action="REASSIGN_USER",
            entity="usuario",
            entity_id=target.id,
            details={"old_unit": old_unit, "new_unit": str(unidad.id)},
            modulo="usuarios",
        )
        return target
