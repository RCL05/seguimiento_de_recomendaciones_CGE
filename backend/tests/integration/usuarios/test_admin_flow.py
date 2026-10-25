def test_sso_simulado_y_administracion_dti():
    from backend.modules.usuarios.infrastructure.sso_adapter import SsoAdapter

    sso = SsoAdapter()
    assert sso.authenticate(token="valid-sso-token")["rol"] == "UAI"
    assert sso.authenticate(token="dti-sso-token")["rol"] == "DTI"
    assert sso.authenticate(token="bad") == {}
