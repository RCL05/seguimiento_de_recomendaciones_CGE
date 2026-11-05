import json
from functools import wraps
from datetime import date
from uuid import UUID

from django.db import IntegrityError
from django.http import FileResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from backend.core.api.error_catalog import error_response
from backend.core.api.request_context import request_id_from
from backend.core.api.response_envelope import build_envelope
from backend.core.shared.domain_types import (
    AuthenticationRequired,
    DomainError,
    NotFoundError,
    PayloadTooLarge,
    PermissionDenied,
    Role,
    User,
    ValidationError,
    to_dict,
)
from backend.modules.informes_cge.application.register_informe import RegisterInforme
from backend.modules.recomendaciones.application.create_recomendacion import CreateRecomendacion
from backend.modules.recomendaciones.application.get_recomendacion import GetRecomendacion
from backend.modules.recomendaciones.application.list_recomendaciones import ListRecomendaciones
from backend.modules.recomendaciones.application.create_plan_accion import CreatePlanAccion
from backend.modules.recomendaciones.application.upload_evidencia import (
    MAX_SIZE_BYTES,
    UploadEvidencia,
)
from backend.modules.recomendaciones.application.issue_dictamen import IssueDictamen
from backend.modules.evidencias.application.anular_evidencia import AnularEvidencia
from backend.modules.evidencias.application.get_evidence_file import GetEvidenceFile
from backend.modules.usuarios.application.list_units import ListUnits
from backend.modules.recomendaciones.models import Recomendacion
from backend.modules.usuarios.models import UnidadOrganica, Usuario
from backend.modules.usuarios.infrastructure.sso_adapter import SsoAdapter


def _json(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError as error:
        raise ValidationError("El cuerpo debe ser JSON válido.") from error


def _request_chunks(request, chunk_size: int = 64 * 1024):
    while True:
        chunk = request.read(chunk_size)
        if not chunk:
            return
        yield chunk


def _user(request):
    authorization = request.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AuthenticationRequired("Se requiere un token Bearer válido.")
    identity = SsoAdapter().validate_session(token)
    if not identity or not identity.get("user_id"):
        raise AuthenticationRequired("El token de sesión no es válido o expiró.")
    actor = Usuario.objects.select_related("unidad_org").filter(
        pk=identity["user_id"],
        correo_institucional=identity["correo"],
        activo=True,
    ).first()
    if actor is None:
        raise AuthenticationRequired("La identidad no está habilitada en el sistema.")
    try:
        role = Role(identity["rol"])
    except ValueError as error:
        raise AuthenticationRequired("El rol registrado no es válido.") from error
    unit_id = identity.get("unidad_codigo")
    current_unit_id = actor.unidad_org.codigo if actor.unidad_org_id else None
    if actor.rol != role.value or current_unit_id != unit_id:
        raise AuthenticationRequired("Los permisos del token ya no coinciden con la cuenta activa.")
    return User(str(identity["user_id"]), role, unit_id)

def _persistent_user(request) -> tuple[User, Usuario]:
    user = _user(request)
    actor = Usuario.objects.select_related("unidad_org").get(pk=user.id, activo=True)
    return user, actor

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
        "type": evidence.tipo,
        "status": evidence.estado,
    }


def _response(request, data, message, status=200, pagination=None, location=None):
    response = JsonResponse(
        build_envelope(
            success=True,
            message=message,
            data=to_dict(data),
            request_id=request_id_from(request),
            pagination=pagination,
        ),
        status=status,
    )
    if location:
        # RFC 9110 §10.2.2: en 201 Created, Location identifica el recurso creado.
        response["Location"] = location
    return response


def _error(request, error):
    envelope, status = error_response(error, request_id_from(request))
    return JsonResponse(envelope, status=status)


def bearer_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        try:
            _user(request)
        except DomainError as error:
            envelope, _ = error_response(error, request_id_from(request))
            return JsonResponse(envelope, status=401)
        return view(request, *args, **kwargs)
    return wrapped

@require_http_methods(["GET", "HEAD"])
def health(request):
    return _response(request, {"status": "ok"}, "Servicio disponible")


@require_http_methods(["GET"])
@bearer_required
def units_list(request):
    try:
        _, actor = _persistent_user(request)
        units = ListUnits().execute(actor=actor)
        return _response(
            request,
            [{"id": str(unit.id), "codigo": unit.codigo, "nombre": unit.nombre} for unit in units],
            "Catálogo de unidades consultado",
        )
    except DomainError as error:
        return _error(request, error)


