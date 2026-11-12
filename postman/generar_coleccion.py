"""Genera la colección y los entornos de Postman de SITRA-CGE UNL.

Uso:
    python postman/generar_coleccion.py postman
    python postman/generar_coleccion.py postman --ejemplos reporte-newman.json

La segunda forma agrega a cada solicitud la respuesta real obtenida en una ejecución
de newman (`--reporters json --reporter-json-export reporte-newman.json`), como
ejemplo guardado de Postman. Los tokens se ocultan antes de guardarlos.
"""
import argparse
import json
import re
import uuid
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("salida", type=Path)
parser.add_argument("--ejemplos", type=Path, help="Reporte JSON de newman para generar ejemplos de respuesta.")
args = parser.parse_args()
out = args.salida
out.mkdir(parents=True, exist_ok=True)

PDF = "%PDF-1.7\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"
NS = uuid.uuid5(uuid.NAMESPACE_URL, "sitra-cge-unl-postman")
_folder_actual = ""


def js(*lines):
    # Cada script va en su propio bloque: el sandbox de Postman comparte el ámbito
    # entre scripts y un `const` repetido produce un SyntaxError.
    body = [line for block in lines for line in block.strip("\n").split("\n")]
    return ["{"] + ["  " + line for line in body] + ["}"]


def test(*lines):
    return {"listen": "test", "script": {"type": "text/javascript", "exec": js(*lines)}}


def pre(*lines):
    return {"listen": "prerequest", "script": {"type": "text/javascript", "exec": js(*lines)}}


def status(code):
    return f'pm.test("Responde {code}", () => pm.response.to.have.status({code}));'


def url(path, query=None):
    raw = "{{baseUrl}}" + path
    parts = [p for p in path.strip("/").split("/")]
    u = {"raw": raw, "host": ["{{baseUrl}}"], "path": parts}
    if query:
        u["query"] = [{"key": k, "value": v} for k, v in query]
        u["raw"] += "?" + "&".join(f"{k}={v}" for k, v in query)
    return u


def bearer(token):
    if token is None:
        return {"type": "noauth"}
    return {"type": "bearer", "bearer": [{"key": "token", "value": "{{" + token + "}}", "type": "string"}]}


def req(name, method, path, *, token=None, body=None, raw=None, formdata=None, content_type=None,
        accept="application/json", headers=None, query=None, tests=(), prerequest=(), description=""):
    h = [{"key": "Accept", "value": accept}]
    if body is not None:
        h.append({"key": "Content-Type", "value": "application/json"})
    if content_type:
        h.append({"key": "Content-Type", "value": content_type})
    for k, v in (headers or []):
        h.append({"key": k, "value": v})
    request = {"auth": bearer(token), "method": method, "header": h, "url": url(path, query), "description": description}
    if body is not None:
        request["body"] = {"mode": "raw", "raw": json.dumps(body, ensure_ascii=False, indent=2),
                           "options": {"raw": {"language": "json"}}}
    if raw is not None:
        request["body"] = {"mode": "raw", "raw": raw}
    if formdata is not None:
        request["body"] = {"mode": "formdata", "formdata": formdata}
    item = {"id": str(uuid.uuid5(NS, f"{_folder_actual}/{name}")), "name": name, "request": request, "event": []}
    if prerequest:
        item["event"].append(pre(*prerequest))
    if tests:
        item["event"].append(test(*tests))
    return item


def folder(name, description, build):
    global _folder_actual
    _folder_actual = name
    return {"name": name, "description": description, "item": build()}


def login(name, credential, var):
    return req(
        f"Iniciar sesión: {name}", "POST", "/api/v1/sesiones",
        body={"credential": "{{" + credential + "}}"},
        tests=[status(200), f"""
const data = pm.response.json().data;
pm.test("Devuelve un token Bearer", () => pm.expect(data.token_type).to.eql("Bearer"));
pm.environment.set("{var}", data.access_token);
"""],
        description=(
            f"Crea una sesión del rol {name} y guarda el JWT en la variable de entorno `{var}`.\n\n"
            "En desarrollo, la credencial es un token de prueba que solo funciona con `DJANGO_DEBUG=true`. "
            "En preproducción y producción, es la credencial del SSO institucional."
        ),
    )


