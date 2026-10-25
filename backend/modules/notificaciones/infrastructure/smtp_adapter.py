from __future__ import annotations

import smtplib


class SmtpAdapter:
    def __init__(self, host: str = "localhost", port: int = 25, timeout: int = 10):
        self.host = host
        self.port = port
        self.timeout = timeout

    def send_mail(self, to: str, subject: str, body: str) -> bool:
        try:
            with smtplib.SMTP(self.host, self.port, timeout=self.timeout):
                return True
        except Exception:
            return False
