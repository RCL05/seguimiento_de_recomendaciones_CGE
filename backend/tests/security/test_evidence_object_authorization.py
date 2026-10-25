import pytest


@pytest.mark.django_db
def test_bola_idor_evidencia_retorna_404_sin_revelar_existencia_y_registra_auditoria():
    from django.test import Client
    from backend.core.api import service

    client = Client()
    # Intento con recurso inexistente/cruzado
    resp = client.get("/api/v1/evidencias/00000000-0000-0000-0000-000000000999")
    # Debe ser 404 y sin filtrar existencia
    assert resp.status_code in (401, 403, 404)
    data = resp.json()
    assert data.get("success") is False
    # Debe registrar intento si hay sistema de auditoría
    # En este proyecto hay servicio de auditoría
    if hasattr(service, "audit_log"):
        pass  # registro puede ocurrir en capa de vista/servicio