ENVELOPE = """
const type = pm.response.headers.get("Content-Type") || "";
if (type.includes("application/json")) {
  pm.test("Usa la envoltura universal", () => {
    const body = pm.response.json();
    pm.expect(body).to.include.all.keys("success", "message", "data", "errors", "meta");
    if (body.success) { pm.expect(body.errors).to.eql(null); } else { pm.expect(body.data).to.eql(null); }
  });
}
"""

SETUP = """
// Sufijo único por ejecución para que los números de informe no se repitan.
if (!pm.collectionVariables.get("sufijo")) {
  pm.collectionVariables.set("sufijo", Date.now().toString().slice(-8));
}
const dia = (n) => { const d = new Date(); d.setDate(d.getDate() + n); return d.toISOString().slice(0, 10); };
pm.collectionVariables.set("fecha_hoy", dia(0));
pm.collectionVariables.set("fecha_vencimiento", dia(90));
pm.collectionVariables.set("fecha_hito", dia(30));

// Entorno de solo lectura (producción): no se envía nada que modifique datos.
const escritura = !["GET", "HEAD", "OPTIONS"].includes(pm.request.method);
const esSesion = pm.request.url.getPath().endsWith("/sesiones");
if (pm.environment.get("solo_lectura") === "true" && escritura && !esSesion) {
  console.warn("Omitida por solo_lectura: " + pm.request.method + " " + pm.request.url.getPath());
  pm.execution.skipRequest();
}
"""

TOKEN_VARS = ("token_uai", "token_ejecutor", "token_dti", "token_rectorado")

items = []

items.append(folder("00 Salud y sesión", "Comprueba el servicio y crea una sesión por rol. Los tokens quedan en el entorno activo.", lambda: [
    req("Salud del servicio", "GET", "/health/", tests=[status(200)]),
    login("UAI", "cred_uai", "token_uai"),
    login("Ejecutor (DEP-A)", "cred_ejecutor", "token_ejecutor"),
    login("DTI", "cred_dti", "token_dti"),
    login("Rectorado", "cred_rectorado", "token_rectorado"),
    req("Credencial inválida", "POST", "/api/v1/sesiones", body={"credential": "{{cred_invalida}}"},
        tests=[status(401), """
pm.test("Incluye WWW-Authenticate", () => pm.response.to.have.header("WWW-Authenticate"));
pm.test("Código AUTHENTICATION_REQUIRED", () => pm.expect(pm.response.json().errors.code).to.eql("AUTHENTICATION_REQUIRED"));
"""]),
]))

items.append(folder("01 Administración DTI", "Unidades, usuarios y configuración de notificaciones (rol DTI).", lambda: [
    req("Listar unidades", "GET", "/api/v1/unidades", token="token_dti", tests=[status(200)]),
    req("Registrar unidad destino", "POST", "/api/v1/unidades", token="token_dti",
        body={"codigo": "DEP-PM-{{sufijo}}", "nombre": "Unidad de prueba Postman {{sufijo}}"},
        tests=[status(201), 'pm.collectionVariables.set("unidad_destino", pm.response.json().data.codigo);'],
        description="Unidad a la que luego se reasigna la recomendación."),
    req("Listar usuarios", "GET", "/api/v1/usuarios", token="token_dti", tests=[status(200), """
const ejecutor = pm.response.json().data.find((u) => u.rol === "EJECUTOR" && u.unidad_codigo === "DEP-A");
pm.test("Existe un ejecutor de DEP-A", () => pm.expect(ejecutor).to.be.an("object"));
if (ejecutor) { pm.collectionVariables.set("usuario_ejecutor_id", ejecutor.id); }
"""]),
    req("Asignar rol y unidad a un usuario", "PATCH", "/api/v1/usuarios/{{usuario_ejecutor_id}}", token="token_dti",
        body={"rol": "EJECUTOR", "unidad_codigo": "DEP-A"},
        tests=[status(200), 'pm.test("Conserva la unidad DEP-A", () => pm.expect(pm.response.json().data.unidad_codigo).to.eql("DEP-A"));'],
        description=(
            "El DTI asigna el rol y la unidad orgánica. Se envían los valores actuales del ejecutor para no invalidar "
            "su sesión: un cambio real de rol o de unidad revoca los tokens emitidos antes."
        )),
    req("Consultar configuración de notificaciones", "GET", "/api/v1/notificaciones/configuracion",
        token="token_dti", tests=[status(200)]),
    req("Actualizar configuración de notificaciones", "PUT", "/api/v1/notificaciones/configuracion",
        token="token_dti", body={"umbral_dias": 15, "notificaciones_activas": True},
        tests=[status(200), 'pm.test("Umbral de 15 días", () => pm.expect(pm.response.json().data.umbral_dias).to.eql(15));']),
]))

