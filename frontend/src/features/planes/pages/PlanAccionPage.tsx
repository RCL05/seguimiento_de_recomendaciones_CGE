import { FormEvent, useCallback, useEffect, useState } from "react";

import { api, ApiError, Milestone, Recommendation } from "../../../api/client";
import { FormStepper } from "../../../components/FormStepper";
import { Toast } from "../../../components/Toast";
import { formatDate, stateLabel } from "../../../components/format";
import { EmptyState, Notice, PageHeader, RecommendationBadges, RecommendationQueue } from "../../../components/ui";
import { useToast } from "../../../hooks/useToast";
import { EvidenceUpload } from "../../evidencias/components/EvidenceUpload";

// "Vencida" no es un estado: es un indicador (recommendation.vencida) y no bloquea el flujo.
const RESTARTABLE_STATES = new Set(["REABIERTA"]);

function today() {
  return new Date().toISOString().slice(0, 10);
}

export function PlanAccionPage() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [selected, setSelected] = useState("");
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [savingPlan, setSavingPlan] = useState(false);
  const [loading, setLoading] = useState(true);
  const { toast, showToast, dismissToast } = useToast();

  const refreshRecommendations = useCallback(async () => {
    const items = await api.listRecommendations();
    setRecommendations(items);
    setSelected((current) => (items.some((item) => item.id === current) ? current : items[0]?.id ?? ""));
  }, []);

  const refreshMilestones = useCallback(async (recommendationId: string) => {
    setMilestones(recommendationId ? await api.listPlan(recommendationId) : []);
  }, []);

  useEffect(() => {
    refreshRecommendations()
      .catch((caught) => {
        showToast(caught instanceof ApiError ? caught.message : "No se pudo cargar la bandeja.", "error");
      })
      .finally(() => setLoading(false));
  }, [refreshRecommendations, showToast]);

  useEffect(() => {
    refreshMilestones(selected).catch(() => setMilestones([]));
  }, [refreshMilestones, selected]);

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
      await Promise.all([refreshRecommendations(), refreshMilestones(selected)]);
      showToast("Hito del plan de acción registrado.");
      formElement.reset();
    } catch (caught) {
      showToast(caught instanceof ApiError ? caught.message : "No se pudo registrar el plan.", "error");
    } finally {
      setSavingPlan(false);
    }
  }

  const current = recommendations.find((item) => item.id === selected);
  const startsPlan = current?.state === "PENDIENTE" || RESTARTABLE_STATES.has(current?.state ?? "");
  const inProgress = current?.state === "EN_PROCESO";
  const underReview = current?.state === "EN_VALIDACION";
  const currentStep = inProgress ? 2 : underReview ? 3 : current?.state === "CUMPLIDA" ? 4 : 1;
  const minDate = current?.vencida ? today() : undefined;
  const maxDate = current && !current.vencida ? current.due_date : undefined;

  return (
    <>
      <PageHeader
        eyebrow="Unidad ejecutora"
        title="Mi bandeja"
        description="Registre el plan de acción y respalde el cumplimiento con evidencias PDF para la revisión de la UAI."
      />

      {loading ? (
        <p role="status" className="muted">
          Cargando recomendaciones...
        </p>
      ) : recommendations.length === 0 ? (
        <EmptyState title="No tiene recomendaciones asignadas">
          <p>Cuando la UAI le asigne una recomendación aparecerá aquí.</p>
        </EmptyState>
      ) : (
        <div className="split">
          <section className="card" aria-labelledby="bandeja-title">
            <div className="card-header">
              <h2 id="bandeja-title">Recomendaciones de su unidad</h2>
            </div>
            <RecommendationQueue
              items={recommendations}
              selected={selected}
              onSelect={setSelected}
              label="Recomendaciones de su unidad"
            />
          </section>

          {current && (
            <section className="card" aria-labelledby="detalle-title">
              <div className="card-header">
                <div>
                  <p className="eyebrow">Recomendación {current.number}</p>
                  <h2 id="detalle-title">{current.description}</h2>
                </div>
                <RecommendationBadges item={current} />
              </div>

              <dl className="detail-meta">
                <div>
                  <dt>Unidad</dt>
                  <dd>{current.unit_id}</dd>
                </div>
                <div>
                  <dt>Plazo legal</dt>
                  <dd>{current.legal_days} días</dd>
                </div>
                <div>
                  <dt>Vence</dt>
                  <dd>{formatDate(current.due_date)}</dd>
                </div>
                <div>
                  <dt>Estado</dt>
                  <dd>{stateLabel(current.state)}</dd>
                </div>
              </dl>

              <FormStepper
                currentStep={currentStep}
                steps={[
                  { label: "Plan de acción", description: "Defina hitos y fechas de compromiso." },
                  { label: "Evidencia PDF", description: "Respalde el avance de su unidad." },
                  { label: "Validación UAI", description: "La auditoría revisa la evidencia." },
                ]}
              />

              <div className="stack">
                {current.vencida && (
                  <Notice tone="warning">
                    El plazo legal venció el {formatDate(current.due_date)}. Puede continuar: los nuevos hitos deben
                    tener fecha de hoy en adelante y el cumplimiento quedará registrado como tardío.
                  </Notice>
                )}

                {underReview && <Notice tone="info">En revisión por Auditoría UAI. Recibirá el dictamen en su bandeja.</Notice>}
                {current.state === "CUMPLIDA" && (
                  <Notice tone="success">Recomendación cumplida: la UAI aprobó la evidencia.</Notice>
                )}

                {milestones.length > 0 && (
                  <div>
                    <h3>Plan de acción</h3>
                    <ul className="evidence-list">
                      {milestones.map((hito) => (
                        <li key={hito.id}>
                          <div>
                            <strong>{hito.descripcion_hito}</strong>
                            <small className="muted">Compromiso: {formatDate(hito.fecha_compromiso)}</small>
                          </div>
                          <span className={`badge ${hito.completado ? "state-cumplida" : "neutral"}`}>
                            {hito.completado ? "Completado" : "En curso"}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {(startsPlan || inProgress) && (
                  <form className="form-grid" onSubmit={handleSubmit} aria-label="Registrar hito">
                    <p className="full-width hint">
                      {current.state === "PENDIENTE"
                        ? "Registre el primer hito del plan de acción para iniciar la ejecución."
                        : startsPlan
                          ? "Registre un nuevo hito para reanudar la ejecución."
                          : "Puede agregar hitos al plan mientras la recomendación está en proceso."}
                    </p>
                    <label className="full-width">
                      Descripción del hito
                      <textarea name="descripcion_hito" required rows={2} />
                    </label>
                    <label>
                      Fecha de compromiso
                      <input name="fecha_compromiso" type="date" required min={minDate} max={maxDate} />
                    </label>
                    <div className="form-footer">
                      <button type="submit" className={inProgress ? "secondary" : undefined} disabled={savingPlan}>
                        {savingPlan ? "Registrando..." : inProgress ? "Agregar hito" : "Registrar Plan de Acción"}
                      </button>
                    </div>
                  </form>
                )}

                {inProgress ? (
                  <EvidenceUpload
                    recommendationId={selected}
                    onUploaded={() => {
                      refreshRecommendations().catch((caught) => {
                        showToast(caught instanceof ApiError ? caught.message : "No se pudo actualizar la bandeja.", "error");
                      });
                    }}
                  />
                ) : (
                  current.state === "PENDIENTE" && (
                    <EvidenceUpload
                      recommendationId={selected}
                      disabled
                      disabledMessage="Registre el plan para habilitar la subida de evidencias."
                    />
                  )
                )}
              </div>
            </section>
          )}
        </div>
      )}
      <Toast toast={toast} onClose={dismissToast} />
    </>
  );
}
