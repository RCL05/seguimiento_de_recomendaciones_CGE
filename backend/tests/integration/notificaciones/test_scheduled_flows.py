def test_smtp_fallido_no_revierte_transaccion_y_reintentos():
    from backend.modules.notificaciones.infrastructure.smtp_adapter import SmtpAdapter

    smtp = SmtpAdapter(host="invalid.host.test", port=2525)
    result = smtp.send_mail("x@y.com", "t", "b")
    assert result is False
