from __future__ import annotations

from functools import wraps
from uuid import uuid4

from django.db import transaction

from backend.core.audit.repository import record_audit


class AuditInterceptor:
    @staticmethod
    def intercept(action: str, entity: str, module: str = "api"):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                request = kwargs.get("request") or (args[0] if args else None)
                user = kwargs.get("actor") or kwargs.get("user")
                request_id = kwargs.get("request_id") or uuid4()
                ip_address = getattr(request, "META", {}).get("REMOTE_ADDR") if request else None
                with transaction.atomic():
                    result = func(*args, **kwargs)
                    record_audit(
                        request_id=request_id,
                        user=user,
                        action=action,
                        entity=entity,
                        entity_id=None,
                        details={"func": func.__name__},
                        ip_address=ip_address,
                        modulo=module,
                    )
                    return result

            return wrapper

        return decorator
