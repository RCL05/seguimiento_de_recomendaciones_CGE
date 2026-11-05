def validate_recommendation_payload(payload: dict) -> dict:
    required = ("number", "description", "unit_id", "legal_days", "due_date")
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise ValueError(f"Campos obligatorios ausentes: {', '.join(missing)}.")
    legal_days = int(payload["legal_days"])
    if legal_days <= 0:
        raise ValueError("El plazo legal debe ser mayor que cero.")
    return {**payload, "legal_days": legal_days}
