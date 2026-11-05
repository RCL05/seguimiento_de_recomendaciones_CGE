import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

import { api, ApiError, Recommendation, Report, Unit } from "../../../api/client";
import { FormStepper } from "../../../components/FormStepper";
import { Toast } from "../../../components/Toast";
import { formatDate, STATE_OPTIONS } from "../../../components/format";
import { EmptyState, Notice, PageHeader, RecommendationBadges } from "../../../components/ui";
import { useToast } from "../../../hooks/useToast";

const MAX_REPORT_PDF_BYTES = 30 * 1024 * 1024;

function today() {
  return new Date().toISOString().slice(0, 10);
}

function addDays(isoDate: string, days: number) {
  const date = new Date(`${isoDate}T00:00:00`);
  date.setDate(date.getDate() + days);
  return date.toISOString().slice(0, 10);
}

export function RegistroRecomendacionPage() {
  const [units, setUnits] = useState<Unit[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [createdReport, setCreatedReport] = useState<Report | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [notificationDate, setNotificationDate] = useState(today());
  const [legalDays, setLegalDays] = useState(30);
  const [filters, setFilters] = useState({ text: "", state: "", unit: "", overdue: false });
  const { toast, showToast, dismissToast } = useToast();

  const refreshRecommendations = useCallback(async () => {
    setRecommendations(await api.listRecommendations());
  }, []);

  useEffect(() => {
    api.listUnits().then(setUnits).catch((caught) => {
      showToast(caught instanceof ApiError ? caught.message : "No se pudieron cargar las unidades.", "error");
    });
    refreshRecommendations()
      .catch((caught) => {
        showToast(caught instanceof ApiError ? caught.message : "No se pudieron cargar las recomendaciones.", "error");
      })
      .finally(() => setLoading(false));
  }, [refreshRecommendations, showToast]);

  const visible = useMemo(() => {
    const text = filters.text.trim().toLowerCase();
    return recommendations.filter(
      (item) =>
        (!filters.state || item.state === filters.state) &&
        (!filters.unit || item.unit_id === filters.unit) &&
        (!filters.overdue || item.vencida) &&
        (!text || `${item.number} ${item.description}`.toLowerCase().includes(text)),
    );
  }, [filters, recommendations]);

  const overdueCount = recommendations.filter((item) => item.vencida).length;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    setSaving(true);

    try {
      let report = createdReport;
      if (!report) {
        const document = form.get("pdf_informe");
        if (!(document instanceof File) || !document.name) {
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
      await refreshRecommendations();
      showToast(`Recomendación ${recommendation.number} registrada y asignada a ${recommendation.unit_id}.`);
      setCreatedReport(null);
      formElement.reset();
      setNotificationDate(today());
      setLegalDays(30);
      setFormOpen(false);
    } catch (caught) {
      showToast(caught instanceof ApiError ? caught.message : "No se pudo registrar.", "error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="Unidad de Auditoría Interna"
        title="Recomendaciones CGE"
        description="Registre los informes de la Contraloría, asigne cada recomendación a su unidad ejecutora y siga su cumplimiento."
        actions={
          <button type="button" onClick={() => setFormOpen((open) => !open)} aria-expanded={formOpen}>
            {formOpen ? "Cerrar formulario" : "+ Nueva recomendación"}
          </button>
        }
      />

      {formOpen && (
        <section className="card" aria-labelledby="registro-title">
          <div className="card-header">
            <div>
              <h2 id="registro-title">Registrar informe y recomendación</h2>
              <p>La recomendación se crea en estado Pendiente y queda visible para la unidad asignada.</p>
            </div>
          </div>
          <FormStepper
            currentStep={createdReport ? 2 : 1}
            steps={[
              { label: "Adjunte el Informe CGE", description: "PDF oficial y datos del examen especial." },
              { label: "Registre la recomendación", description: "Unidad, plazo, prioridad y descripción." },
            ]}
          />
          {createdReport && (
            <Notice tone="info">
              Informe {createdReport.numero_informe} guardado. Complete la recomendación para terminar el registro.
            </Notice>
          )}
          <form className="form-grid" onSubmit={handleSubmit}>
            <fieldset className="form-section" disabled={Boolean(createdReport)}>
              <legend>Informe CGE</legend>
              <label>
                Número de informe
                <input name="numero_informe" required maxLength={100} placeholder="DNAI-AI-0123-2026" />
              </label>
              <label>
                Período auditado
                <input name="periodo_auditado" required maxLength={100} placeholder="2024-2025" />
              </label>
              <label>
                Fecha de notificación
                <input
                  name="fecha_notificacion"
                  type="date"
                  required
                  value={notificationDate}
                  onChange={(event) => setNotificationDate(event.target.value)}
                />
              </label>
              <label>
                Informe CGE (PDF, máximo 30 MB)
                <input name="pdf_informe" type="file" accept="application/pdf,.pdf" required={!createdReport} />
              </label>
            </fieldset>

            <fieldset className="form-section">
              <legend>Recomendación</legend>
              <label>
                Número de recomendación
                <input name="numero_recomendacion" required maxLength={50} placeholder="R-01" />
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
                <input
                  name="plazo_legal_dias"
                  type="number"
                  min={1}
                  required
                  value={legalDays}
                  onChange={(event) => setLegalDays(Number(event.target.value))}
                />
              </label>
              <label>
                Fecha de vencimiento
                <input
                  name="fecha_vencimiento"
                  type="date"
                  required
                  key={`${notificationDate}-${legalDays}`}
                  defaultValue={legalDays > 0 ? addDays(notificationDate, legalDays) : ""}
                />
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
                <textarea name="descripcion" required rows={3} placeholder="Texto de la recomendación emitida por la CGE" />
              </label>
            </fieldset>

            <div className="form-footer">
              <span className="hint">La fecha de vencimiento se sugiere a partir de la notificación y el plazo legal.</span>
              <button type="submit" disabled={saving || units.length === 0}>
                {saving ? "Guardando..." : createdReport ? "Registrar recomendación" : "Registrar informe y recomendación"}
              </button>
            </div>
          </form>
        </section>
      )}

      <section className="card" aria-labelledby="listado-title">
        <div className="card-header">
          <div>
            <h2 id="listado-title">Seguimiento</h2>
            <p>
              {recommendations.length} recomendaciones · {overdueCount} vencidas
            </p>
          </div>
        </div>

        <div className="filters" role="search">
          <label className="grow">
            Buscar
            <input
              type="search"
              placeholder="Número o descripción"
              value={filters.text}
              onChange={(event) => setFilters({ ...filters, text: event.target.value })}
            />
          </label>
          <label>
            Estado
            <select value={filters.state} onChange={(event) => setFilters({ ...filters, state: event.target.value })}>
              <option value="">Todos</option>
              {STATE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Unidad
            <select value={filters.unit} onChange={(event) => setFilters({ ...filters, unit: event.target.value })}>
              <option value="">Todas</option>
              {units.map((unit) => (
                <option key={unit.id} value={unit.codigo}>
                  {unit.codigo}
                </option>
              ))}
            </select>
          </label>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={filters.overdue}
              onChange={(event) => setFilters({ ...filters, overdue: event.target.checked })}
            />
            Solo vencidas
          </label>
        </div>

        {loading ? (
          <p role="status" className="muted">
            Cargando recomendaciones...
          </p>
        ) : recommendations.length === 0 ? (
          <EmptyState title="Aún no hay recomendaciones">
            <p>Use “Nueva recomendación” para registrar el primer informe de la CGE.</p>
          </EmptyState>
        ) : visible.length === 0 ? (
          <EmptyState title="Sin resultados">
            <p>Ninguna recomendación coincide con los filtros.</p>
          </EmptyState>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Recomendación</th>
                  <th>Unidad</th>
                  <th>Vencimiento</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {visible.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <div className="cell-title">{item.number}</div>
                      <div className="cell-sub">{item.description}</div>
                    </td>
                    <td>{item.unit_id}</td>
                    <td>
                      {formatDate(item.due_date)}
                      <div className="cell-sub">{item.legal_days} días</div>
                    </td>
                    <td>
                      <RecommendationBadges item={item} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      <Toast toast={toast} onClose={dismissToast} />
    </>
  );
}
