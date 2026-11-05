from datetime import date


def validate_informe_payload(payload: dict) -> dict:
    required = ("numero_informe", "periodo_auditado", "fecha_notificacion", "pdf_informe_url")
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise ValueError(f"Campos obligatorios ausentes: {', '.join(missing)}.")
    return {
        "number": str(payload["numero_informe"]),
        "audited_period": str(payload["periodo_auditado"]),
        "notification_date": date.fromisoformat(str(payload["fecha_notificacion"])),
        "document_url": str(payload["pdf_informe_url"]),
    }