items.append(folder("02 Flujo de cumplimiento", "Ejecutar en orden: informe → recomendación → hito → evidencia → dictamen.", lambda: [
    req("Registrar informe CGE", "POST", "/api/v1/informes", token="token_uai",
        body={"numero_informe": "DNA-PM-{{sufijo}}", "periodo_auditado": "2025",
              "fecha_notificacion": "{{fecha_hoy}}", "pdf_informe_url": "https://example.test/informe.pdf"},
        tests=[status(201), """
pm.test("Incluye Location", () => pm.response.to.have.header("Location"));
pm.collectionVariables.set("informe_id", pm.response.json().data.id);
"""]),
    req("Registrar informe con PDF adjunto (multipart)", "POST", "/api/v1/informes", token="token_uai",
        formdata=[
            {"key": "numero_informe", "value": "DNA-PM-DOC-{{sufijo}}", "type": "text"},
            {"key": "periodo_auditado", "value": "2025", "type": "text"},
            {"key": "fecha_notificacion", "value": "{{fecha_hoy}}", "type": "text"},
            {"key": "pdf_informe", "type": "file", "src": "archivos/informe-ejemplo.pdf"},
        ],
        tests=[status(201), 'pm.collectionVariables.set("informe_con_pdf_id", pm.response.json().data.id);'],
        description=(
            "Adjunta el documento oficial como `multipart/form-data`. El archivo está en `postman/archivos/`. "
            "En Postman, configure esa carpeta como *Working directory* (Settings → General) o vuelva a elegir el archivo."
        )),
    req("Descargar documento del informe", "GET", "/api/v1/informes/{{informe_con_pdf_id}}/documento", token="token_uai",
        accept="application/pdf",
        tests=[status(200), 'pm.test("Es un PDF", () => pm.expect(pm.response.headers.get("Content-Type")).to.include("application/pdf"));']),
    req("Listar informes", "GET", "/api/v1/informes", token="token_uai", query=[("page", "1"), ("page_size", "10")],
        tests=[status(200), 'pm.test("Incluye paginación", () => pm.expect(pm.response.json().meta.pagination).to.include.keys("page", "total"));']),
    req("Consultar informe", "GET", "/api/v1/informes/{{informe_id}}", token="token_uai", tests=[status(200)]),
    req("Registrar recomendación", "POST", "/api/v1/recomendaciones", token="token_uai",
        body={"report_id": "{{informe_id}}", "number": "R-01", "description": "Actualizar el reglamento interno de bienes.",
              "unit_id": "DEP-A", "legal_days": 90, "due_date": "{{fecha_vencimiento}}", "priority": "ALTA"},
        tests=[status(201), """
const rec = pm.response.json().data;
pm.test("Queda en PENDIENTE", () => pm.expect(rec.state).to.eql("PENDIENTE"));
pm.collectionVariables.set("recomendacion_id", rec.id);
"""]),
    req("Listar recomendaciones filtradas", "GET", "/api/v1/recomendaciones", token="token_uai",
        query=[("state", "PENDIENTE"), ("unit_id", "DEP-A"), ("page", "1"), ("page_size", "25")], tests=[status(200)]),
    req("Consultar recomendación (ejecutor de su unidad)", "GET", "/api/v1/recomendaciones/{{recomendacion_id}}",
        token="token_ejecutor", tests=[status(200)]),
    req("Registrar hito del plan", "POST", "/api/v1/recomendaciones/{{recomendacion_id}}/hitos",
        token="token_ejecutor", body={"descripcion_hito": "Redactar la propuesta de reglamento", "fecha_compromiso": "{{fecha_hito}}"},
        tests=[status(201)]),
    req("Listar hitos", "GET", "/api/v1/recomendaciones/{{recomendacion_id}}/hitos",
        token="token_ejecutor", tests=[status(200)]),
    req("Cargar evidencia BORRADOR", "POST", "/api/v1/recomendaciones/{{recomendacion_id}}/evidencias",
        token="token_ejecutor", raw=PDF, content_type="application/pdf",
        headers=[("X-Filename", "avance.pdf"), ("X-Evidence-Type", "BORRADOR")],
        tests=[status(201), """
const ev = pm.response.json().data;
pm.test("Calcula el SHA-256", () => pm.expect(ev.sha256).to.match(/^[0-9a-f]{64}$/));
pm.collectionVariables.set("evidencia_borrador_id", ev.id);
"""],
        description="El cuerpo es el PDF en binario. En Postman también puede elegir Body → binary y seleccionar un archivo."),
    req("Verificar integridad", "GET", "/api/v1/evidencias/{{evidencia_borrador_id}}/integridad", token="token_uai",
        tests=[status(200), 'pm.test("Archivo íntegro", () => pm.expect(pm.response.json().data.integra).to.eql(true));']),
    req("Aprobar un BORRADOR (rechazado)", "POST", "/api/v1/recomendaciones/{{recomendacion_id}}/dictamenes",
        token="token_uai", body={"evidence_id": "{{evidencia_borrador_id}}", "approved": True},
        tests=[status(409)], description="Solo una evidencia FINAL puede sustentar el cumplimiento."),
    req("Rechazar sin observaciones", "POST", "/api/v1/recomendaciones/{{recomendacion_id}}/dictamenes",
        token="token_uai", body={"evidence_id": "{{evidencia_borrador_id}}", "approved": False},
        tests=[status(400), 'pm.test("Indica el campo observaciones", () => pm.expect(pm.response.json().errors.fields).to.have.property("observaciones"));']),
    req("Rechazar con observaciones", "POST", "/api/v1/recomendaciones/{{recomendacion_id}}/dictamenes",
        token="token_uai", body={"evidence_id": "{{evidencia_borrador_id}}", "approved": False,
                                 "observaciones": "Es un avance; falta la versión firmada."},
        tests=[status(201), """
pm.test("Vuelve a EN_PROCESO", () => pm.expect(pm.response.json().data.recomendacion.state).to.eql("EN_PROCESO"));
pm.test("Location identifica el dictamen", () => pm.expect(pm.response.headers.get("Location")).to.include("/dictamenes/" + pm.response.json().data.id));
pm.collectionVariables.set("dictamen_id", pm.response.json().data.id);
"""]),
    req("Consultar dictamen", "GET", "/api/v1/recomendaciones/{{recomendacion_id}}/dictamenes/{{dictamen_id}}",
        token="token_ejecutor",
        tests=[status(200), 'pm.test("Es el rechazo registrado", () => pm.expect(pm.response.json().data.resultado).to.eql("RECHAZADO"));'],
        description="Recurso que identifica la cabecera Location del POST de dictámenes."),
    req("Cargar evidencia FINAL", "POST", "/api/v1/recomendaciones/{{recomendacion_id}}/evidencias",
        token="token_ejecutor", raw=PDF, content_type="application/pdf",
        headers=[("X-Filename", "reglamento-firmado.pdf"), ("X-Evidence-Type", "FINAL")],
        tests=[status(201), 'pm.collectionVariables.set("evidencia_final_id", pm.response.json().data.id);']),
    req("Descargar archivo de evidencia", "GET", "/api/v1/evidencias/{{evidencia_final_id}}/archivo", token="token_uai",
        accept="application/pdf",
        tests=[status(200), 'pm.test("Es un PDF", () => pm.expect(pm.response.headers.get("Content-Type")).to.include("application/pdf"));']),
    req("Aprobar evidencia FINAL", "POST", "/api/v1/recomendaciones/{{recomendacion_id}}/dictamenes",
        token="token_uai", body={"evidence_id": "{{evidencia_final_id}}", "approved": True},
        tests=[status(201), 'pm.test("Queda CUMPLIDA", () => pm.expect(pm.response.json().data.recomendacion.state).to.eql("CUMPLIDA"));']),
    req("Anular la evidencia que sustenta el cumplimiento (rechazado)", "PATCH", "/api/v1/evidencias/{{evidencia_final_id}}",
        token="token_uai", body={"estado": "ANULADA", "motivo": "Prueba de regla."}, tests=[status(409)]),
    req("Reabrir recomendación", "PATCH", "/api/v1/recomendaciones/{{recomendacion_id}}", token="token_uai",
        body={"estado": "REABIERTA", "motivo": "Hallazgo posterior de la auditoría."},
        tests=[status(200), 'pm.test("Queda REABIERTA", () => pm.expect(pm.response.json().data.state).to.eql("REABIERTA"));']),
    req("Reasignar recomendación", "PATCH", "/api/v1/recomendaciones/{{recomendacion_id}}", token="token_uai",
        body={"unit_id": "{{unidad_destino}}", "motivo": "Cambio de estructura orgánica."},
        tests=[status(200), 'pm.test("Cambia la unidad", () => pm.expect(pm.response.json().data.unit_id).to.eql(pm.collectionVariables.get("unidad_destino")));']),
    req("Consultar auditoría de la recomendación", "GET", "/api/v1/auditoria", token="token_uai",
        query=[("entity", "recomendacion"), ("entity_id", "{{recomendacion_id}}"), ("limit", "50")],
        tests=[status(200)]),
]))