@require_http_methods(["POST"])
def login_sso(request):
    try:
        payload = _json(request)
        identity = SsoAdapter().authenticate(token=payload.get("credential", ""))
        if not identity:
            raise AuthenticationRequired("La credencial SSO no es válida.")
        actor, _ = Usuario.objects.get_or_create(
            correo_institucional=identity["correo"],
            defaults={
                "nombres": identity["nombres"],
                "rol": identity["rol"],
                "activo": True,
            },
        )
        if not actor.activo:
            raise AuthenticationRequired("La identidad no está habilitada en el sistema.")
        if actor.unidad_org_id is None and identity.get("unidad_codigo"):
            unit, _ = UnidadOrganica.objects.get_or_create(codigo=identity["unidad_codigo"], defaults={"nombre": identity["unidad_codigo"]})
            actor.unidad_org = unit
            actor.save(update_fields=["unidad_org"])
        session_token = SsoAdapter().issue_session(
            {
                "user_id": str(actor.id),
                "email": actor.correo_institucional,
                "role": actor.rol,
                "unit_id": actor.unidad_org.codigo if actor.unidad_org_id else None,
            }
        )
        return _response(
            request,
            {
                "access_token": session_token,
                "token_type": "Bearer",
                "expires_in": SsoAdapter.token_ttl_seconds,
                "user_id": str(actor.id),
                "email": identity["correo"],
                "display_name": identity["nombres"],
                "role": actor.rol,
                "unit_id": actor.unidad_org.codigo if actor.unidad_org_id else None,
            },
            "Identidad institucional validada",
        )
    except (DomainError, ValueError) as error:
        return _error(request, error if isinstance(error, DomainError) else ValidationError(str(error)))


@require_http_methods(["GET", "POST"])
@bearer_required
def recommendation_list(request):
    if request.method == "POST":
        return recommendation_create(request)
    try:
        try:
            page_number = int(request.GET.get("page", "1"))
            page_size = int(request.GET.get("page_size", "25"))
        except ValueError as error:
            raise ValidationError("page y page_size deben ser números enteros.") from error
        _, actor = _persistent_user(request)
        result_page = ListRecomendaciones().execute(
            actor=actor,
            page=page_number,
            page_size=page_size,
            state=request.GET.get("state") or request.GET.get("estado"),
            unit_code=request.GET.get("unit_id") or request.GET.get("unidad_id"),
            priority=request.GET.get("priority") or request.GET.get("prioridad"),
            due_date=request.GET.get("due_date") or request.GET.get("fecha_vencimiento"),
            due_before=request.GET.get("due_before") or request.GET.get("fecha_vencimiento_hasta"),
            due_after=request.GET.get("due_after") or request.GET.get("fecha_vencimiento_desde"),
        )
        return _response(
            request,
            [_recommendation_data(item) for item in result_page.object_list],
            "Recommendations retrieved",
            pagination={
                "page": result_page.number,
                "page_size": result_page.paginator.per_page,
                "total": result_page.paginator.count,
                "total_pages": result_page.paginator.num_pages,
                "has_next": result_page.has_next(),
                "has_previous": result_page.has_previous(),
            },
        )
    except DomainError as error:
        return _error(request, error)


def recommendation_create(request):
    """Rama POST de recommendation_list (ya autenticada y con método validado)."""
    try:
        payload = _json(request)
        user, actor = _persistent_user(request)
        if user.role is not Role.UAI:
            raise PermissionDenied("Solo el rol UAI puede crear recomendaciones.")

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
        return _response(
            request,
            _recommendation_data(recommendation),
            "Recomendación creada",
            201,
            location=reverse("recommendation-detail", args=[recommendation.id]),
        )
    except (DomainError, KeyError, TypeError, ValueError, IntegrityError) as error:
        return _error(request, error if isinstance(error, DomainError) else ValidationError("Datos de recomendación inválidos."))


@require_http_methods(["POST"])
@bearer_required
def report_create(request):
    try:
        is_multipart = request.content_type.startswith("multipart/form-data")
        payload = request.POST if is_multipart else _json(request)
        report_file = request.FILES.get("pdf_informe") if is_multipart else None
        required = ("numero_informe", "periodo_auditado", "fecha_notificacion")
        if any(not payload.get(field) for field in required):
            raise ValidationError("El informe requiere número, período y fecha de notificación.")
        document_url = str(payload.get("pdf_informe_url", ""))
        if not document_url and report_file is None:
            raise ValidationError("Adjunte el PDF oficial o proporcione su URL.")
        if report_file is not None:
            if not report_file.name.lower().endswith(".pdf") or report_file.content_type != "application/pdf":
                raise ValidationError("El documento oficial debe ser un archivo PDF.")
            if report_file.size > MAX_SIZE_BYTES:
                raise PayloadTooLarge("El PDF supera el tamaño máximo permitido.")
            signature = report_file.read(5)
            report_file.seek(0)
            if not signature.startswith(b"%PDF-"):
                raise ValidationError("El contenido no corresponde a un documento PDF.")
        user, actor = _persistent_user(request)
        if user.role is not Role.UAI:
            raise PermissionDenied("Solo el rol UAI puede registrar informes.")
        created = RegisterInforme().execute(
            number=str(payload["numero_informe"]),
            audited_period=str(payload["periodo_auditado"]),
            notification_date=date.fromisoformat(payload["fecha_notificacion"]),
            document_url=document_url,
            document_file=report_file,
            creator=actor,
        )
        report = {
            "id": str(created.id),
            "numero_informe": created.numero_informe,
            "periodo_auditado": created.periodo_auditado,
            "fecha_notificacion": str(created.fecha_notificacion),
            "pdf_informe_url": created.pdf_informe.url if created.pdf_informe else created.pdf_informe_url,
        }
        return _response(request, report, "Informe CGE registrado", 201)
    except (DomainError, TypeError, ValueError, IntegrityError) as error:
        return _error(request, error if isinstance(error, DomainError) else ValidationError("Datos de informe inválidos."))


