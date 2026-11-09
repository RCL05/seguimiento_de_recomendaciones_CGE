"""La bitácora de auditoría solo admite INSERT; UPDATE y DELETE deben fallar."""

import pytest

from backend.core.audit.models import AuditLog

pytestmark = pytest.mark.django_db


def _registro() -> AuditLog:
    return AuditLog.objects.create(modulo="api", accion="TEST", entidad="recomendacion")


def test_no_permite_actualizar_por_queryset():
    log = _registro()
    with pytest.raises(TypeError):
        AuditLog.objects.filter(pk=log.pk).update(resultado="ALTERADO")
    with pytest.raises(TypeError):
        AuditLog.objects.all().update(resultado="ALTERADO")


def test_no_permite_eliminar_por_queryset():
    log = _registro()
    with pytest.raises(TypeError):
        AuditLog.objects.filter(pk=log.pk).delete()
    with pytest.raises(TypeError):
        log.delete()


def test_no_permite_guardar_una_instancia_existente():
    log = _registro()
    log.resultado = "ALTERADO"
    with pytest.raises(TypeError):
        log.save()
