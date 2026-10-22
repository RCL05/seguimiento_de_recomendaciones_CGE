import json
import uuid
from uuid import UUID
from uuid import uuid4

from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from backend.core.api.error_catalog import error_response
from backend.core.api.request_context import request_id_from
from backend.core.api.response_envelope import build_envelope
from backend.core.audit.repository import record_audit
from backend.core.shared.domain_types import (
    ConflictError,
    DomainError,
    NotFoundError,
    RecommendationState,
    Role,
    User,
    to_dict,
)
from backend.modules.recomendaciones.application.service import RecommendationService
from backend.modules.recomendaciones.infrastructure.storage import EvidenceStorage
from backend.modules.recomendaciones.models import DictamenUAI, Evidencia, InformeCGE, PlanAccion, Recomendacion
from backend.modules.usuarios.models import UnidadOrganica, Usuario
from backend.modules.usuarios.infrastructure.sso_adapter import SsoAdapter
from backend.modules.recomendaciones.domain.state_machine import transition

service = RecommendationService()
reports: dict[str, dict] = {}


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
        identity = SsoAdapter().authenticate(payload.get("credential"))
        return _response(
            request,
            {"user_id": identity.subject, "email": identity.email, "display_name": identity.display_name},
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
            raise DomainError("El rol no puede crear recomendaciones.")
        unit = UnidadOrganica.objects.get(codigo=payload["unit_id"])
        with transaction.atomic():
            recommendation = Recomendacion.objects.create(
                informe=_report_for(payload, actor),
                numero_recomendacion=payload["number"],
                descripcion=payload["description"],
                unidad_responsable=unit,
                plazo_legal_dias=int(payload["legal_days"]),
                fecha_vencimiento_legal=payload["due_date"],
            )
            record_audit(
                request_id=request_id_from(request),
                user=actor,
                action="CREATE",
                entity="recommendation",
                entity_id=recommendation.id,
                new_state=recommendation.estado,
            )
        return _response(request, _recommendation_data(recommendation), "Recomendación creada", 201)
    except (
        DomainError,
        KeyError,
        TypeError,
        ValueError,
        UnidadOrganica.DoesNotExist,
        InformeCGE.DoesNotExist,
        IntegrityError,
    ) as error:
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
        user, actor = _persistent_user(request, Role.EJECUTOR)
        with transaction.atomic():
            recommendation = Recomendacion.objects.select_for_update().select_related(
                "unidad_responsable"
            ).get(pk=recommendation_id)
            if user.unit_id != recommendation.unidad_responsable.codigo:
                _audit_denied(request, actor, recommendation.id, "different_unit")
                raise NotFoundError("La recomendación no existe.")
            description = payload.get("descripcion_hito")
            commitment_date = payload.get("fecha_compromiso")
            if not description or not commitment_date:
                raise DomainError("El hito requiere descripción y fecha de compromiso.")
            if recommendation.estado == Recomendacion.Estado.PENDIENTE:
                recommendation.estado = Recomendacion.Estado.EN_PLANIFICACION
            if recommendation.estado != Recomendacion.Estado.EN_PLANIFICACION:
                raise ConflictError("La recomendación no acepta planes en su estado actual.")
            previous_state = recommendation.estado
            recommendation.estado = Recomendacion.Estado.EN_EJECUCION
            plan_model = PlanAccion.objects.create(
                recomendacion=recommendation,
                descripcion_hito=description,
                fecha_compromiso=commitment_date,
                creado_por=actor,
            )
            recommendation.save(update_fields=["estado"])
            record_audit(
                request_id=request_id_from(request),
                user=actor,
                action="CREATE_PLAN",
                entity="recommendation",
                entity_id=recommendation.id,
                previous_state=previous_state,
                new_state=recommendation.estado,
            )
        return _response(request, {
            "id": str(plan_model.id),
            "recommendation_id": str(recommendation_id),
            "descripcion_hito": plan_model.descripcion_hito,
            "fecha_compromiso": str(plan_model.fecha_compromiso),
            "completado": plan_model.completado,
            "created_by": str(actor.id),
        }, "Plan de acción creado", 201)
    except Recomendacion.DoesNotExist:
        raise NotFoundError("La recomendación no existe.")
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
    return _response(request, _recommendation_data(recommendation), "Recomendación consultada")


@csrf_exempt
def recommendation_evidence(request, recommendation_id: UUID):
    if request.method != "POST":
        return JsonResponse({"detail": "Método no permitido."}, status=405)
    try:
        user, actor = _persistent_user(request, Role.EJECUTOR)
        filename = request.headers.get("X-Filename", "evidence.pdf")
        content = request.body
        digest = validate_pdf(filename, content)
        with transaction.atomic():
            recommendation = Recomendacion.objects.select_for_update().select_related(
                "unidad_responsable"
            ).get(pk=recommendation_id)
            if user.unit_id != recommendation.unidad_responsable.codigo:
                _audit_denied(request, actor, recommendation.id, "different_unit")
                raise NotFoundError("La recomendación no existe.")
            if recommendation.estado not in {
                Recomendacion.Estado.EN_EJECUCION,
                Recomendacion.Estado.RECHAZADA_CORRECCION,
            }:
                raise ConflictError("La recomendación no acepta evidencias en su estado actual.")
            evidence_id = uuid4()
            storage_url, _ = EvidenceStorage().save(evidence_id, filename, content)
            evidence = Evidencia.objects.create(
                id=evidence_id,
                recomendacion=recommendation,
                nombre_archivo=filename,
                mime_type="application/pdf",
                tamano_bytes=len(content),
                url_almacenamiento=storage_url,
                hash_sha256=digest,
                subido_por=actor,
            )
            previous_state = recommendation.estado
            recommendation.estado = Recomendacion.Estado.EN_REVISION_INTERNA
            recommendation.save(update_fields=["estado"])
            record_audit(
                request_id=request_id_from(request),
                user=actor,
                action="UPLOAD_EVIDENCE",
                entity="recommendation",
                entity_id=recommendation.id,
                previous_state=previous_state,
                new_state=recommendation.estado,
                details={"evidence_id": str(evidence.id), "sha256": digest},
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
        _, actor = _persistent_user(request)
        with transaction.atomic():
            recommendation = Recomendacion.objects.select_for_update().get(pk=recommendation_id)
            evidence = Evidencia.objects.filter(
                pk=payload["evidence_id"], recomendacion=recommendation
            ).first()
            if evidence is None:
                raise ValidationError("La evidencia no pertenece a la recomendación.")
            if recommendation.estado != Recomendacion.Estado.EN_REVISION_INTERNA:
                raise ConflictError("La recomendación no está lista para dictamen.")
            approved = bool(payload["approved"])
            previous_state = recommendation.estado
            if approved:
                evidence.validada = True
                evidence.save(update_fields=["validada"])
                recommendation.estado = Recomendacion.Estado.CUMPLIDA
            else:
                recommendation.estado = Recomendacion.Estado.RECHAZADA_CORRECCION
            dictamen = DictamenUAI.objects.create(
                recomendacion=recommendation,
                evidencia=evidence,
                evaluador=actor,
                resultado=(
                    DictamenUAI.Resultado.APROBADO
                    if approved else DictamenUAI.Resultado.RECHAZADO
                ),
                observaciones_oficiales=payload.get("observaciones", ""),
            )
            recommendation.save(update_fields=["estado"])
            record_audit(
                request_id=request_id_from(request),
                user=actor,
                action="ISSUE_DICTAMEN",
                entity="recommendation",
                entity_id=recommendation.id,
                previous_state=previous_state,
                new_state=recommendation.estado,
                details={"dictamen_id": str(dictamen.id), "approved": approved},
            )
        return _response(request, _recommendation_data(recommendation), "Dictamen registrado")
    except (DomainError, KeyError, Recomendacion.DoesNotExist) as error:
        return _error(request, error if isinstance(error, DomainError) else DomainError("El dictamen requiere evidence_id y approved."))
