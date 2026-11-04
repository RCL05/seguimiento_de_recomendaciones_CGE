import { FormEvent, useCallback, useEffect, useRef, useState } from "react";

import { api, ApiError, Recommendation, Report, Unit } from "../../../api/client";
import { FormStepper } from "../../../components/FormStepper";
import { Toast } from "../../../components/Toast";
import { useToast } from "../../../hooks/useToast";

const MAX_REPORT_PDF_BYTES = 30 * 1024 * 1024;

function today() {
  return new Date().toISOString().slice(0, 10);
}

export function RegistroRecomendacionPage() {
  const [units, setUnits] = useState<Unit[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [createdReport, setCreatedReport] = useState<Report | null>(null);
  const [created, setCreated] = useState<Recommendation | null>(null);
  const [saving, setSaving] = useState(false);
  const formRef = useRef<HTMLFormElement>(null);
  const { toast, showToast, dismissToast } = useToast();

  const refreshRecommendations = useCallback(async () => {
    setRecommendations(await api.listRecommendations());
  }, []);

  useEffect(() => {
    api.listUnits().then(setUnits).catch((caught) => {
      showToast(caught instanceof ApiError ? caught.message : "No se pudieron cargar las unidades.", "error");
    });
    refreshRecommendations().catch((caught) => {
      showToast(caught instanceof ApiError ? caught.message : "No se pudieron cargar las recomendaciones.", "error");
    });
  }, [refreshRecommendations, showToast]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    setSaving(true);
    setCreated(null);

    try {
      let report = createdReport;
      if (!report) {
        const document = form.get("pdf_informe");
        if (!(document instanceof File)) {
          showToast("Seleccione el PDF oficial del informe.", "error");
          return;
        }
        if (document.type !== "application/pdf" || !document.name.toLowerCase().endsWith(".pdf")) {
          showToast("El documento oficial debe ser un archivo PDF.", "error");
          return;
        }
        if (document.size > MAX_REPORT_PDF_BYTES) {
          showToast("El PDF supera el límite de 30 MB.", "error");
          return;
        }
        const reportPayload = new FormData();
        reportPayload.set("numero_informe", String(form.get("numero_informe")));
        reportPayload.set("periodo_auditado", String(form.get("periodo_auditado")));
        reportPayload.set("fecha_notificacion", String(form.get("fecha_notificacion")));
        reportPayload.set("pdf_informe", document);
        report = await api.createReport(reportPayload);
        setCreatedReport(report);
      }

      const recommendation = await api.createRecommendation({
        report_id: report.id,
        number: String(form.get("numero_recomendacion")),
        description: String(form.get("descripcion")),
        unit_id: String(form.get("unidad")),
        legal_days: Number(form.get("plazo_legal_dias")),
        due_date: String(form.get("fecha_vencimiento")),
        priority: String(form.get("prioridad")),
      });
      setCreated(recommendation);
      await refreshRecommendations();
      showToast(`Recomendación ${recommendation.number} registrada y asignada.`);
      setCreatedReport(null);
      formElement.reset();
    } catch (caught) {
      showToast(caught instanceof ApiError ? caught.message : "No se pudo registrar.", "error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="card" aria-labelledby="registro-title">
      <h2 id="registro-title">Registrar informe y recomendación</h2>
      <p>La UAI carga el informe CGE y asigna la recomendación a una unidad ejecutora.</p>
      <FormStepper
        currentStep={createdReport ? 2 : 1}
        steps={[
          {
            label: "Adjunte el Informe CGE",
            description: "Seleccione el PDF oficial y complete sus datos.",
          },
          {
            label: "Registre la recomendación",
            description: "Asigne unidad, plazo, prioridad y descripción.",
          },
        ]}
      />
      {createdReport && (
        <p className="hint" role="status">
          Informe {createdReport.numero_informe} guardado. Complete la recomendación para terminar el registro.
        </p>
      )}
      <form ref={formRef} className="form-grid" onSubmit={handleSubmit}>
        <label>
          Número de informe
          <input name="numero_informe" required maxLength={100} disabled={Boolean(createdReport)} />
        </label>
        <label>
          Período auditado
          <input name="periodo_auditado" required maxLength={100} disabled={Boolean(createdReport)} />
        </label>
        <label>
          Fecha de notificación
          <input
            name="fecha_notificacion"
            type="date"
            required
            defaultValue={today()}
            disabled={Boolean(createdReport)}
          />
        </label>
        <label>
          Informe CGE (PDF, máximo 30 MB)
          <input
            name="pdf_informe"
            type="file"
            accept="application/pdf,.pdf"
            required={!createdReport}
            disabled={Boolean(createdReport)}
          />
        </label>
        <label>
          Número de recomendación
          <input name="numero_recomendacion" required maxLength={50} />
        </label>
        <label>
          Unidad responsable
          <select name="unidad" required defaultValue="" disabled={units.length === 0}>
            <option value="" disabled>
              {units.length ? "Seleccione una unidad" : "No hay unidades activas disponibles"}
            </option>
            {units.map((unit) => (
              <option key={unit.id} value={unit.codigo}>
                {unit.codigo} - {unit.nombre}
              </option>
            ))}
          </select>
        </label>
        <label>
          Plazo legal (días)
          <input name="plazo_legal_dias" type="number" min={1} required defaultValue={30} />
        </label>
        <label>
          Fecha de vencimiento
          <input name="fecha_vencimiento" type="date" required />
        </label>
        <label>
          Prioridad
          <select name="prioridad" defaultValue="MEDIA">
            <option value="ALTA">Alta</option>
            <option value="MEDIA">Media</option>
            <option value="BAJA">Baja</option>
          </select>
        </label>
        <label className="full-width">
          Descripción
          <textarea name="descripcion" required rows={4} />
        </label>
        <button type="submit" disabled={saving || units.length === 0}>
          {saving ? "Guardando..." : createdReport ? "Registrar recomendación" : "Registrar informe y recomendación"}
        </button>
      </form>
      {created && (
        <p className="hint">
          Estado inicial: <strong>{created.state}</strong> · vence {created.due_date}
        </p>
      )}
      {recommendations.length > 0 && (
        <div className="recent-items">
          <h3>Recomendaciones actualizadas</h3>
          <ul>
            {recommendations.slice(0, 5).map((item) => (
              <li key={item.id}>
                <strong>{item.number}</strong> · {item.state} · {item.unit_id}
              </li>
            ))}
          </ul>
        </div>
      )}
      <Toast toast={toast} onClose={dismissToast} />
    </section>
  );
}
