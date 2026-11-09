from __future__ import annotations

import smtplib
from email.message import EmailMessage

from django.conf import settings


class SmtpAdapter:
    """Adaptador SMTP que envía correo real usando la configuración EMAIL_*.

    Los fallos de conexión o autenticación se reportan como ``False`` para que
    el caso de uso pueda reintentar sin revertir la transacción de negocio.
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        timeout: int | None = None,
        use_tls: bool | None = None,
    ):
        self.host = host or getattr(settings, "EMAIL_HOST", "") or "localhost"
        self.port = port or getattr(settings, "EMAIL_PORT", 25)
        self.timeout = timeout or getattr(settings, "EMAIL_TIMEOUT", 10)
        self.use_tls = (
            getattr(settings, "EMAIL_USE_TLS", False) if use_tls is None else use_tls
        )
        self.username = getattr(settings, "EMAIL_HOST_USER", "")
        self.password = getattr(settings, "EMAIL_HOST_PASSWORD", "")

    def send_mail(self, to: str, subject: str, body: str) -> bool:
        message = EmailMessage()
        message["From"] = getattr(
            settings, "DEFAULT_FROM_EMAIL", "SITRA-CGE <no-reply@unl.edu.ec>"
        )
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)
        try:
            with smtplib.SMTP(self.host, self.port, timeout=self.timeout) as server:
                if self.use_tls:
                    server.starttls()
                if self.username:
                    server.login(self.username, self.password)
                server.send_message(message)
            return True
        except Exception:
            return False
