from uuid import UUID, uuid4


def request_id_from(request) -> UUID:
    value = request.headers.get("X-Request-ID")
    try:
        return UUID(value) if value else uuid4()
    except (ValueError, AttributeError):
        return uuid4()