items.append(folder("03 Reportes y notificaciones", "Tablero, KPIs, matriz CGE, preferencias y bandeja.", lambda: [
    req("Tablero ejecutivo (Rectorado)", "GET", "/api/v1/reportes/tablero", token="token_rectorado", tests=[status(200)]),
    req("KPIs (ejecutor, solo su unidad)", "GET", "/api/v1/dashboard/kpis", token="token_ejecutor", tests=[status(200)]),
    req("KPIs institucionales (UAI)", "GET", "/api/v1/dashboard/kpis", token="token_uai", tests=[status(200)]),
    req("Exportar matriz CGE (CSV)", "GET", "/api/v1/reportes/matriz-cge", token="token_uai", accept="text/csv",
        tests=[status(200), 'pm.test("Es CSV", () => pm.expect(pm.response.headers.get("Content-Type")).to.include("text/csv"));']),
    req("Consultar mis preferencias de notificación", "GET", "/api/v1/notificaciones/preferencias", token="token_ejecutor",
        tests=[status(200)]),
    req("Actualizar mis preferencias de notificación", "PUT", "/api/v1/notificaciones/preferencias", token="token_ejecutor",
        body={"preferencias": [
            {"tipo_alerta": "ALERTA_VENCIMIENTO", "notificar_interno": True, "notificar_email": True, "activo": True},
            {"tipo_alerta": "EN_MORA", "notificar_interno": True, "notificar_email": False, "activo": True},
        ]},
        tests=[status(200), """
const mora = pm.response.json().data.preferencias.find((p) => p.tipo_alerta === "EN_MORA");
pm.test("Mora solo por canal interno", () => pm.expect(mora.notificar_email).to.eql(false));
"""],
        description="Cada usuario edita sus propias preferencias. El DTI puede editar las de otro con `usuario_id`."),
    req("Bandeja de notificaciones", "GET", "/api/v1/notificaciones", token="token_ejecutor", tests=[status(200)]),
]))

