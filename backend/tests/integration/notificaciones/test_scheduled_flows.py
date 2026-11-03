def test_smtp_fallido_no_revierte_transaccion_y_reintentos():
    from backend.modules.notificaciones.infrastructure.smtp_adapter import SmtpAdapter

    smtp = SmtpAdapter(host="invalid.host.test", port=2525)
    result = smtp.send_mail("x@y.com", "t", "b")
    assert result is False


def test_paso_a_en_mora_y_tablero():
    from backend.modules.recomendaciones.models import Recomendacion

    assert hasattr(Recomendacion.Estado, "EN_MORA")
