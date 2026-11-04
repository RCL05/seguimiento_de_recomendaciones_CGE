import { FormEvent, useCallback, useEffect, useState } from "react";

import { api, ApiError, Recommendation } from "../../../api/client";
import { FormStepper } from "../../../components/FormStepper";
import { Toast } from "../../../components/Toast";
import { useToast } from "../../../hooks/useToast";
import { EvidenceUpload } from "../../evidencias/components/EvidenceUpload";

const RESTARTABLE_STATES = new Set(["VENCIDA", "REABIERTA"]);

export function PlanAccionPage() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [selected, setSelected] = useState("");
  const [savingPlan, setSavingPlan] = useState(false);
  const [loading, setLoading] = useState(true);
  const { toast, showToast, dismissToast } = useToast();

  const refreshRecommendations = useCallback(async () => {
    const items = await api.listRecommendations();
    setRecommendations(items);
    setSelected((current) => (items.some((item) => item.id === current) ? current : items[0]?.id ?? ""));
  }, []);

  useEffect(() => {
    refreshRecommendations()
      .catch((caught) => {
        showToast(caught instanceof ApiError ? caught.message : "No se pudo cargar la bandeja.", "error");
      })
      .finally(() => setLoading(false));
  }, [refreshRecommendations, showToast]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    setSavingPlan(true);
    try {
      await api.createPlan(selected, {
        descripcion_hito: String(form.get("descripcion_hito")),
        fecha_compromiso: String(form.get("fecha_compromiso")),
      });
      await refreshRecommendations();
      showToast("Plan de acción registrado. La bandeja se actualizó.");
      formElement.reset();
    } catch (caught) {
      showToast(caught instanceof ApiError ? caught.message : "No se pudo registrar el plan.", "error");
    } finally {
      setSavingPlan(false);
    }
  }

  const current = recommendations.find((item) => item.id === selected);
  const canRegisterPlan = current?.state === "PENDIENTE" || RESTARTABLE_STATES.has(current?.state ?? "");
  const canUploadEvidence = current?.state === "EN_PROCESO";
  const underReview = current?.state === "EN_VALIDACION";
  const currentStep =
    current?.state === "EN_PROCESO"
      ? 2
      : current?.state === "EN_VALIDACION"
        ? 3
        : 1;

  return (
    <section className="card" aria-labelledby="plan-title">
      <h2 id="plan-title">Bandeja del ejecutor</h2>
      <p>Seleccione una recomendación de su unidad y continúe según su estado actual.</p>
      <FormStepper
        currentStep={currentStep}
        steps={[
          {
            label: "Registre su Plan de Acción",
            description: "Defina el hito y la fecha de compromiso.",
          },
          {
            label: "Adjunte evidencia PDF",
            description: "Respalde el avance de su unidad.",
          },
          {
            label: "Espere la validación UAI",
            description: "La auditoría revisará la evidencia.",
          },
        ]}
      />

      {loading ? (
        <p role="status">Cargando recomendaciones...</p>
      ) : recommendations.length === 0 ? (
        <p>No tiene recomendaciones asignadas.</p>
      ) : (
        <>
          <label>
            Recomendación
            <select value={selected} onChange={(event) => setSelected(event.target.value)}>
              {recommendations.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.number} · {item.state} · vence {item.due_date}
                </option>
              ))}
            </select>
          </label>

          {current && (
            <>
              <div className="recommendation-summary">
                <span className={`state-badge state-${current.state.toLowerCase()}`}>{current.state}</span>
                <p>{current.description} · Unidad {current.unit_id}</p>
              </div>

              {underReview ? (
                <p className="state-notice info" role="status">
                  En revisión por Auditoría UAI
                </p>
              ) : canRegisterPlan ? (
                <form className="form-grid" onSubmit={handleSubmit}>
                  <p className="full-width hint">
                    {current.state === "PENDIENTE"
                      ? "Registre el Plan de Acción para iniciar la ejecución."
                      : "Registre un nuevo Plan de Acción para reanudar la ejecución."}
                  </p>
                  <label className="full-width">
                    Descripción del hito
                    <textarea name="descripcion_hito" required rows={3} />
                  </label>
                  <label>
                    Fecha de compromiso
                    <input name="fecha_compromiso" type="date" required />
                  </label>
                  <button className="action-highlight" type="submit" disabled={savingPlan}>
                    {savingPlan ? "Registrando..." : "Registrar Plan de Acción"}
                  </button>
                </form>
              ) : canUploadEvidence ? (
                <EvidenceUpload
                  recommendationId={selected}
                  onUploaded={() => {
                    refreshRecommendations().catch((caught) => {
                      showToast(caught instanceof ApiError ? caught.message : "No se pudo actualizar la bandeja.", "error");
                    });
                  }}
                />
              ) : (
                <div className="disabled-action" role="status">
                  <button
                    type="button"
                    disabled
                    title="Esta recomendación no admite acciones en su estado actual."
                    aria-describedby="state-action-help"
                  >
                    Acción no disponible
                  </button>
                  <span id="state-action-help">
                    No hay acciones disponibles para la recomendación en estado {current.state}.
                  </span>
                </div>
              )}

              {current.state === "PENDIENTE" && (
                <EvidenceUpload
                  recommendationId={selected}
                  disabled
                  disabledMessage="Registre el plan para habilitar la subida de evidencias."
                />
              )}
            </>
          )}
        </>
      )}
      <Toast toast={toast} onClose={dismissToast} />
    </section>
  );
}