@require_http_methods(["POST"])
@bearer_required
def recommendation_plan(request, recommendation_id: UUID):
    try:
        payload = _json(request)
        user, actor = _persistent_user(request)
        if user.role is not Role.EJECUTOR:
            raise PermissionDenied("Solo el rol EJECUTOR puede crear planes de acción.")
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
        return _error(request, error if isinstance(error, DomainError) else ValidationError("Datos de plan inválidos."))


@require_http_methods(["GET", "HEAD"])
@bearer_required
def recommendation_detail(request, recommendation_id: UUID):
    try:
        _, actor = _persistent_user(request)
        recommendation = GetRecomendacion().execute(
            actor=actor,
            recommendation_id=recommendation_id,
            request_id=request_id_from(request),
            ip_address=request.META.get("REMOTE_ADDR"),
        )
    except DomainError as error:
        return _error(request, error)

    data = _recommendation_data(recommendation)
    data["evidencias"] = [
        _evidence_data(evidence) for evidence in recommendation.evidencias.all()
    ]
    return _response(request, data, "Recommendation retrieved")


@require_http_methods(["POST"])
@bearer_required
def recommendation_evidence(request, recommendation_id: UUID):
    content_length = request.headers.get("Content-Length")
    if content_length is not None:
        try:
            content_length_value = int(content_length)
        except ValueError:
            return _error(request, ValidationError("Content-Length invalido."))
        if content_length_value < 0:
            return _error(request, ValidationError("Content-Length invalido."))
        if content_length_value > MAX_SIZE_BYTES:
            return _error(request, PayloadTooLarge("El PDF supera el tamano maximo permitido."))
    try:
        user, actor = _persistent_user(request)
        if user.role is not Role.EJECUTOR:
            raise PermissionDenied("Solo el rol EJECUTOR puede cargar evidencias.")
        filename = request.headers.get("X-Filename", "evidence.pdf")
        content = _request_chunks(request)
        use_case = UploadEvidencia()
        evidence = use_case.execute(
            actor=actor,
            request_id=request_id_from(request),
            recommendation_id=recommendation_id,
            filename=filename,
            content=content,
            evidence_type=request.headers.get("X-Evidence-Type", "BORRADOR").upper(),
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
                "type": evidence.tipo,
                "status": evidence.estado,
            },
            "Evidencia cargada",
            201,
            location=reverse("evidence-file", args=[evidence.id]),
        )
    except (DomainError, Recomendacion.DoesNotExist) as error:
        return _error(request, error if isinstance(error, DomainError) else NotFoundError("La recomendación no existe."))


@require_http_methods(["DELETE"])
@bearer_required
def evidence_annul(request, evidence_id: UUID):
    try:
        user, actor = _persistent_user(request)
        if user.role is not Role.UAI:
            raise PermissionDenied("Solo el rol UAI puede anular evidencias.")
        payload = _json(request)
        evidence = AnularEvidencia().execute(
            actor=actor,
            request_id=request_id_from(request),
            evidence_id=evidence_id,
            reason=str(payload.get("reason", "")),
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return _response(request, _evidence_data(evidence), "Evidencia anulada")
    except (DomainError, Recomendacion.DoesNotExist) as error:
        return _error(request, error if isinstance(error, DomainError) else NotFoundError("La evidencia no existe."))


@require_http_methods(["GET", "HEAD"])
@bearer_required
def evidence_file(request, evidence_id: UUID):
    try:
        _, actor = _persistent_user(request)
        path, filename = GetEvidenceFile().execute(actor=actor, evidence_id=evidence_id)
        disposition = request.GET.get("disposition", "inline")
        if disposition not in {"inline", "attachment"}:
            raise ValidationError("disposition debe ser inline o attachment.")
        return FileResponse(
            path.open("rb"),
            as_attachment=disposition == "attachment",
            filename=filename,
            content_type="application/pdf",
        )
    except DomainError as error:
        return _error(request, error)


@require_http_methods(["PATCH"])
@bearer_required
def recommendation_review(request, recommendation_id: UUID):
    try:
        payload = _json(request)
        user, actor = _persistent_user(request)
        if user.role is not Role.UAI:
            raise PermissionDenied("Solo el rol UAI puede emitir dictámenes.")
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
        return _error(request, error if isinstance(error, DomainError) else ValidationError("El dictamen requiere evidence_id y approved."))
