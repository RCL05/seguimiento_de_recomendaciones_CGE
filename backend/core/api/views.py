import json
import uuid
from datetime import date
from uuid import UUID

from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from backend.core.api.error_catalog import error_response
from backend.core.api.request_context import request_id_from
from backend.core.api.response_envelope import build_envelope
from backend.core.audit.repository import record_audit
from backend.core.shared.domain_types import (
    DomainError,
    NotFoundError,
    Role,
    User,
    to_dict,
)
from backend.modules.informes_cge.application.register_informe import RegisterInforme  # noqa: F401
from backend.modules.recomendaciones.application.create_recomendacion import CreateRecomendacion
from backend.modules.recomendaciones.application.create_plan_accion import CreatePlanAccion
from backend.modules.recomendaciones.application.upload_evidencia import UploadEvidencia
from backend.modules.recomendaciones.application.issue_dictamen import IssueDictamen
from backend.modules.recomendaciones.models import InformeCGE, Recomendacion
from backend.modules.usuarios.models import UnidadOrganica, Usuario
from backend.modules.usuarios.infrastructure.sso_adapter import SsoAdapter


def _json(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError as error:
        raise DomainError("El cuerpo debe ser JSON válido.") from error


def _user(request, default_role=Role.UAI):
    role = request.headers.get("X-Role", default_role.value)
    unit = request.headers.get("X-Unit-ID", "unit-a")
    try:
        return User(request.headers.get("X-User-ID", "demo-user"), Role(role), unit)
    except ValueError as error:
        raise DomainError("El rol indicado no es válido.") from error


def _persistent_user(request, default_role=Role.UAI) -> tuple[User, Usuario]:
    user = _user(request, default_role)
    user_id = uuid.uuid5(uuid.NAMESPACE_URL, f"sitra-user:{user.id}")
    unit_id = uuid.uuid5(uuid.NAMESPACE_URL, f"sitra-unit:{user.unit_id}") if user.unit_id else None
    unit = None
    if unit_id:
        unit, _ = UnidadOrganica.objects.get_or_create(
            id=unit_id,
            defaults={"codigo": str(user.unit_id), "nombre": str(user.unit_id)},
        )
    actor, _ = Usuario.objects.get_or_create(
        id=user_id,
        defaults={
            "correo_institucional": f"{user.id}@unl.edu.ec",
            "nombres": user.id,
            "rol": user.role.value,
            "unidad_org": unit,
        },
    )
    changed = []
    if actor.rol != user.role.value:
        actor.rol = user.role.value
        changed.append("rol")
    if actor.unidad_org_id != (unit.id if unit else None):
        actor.unidad_org = unit
        changed.append("unidad_org")
    if changed:
        actor.save(update_fields=changed)
    return user, actor


def _audit_denied(request, actor, entity_id, reason):
    record_audit(
        request_id=request_id_from(request),
        user=actor,
        action="ACCESS_DENIED",
        entity="recommendation",
        entity_id=entity_id,
        details={"reason": reason, "result": "not_found"},
        resultado="DENIED",
        ip_address=request.META.get("REMOTE_ADDR"),
    )


def _report_for(payload, actor):
    report_id = payload.get("report_id")
    if report_id:
        return InformeCGE.objects.get(pk=report_id)
    report, _ = InformeCGE.objects.get_or_create(
        numero_informe="DEMO-API",
        defaults={
            "periodo_auditado": "2026",
            "fecha_notificacion": "2026-01-01",
            "pdf_informe_url": "https://example.test/demo.pdf",
            "creado_por": actor,
        },
    )
    return report


def _recommendation_data(recommendation):
    return {
        "id": str(recommendation.id),
        "report_id": str(recommendation.informe_id),
        "number": recommendation.numero_recomendacion,
        "description": recommendation.descripcion,
        "unit_id": recommendation.unidad_responsable.codigo,
        "legal_days": recommendation.plazo_legal_dias,
        "due_date": str(recommendation.fecha_vencimiento_legal),
        "state": recommendation.estado,
    }


def _evidence_data(evidence):
    return {
        "id": str(evidence.id),
        "recommendation_id": str(evidence.recomendacion_id),
        "filename": evidence.nombre_archivo,
        "mime_type": evidence.mime_type,
        "size_bytes": evidence.tamano_bytes,
        "sha256": evidence.hash_sha256,
        "uploaded_at": evidence.fecha_carga.isoformat(),
        "validated": evidence.validada,
    }


def _response(request, data, message, status=200):
    return JsonResponse(
        build_envelope(
            success=True,
            message=message,
            data=to_dict(data),
            request_id=request_id_from(request),
        ),
        status=status,
    )


def _error(request, error):
    envelope, status = error_response(error, request_id_from(request))
    return JsonResponse(envelope, status=status)


def health(request):
    return _response(request, {"status": "ok"}, "Servicio disponible")


@csrf_exempt
def login_sso(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Método no permitido."}, status=405)
    try:
        payload = _json(request)
        identity = SsoAdapter().authenticate(token=payload.get("credential", ""))
        if not identity:
            raise DomainError("La credencial SSO no es válida.")
        return _response(
            request,
            {
                "user_id": identity["correo"],
                "email": identity["correo"],
                "display_name": identity["nombres"],
                "role": identity["rol"],
                "unit_id": identity["unidad_codigo"],
            },
            "Identidad institucional validada",
        )
    except (DomainError, ValueError) as error:
        return _error(request, error if isinstance(error, DomainError) else DomainError(str(error)))


def recommendation_list(request):
    if request.method == "POST":
        return recommendation_create(request)
    if request.method != "GET":
        return JsonResponse({"detail": "Método no permitido."}, status=405)
    recommendations = Recomendacion.objects.select_related(
        "informe", "unidad_responsable"
    ).order_by("-creada_en")
    user, _ = _persistent_user(request)
    if user.role is Role.EJECUTOR:
        recommendations = recommendations.filter(unidad_responsable__codigo=user.unit_id)
    return _response(
        request,
        [_recommendation_data(item) for item in recommendations],
        "Recomendaciones consultadas",
    )


@csrf_exempt
def recommendation_create(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Método no permitido."}, status=405)
    try:
        payload = _json(request)
        user, actor = _persistent_user(request)
        if user.role is not Role.UAI:
            raise DomainError("Solo el rol UAI puede crear recomendaciones.")

        use_case = CreateRecomendacion()
        recommendation = use_case.execute(
            actor=actor,
            request_id=request_id_from(request),
            report_id=payload.get("report_id"),
            number=payload.get("number", ""),
            description=payload.get("description", ""),
            unit_id=payload.get("unit_id", ""),
            legal_days=int(payload.get("legal_days", 0)),
            due_date=date.fromisoformat(payload["due_date"]) if payload.get("due_date") else None,
            priority=payload.get("priority", "MEDIA"),
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return _response(request, _recommendation_data(recommendation), "Recomendación creada", 201)
    except (DomainError, KeyError, TypeError, ValueError, IntegrityError) as error:
        return _error(request, error if isinstance(error, DomainError) else DomainError("Datos de recomendación inválidos."))


@csrf_exempt
def report_create(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Método no permitido."}, status=405)
    try:
        payload = _json(request)
        required = ("numero_informe", "periodo_auditado", "fecha_notificacion", "pdf_informe_url")
        if any(not payload.get(field) for field in required):
            raise DomainError("El informe requiere número, período, fecha y documento oficial.")
        _, actor = _persistent_user(request)
        created = InformeCGE.objects.create(
            numero_informe=str(payload["numero_informe"]),
            periodo_auditado=str(payload["periodo_auditado"]),
            fecha_notificacion=str(payload["fecha_notificacion"]),
            pdf_informe_url=str(payload["pdf_informe_url"]),
            creado_por=actor,
        )
        report = {
            "id": str(created.id),
            "numero_informe": created.numero_informe,
            "periodo_auditado": created.periodo_auditado,
            "fecha_notificacion": str(created.fecha_notificacion),
            "pdf_informe_url": created.pdf_informe_url,
        }
        return _response(request, report, "Informe CGE registrado", 201)
    except (DomainError, TypeError, ValueError, IntegrityError) as error:
        return _error(request, error if isinstance(error, DomainError) else DomainError("Datos de informe inválidos."))


@csrf_exempt
def recommendation_plan(request, recommendation_id: UUID):
    if request.method != "POST":
        return JsonResponse({"detail": "Método no permitido."}, status=405)
    try:
        payload = _json(request)
        _, actor = _persistent_user(request, Role.EJECUTOR)
        use_case = CreatePlanAccion()
        plan_model = use_case.execute(
            actor=actor,
            request_id=request_id_from(request),
            recommendation_id=recommendation_id,
            description=payload.get("descripcion_hito", ""),
            commitment_date=(
                date.fromisoformat(payload["fecha_compromiso"])
                if payload.get("fecha_compromiso") else None
            ),
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return _response(request, {
            "id": str(plan_model.id),
            "recommendation_id": str(recommendation_id),
            "descripcion_hito": plan_model.descripcion_hito,
            "fecha_compromiso": str(plan_model.fecha_compromiso),
            "completado": plan_model.completado,
            "created_by": str(actor.id),
        }, "Plan de acción creado", 201)
    except (DomainError, KeyError, TypeError, ValueError) as error:
        return _error(request, error if isinstance(error, DomainError) else DomainError("Datos de plan inválidos."))


def recommendation_detail(request, recommendation_id: UUID):
    recommendation = Recomendacion.objects.select_related("unidad_responsable").filter(pk=recommendation_id).first()
    if recommendation is None:
        return JsonResponse(
            build_envelope(
                success=False,
                message="La recomendación no existe.",
                errors={"code": "RESOURCE_NOT_FOUND"},
                request_id=request_id_from(request),
            ),
            status=404,
        )
    user, _ = _persistent_user(request)
    if user.role is Role.EJECUTOR and user.unit_id != recommendation.unidad_responsable.codigo:
        _, actor = _persistent_user(request)
        _audit_denied(request, actor, recommendation.id, "different_unit")
        return JsonResponse(
            build_envelope(
                success=False,
                message="La recomendación no existe.",
                errors={"code": "RESOURCE_NOT_FOUND"},
                request_id=request_id_from(request),
            ),
            status=404,
        )
    data = _recommendation_data(recommendation)
    data["evidencias"] = [
        _evidence_data(evidence)
        for evidence in recommendation.evidencias.order_by("-fecha_carga")
    ]
    return _response(request, data, "Recomendación consultada")


@csrf_exempt
def recommendation_evidence(request, recommendation_id: UUID):
    if request.method != "POST":
        return JsonResponse({"detail": "Método no permitido."}, status=405)
    try:
        _, actor = _persistent_user(request, Role.EJECUTOR)
        filename = request.headers.get("X-Filename", "evidence.pdf")
        content = request.body
        use_case = UploadEvidencia()
        evidence = use_case.execute(
            actor=actor,
            request_id=request_id_from(request),
            recommendation_id=recommendation_id,
            filename=filename,
            content=content,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return _response(
            request,
            {
                "id": str(evidence.id),
                "recommendation_id": str(evidence.recomendacion_id),
                "filename": evidence.nombre_archivo,
                "sha256": evidence.hash_sha256,
                "uploaded_by": str(evidence.subido_por_id),
                "validated": evidence.validada,
            },
            "Evidencia cargada",
            201,
        )
    except (DomainError, Recomendacion.DoesNotExist) as error:
        return _error(request, error if isinstance(error, DomainError) else NotFoundError("La recomendación no existe."))


@csrf_exempt
def recommendation_review(request, recommendation_id: UUID):
    if request.method != "PATCH":
        return JsonResponse({"detail": "Método no permitido."}, status=405)
    try:
        payload = _json(request)
        user, actor = _persistent_user(request)
        if user.role is not Role.UAI:
            raise DomainError("Solo el rol UAI puede emitir dictámenes.")
        use_case = IssueDictamen()
        dictamen = use_case.execute(
            actor=actor,
            request_id=request_id_from(request),
            recommendation_id=recommendation_id,
            evidence_id=UUID(payload["evidence_id"]),
            approved=bool(payload["approved"]),
            observations=payload.get("observaciones", ""),
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        recommendation = dictamen.recomendacion
        return _response(request, _recommendation_data(recommendation), "Dictamen registrado")
    except (DomainError, KeyError, ValueError, Recomendacion.DoesNotExist) as error:
        return _error(request, error if isinstance(error, DomainError) else DomainError("El dictamen requiere evidence_id y approved."))