items.append(folder("04 Errores HTTP", "Casos de error con su código esperado.", lambda: [
    req("401 sin token", "GET", "/api/v1/recomendaciones",
        tests=[status(401), 'pm.test("Incluye WWW-Authenticate", () => pm.response.to.have.header("WWW-Authenticate"));']),
    req("403 ejecutor registra recomendación", "POST", "/api/v1/recomendaciones", token="token_ejecutor",
        body={"report_id": "{{informe_id}}", "number": "R-X", "description": "No permitido.", "unit_id": "DEP-A",
              "legal_days": 30, "due_date": "{{fecha_vencimiento}}"},
        tests=[status(403)]),
    req("400 validación de campos", "POST", "/api/v1/recomendaciones", token="token_uai",
        body={"report_id": "{{informe_id}}", "legal_days": 0},
        tests=[status(400), 'pm.test("Detalla los campos", () => pm.expect(pm.response.json().errors).to.have.property("fields"));']),
    req("400 informe inexistente", "POST", "/api/v1/recomendaciones", token="token_uai",
        body={"report_id": "00000000-0000-0000-0000-000000000000", "number": "R-X", "description": "Sin informe.",
              "unit_id": "DEP-A", "legal_days": 30, "due_date": "{{fecha_vencimiento}}"},
        tests=[status(400), 'pm.test("Señala el campo report_id", () => pm.expect(pm.response.json().errors.fields).to.have.property("report_id"));'],
        description="Una referencia inexistente es un dato de entrada inválido, no un conflicto."),
    req("Preparar: recomendación sin plan", "POST", "/api/v1/recomendaciones", token="token_uai",
        body={"report_id": "{{informe_id}}", "number": "R-SINPLAN-{{sufijo}}", "description": "Aún sin hitos.",
              "unit_id": "DEP-A", "legal_days": 30, "due_date": "{{fecha_vencimiento}}"},
        tests=[status(201), 'pm.collectionVariables.set("recomendacion_sin_plan_id", pm.response.json().data.id);']),
    req("409 evidencia sin plan de acción", "POST", "/api/v1/recomendaciones/{{recomendacion_sin_plan_id}}/evidencias",
        token="token_ejecutor", raw=PDF, content_type="application/pdf",
        headers=[("X-Filename", "prematura.pdf"), ("X-Evidence-Type", "FINAL")],
        tests=[status(409)], description="Pendiente sin plan no admite evidencias, igual que cualquier otro estado distinto de En Proceso."),
    req("404 recomendación inexistente", "GET", "/api/v1/recomendaciones/00000000-0000-0000-0000-000000000000",
        token="token_uai", tests=[status(404)]),
    req("405 método no permitido", "PUT", "/api/v1/recomendaciones/{{recomendacion_id}}", token="token_uai", body={},
        tests=[status(405), 'pm.test("Incluye Allow", () => pm.response.to.have.header("Allow"));']),
    req("409 informe duplicado", "POST", "/api/v1/informes", token="token_uai",
        body={"numero_informe": "DNA-PM-{{sufijo}}", "periodo_auditado": "2025", "fecha_notificacion": "{{fecha_hoy}}",
              "pdf_informe_url": "https://example.test/otro.pdf"},
        tests=[status(409)]),
]))

