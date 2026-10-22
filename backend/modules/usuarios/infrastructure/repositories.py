from uuid import UUID

from django.db import transaction

from backend.modules.usuarios.models import UnidadOrganica, Usuario


class UserRepository:
    def get(self, user_id: UUID) -> Usuario | None:
        return Usuario.objects.select_related("unidad_org").filter(pk=user_id).first()

    def get_by_email(self, email: str) -> Usuario | None:
        return Usuario.objects.select_related("unidad_org").filter(
            correo_institucional=email
        ).first()

    def list_active_by_unit(self, unit_id: UUID) -> list[Usuario]:
        return list(
            Usuario.objects.filter(unidad_org_id=unit_id, activo=True).order_by("nombres")
        )

    @transaction.atomic
    def save(self, user: Usuario) -> Usuario:
        user.save()
        return user


class OrganizationalUnitRepository:
    def get(self, unit_id: UUID) -> UnidadOrganica | None:
        return UnidadOrganica.objects.filter(pk=unit_id).first()

    def list_children(self, parent_id: UUID | None) -> list[UnidadOrganica]:
        return list(
            UnidadOrganica.objects.filter(padre_id=parent_id, activo=True).order_by("codigo")
        )
