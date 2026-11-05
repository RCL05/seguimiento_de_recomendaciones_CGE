from __future__ import annotations

from datetime import datetime, timezone


def run_scheduled_evaluations():
    now = datetime.now(timezone.utc)
    return {"evaluated_at": now.isoformat(), "status": "ok"}