# ---------------------------------------------------------------------------
# Ejemplos de respuesta a partir de una ejecución real de newman.
# ---------------------------------------------------------------------------
JWT = re.compile(r"eyJ[\w-]+\.[\w-]+\.[\w-]+")


def _cuerpo(response):
    data = bytes(response.get("stream", {}).get("data", []))
    tipo = next((h["value"] for h in response.get("header", []) if h["key"].lower() == "content-type"), "")
    if "pdf" in tipo:
        return "(PDF binario de %d bytes)" % len(data), "text"
    texto = JWT.sub("<jwt>", data.decode("utf-8", errors="replace"))
    if "json" in tipo:
        try:
            return json.dumps(json.loads(texto), ensure_ascii=False, indent=2), "json"
        except ValueError:
            pass
    return texto, "text"


def agregar_ejemplos(reporte):
    ejecuciones = {e["item"]["id"]: e for e in reporte["run"]["executions"] if e.get("response")}
    agregados = 0
    for carpeta in items:
        for item in carpeta["item"]:
            e = ejecuciones.get(item["id"])
            if not e:
                continue
            r = e["response"]
            cuerpo, lenguaje = _cuerpo(r)
            visibles = {"content-type", "location", "www-authenticate", "allow", "content-disposition", "retry-after"}
            item["response"] = [{
                "name": f"{r['code']} {r['status']}",
                "originalRequest": item["request"],
                "status": r["status"],
                "code": r["code"],
                "_postman_previewlanguage": lenguaje,
                "header": [h for h in r.get("header", []) if h["key"].lower() in visibles],
                "body": cuerpo,
            }]
            agregados += 1
    return agregados


