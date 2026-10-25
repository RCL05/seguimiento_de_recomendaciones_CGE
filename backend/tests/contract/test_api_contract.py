def test_contract_envoltorio_exitoso_y_error():
    from backend.core.api.response_envelope import build_envelope

    ok = build_envelope(success=True, message="ok", data={"id": "1"})
    err = build_envelope(success=False, message="bad", errors={"code": "VALIDATION_ERROR"})
    assert ok["success"] is True and ok["errors"] is None
    assert err["success"] is False and err["data"] is None
    assert err["errors"]["code"] == "VALIDATION_ERROR"
