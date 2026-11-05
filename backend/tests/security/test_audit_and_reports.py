def test_consulta_auditoria_solo_autorizados_y_sin_modificacion():
    from backend.core.audit.audit_repository import AuditRepository

    try:
        AuditRepository.forbid_modification()
        assert False
    except PermissionError:
        assert True