ejemplos = 0
if args.ejemplos:
    ejemplos = agregar_ejemplos(json.loads(args.ejemplos.read_text(encoding="utf-8")))

collection = {
    "info": {
        "_postman_id": str(NS),
        "name": "SITRA-CGE UNL API",
        "description": (
            "Colección de la API de seguimiento de recomendaciones de la CGE (UNL), versión `/api/v1`.\n\n"
            "**Uso**\n"
            "1. Importe la colección y el entorno que corresponda (desarrollo, preproducción o producción).\n"
            "2. Ejecute primero `00 Salud y sesión`: guarda los tokens en el entorno activo.\n"
            "3. Ejecute las carpetas en orden con el Collection Runner, o una por una.\n\n"
            "**Autenticación:** JWT Bearer. Cada solicitud usa el token del rol que corresponde (`token_uai`, "
            "`token_ejecutor`, `token_dti`, `token_rectorado`).\n\n"
            "**Respuestas:** envoltura universal `success`, `message`, `data`, `errors` y `meta`. Cada solicitud "
            "incluye un ejemplo de respuesta real.\n\n"
            "**Producción:** el entorno tiene `solo_lectura=true`, así que se omiten las solicitudes que modifican datos."
        ),
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    },
    "auth": {"type": "noauth"},
    "event": [pre(SETUP), test(ENVELOPE)],
    "variable": [{"key": k, "value": ""} for k in (
        "sufijo", "fecha_hoy", "fecha_vencimiento", "fecha_hito",
        "informe_id", "informe_con_pdf_id", "recomendacion_id", "evidencia_borrador_id", "evidencia_final_id",
        "dictamen_id", "unidad_destino", "usuario_ejecutor_id", "recomendacion_sin_plan_id",
    )],
    "item": items,
}


def var(key, value="", secret=False):
    return {"key": key, "value": value, "type": "secret" if secret else "default", "enabled": True}


def entorno(slug, nombre, base_url, *, credenciales, solo_lectura):
    valores = [var("baseUrl", base_url), var("entorno", slug), var("solo_lectura", "true" if solo_lectura else "false")]
    for rol in ("uai", "ejecutor", "dti", "rectorado"):
        valores.append(var(f"cred_{rol}", credenciales.get(rol, ""), secret=True))
    valores.append(var("cred_invalida", "credencial-invalida"))
    valores += [var(token, secret=True) for token in TOKEN_VARS]
    return {
        "id": str(uuid.uuid5(NS, f"entorno-{slug}")),
        "name": nombre,
        "values": valores,
        "_postman_variable_scope": "environment",
    }


ENTORNOS = {
    "desarrollo": entorno(
        "desarrollo", "SITRA-CGE desarrollo", "http://127.0.0.1:8000",
        credenciales={"uai": "uai-sso-token", "ejecutor": "ejecutor-sso-token",
                      "dti": "dti-sso-token", "rectorado": "rectorado-sso-token"},
        solo_lectura=False,
    ),
    "preproduccion": entorno(
        "preproduccion", "SITRA-CGE preproducción", "https://CAMBIAR-servidor-preproduccion",
        credenciales={}, solo_lectura=False,
    ),
    "produccion": entorno(
        "produccion", "SITRA-CGE producción", "https://CAMBIAR-servidor-produccion",
        credenciales={}, solo_lectura=True,
    ),
}

(out / "SITRA-CGE.postman_collection.json").write_text(
    json.dumps(collection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for slug, env in ENTORNOS.items():
    (out / f"SITRA-CGE-{slug}.postman_environment.json").write_text(
        json.dumps(env, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(sum(len(f["item"]) for f in items), "solicitudes,", ejemplos, "con ejemplo de respuesta")
