import { FormEvent, useState } from "react";

import { api, ApiError, Recommendation } from "../../../api/client";

function today() {
  return new Date().toISOString().slice(0, 10);
}

export function RegistroRecomendacionPage() {
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [created, setCreated] = useState<Recommendation | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");
    const form = new FormData(event.currentTarget);

    try {
      const report = await api.createReport({
        numero_informe: String(form.get("numero_informe")),
        periodo_auditado: String(form.get("periodo_auditado")),
        fecha_notificacion: String(form.get("fecha_notificacion")),
        pdf_informe_url: String(form.get("pdf_informe_url")),
      });
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
      setMessage(`Recomendación ${recommendation.number} registrada y asignada.`);
      event.currentTarget.reset();
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "No se pudo registrar.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="card" aria-labelledby="registro-title">
      <h2 id="registro-title">Registrar informe y recomendación</h2>
      <p>La UAI registra el informe CGE y asigna la recomendación a la unidad ejecutora.</p>
      <form className="form-grid" onSubmit={handleSubmit}>
        <label>
          Número de informe
          <input name="numero_informe" required maxLength={100} />
        </label>
        <label>
          Período auditado
          <input name="periodo_auditado" required maxLength={100} />
        </label>
        <label>
          Fecha de notificación
          <input name="fecha_notificacion" type="date" required defaultValue={today()} />
        </label>
        <label>
          Documento oficial (URL)
          <input name="pdf_informe_url" type="url" required />
        </label>
        <label>
          Número de recomendación
          <input name="numero_recomendacion" required maxLength={50} />
        </label>
        <label>
          Unidad responsable
          <input name="unidad" required defaultValue="UAI" />
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
        <button type="submit" disabled={saving}>
          {saving ? "Registrando..." : "Registrar recomendación"}
        </button>
      </form>
      {message && <p className="feedback success">{message}</p>}
      {error && <p className="feedback error">{error}</p>}
      {created && (
        <p className="hint">
          Estado inicial: <strong>{created.state}</strong> · vence {created.due_date}
        </p>
      )}
    </section>
  );
}
