import { useCallback, useEffect, useRef, useState } from "react";

import {
  api,
  ApiError,
  Evidence,
  Recommendation,
  RecommendationDetail,
} from "../../../api/client";
import { FormStepper } from "../../../components/FormStepper";
import { Toast } from "../../../components/Toast";
import { useToast } from "../../../hooks/useToast";

const REVIEW_STATE = "EN_VALIDACION";

export function ReviewEvidencePage() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [selected, setSelected] = useState("");
  const [detail, setDetail] = useState<RecommendationDetail | null>(null);
  const [evidenceId, setEvidenceId] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const formRef = useRef<HTMLFormElement>(null);
  const { toast, showToast, dismissToast } = useToast();

  const refreshQueue = useCallback(async () => {
    const items = (await api.listRecommendations()).filter((item) => item.state === REVIEW_STATE);
    setRecommendations(items);
    setSelected((current) => (items.some((item) => item.id === current) ? current : items[0]?.id ?? ""));
    return items;
  }, []);

  useEffect(() => {
    refreshQueue().catch((caught) => {
      showToast(caught instanceof ApiError ? caught.message : "No se pudo cargar la revisión.", "error");
    });
  }, [refreshQueue, showToast]);

  useEffect(() => {
    if (!selected) {
      setDetail(null);
      setEvidenceId("");
      return;
    }
    let active = true;
    setLoading(true);
    api
      .getRecommendation(selected)
      .then((item) => {
        if (!active) return;
        setDetail(item);
        const evidence = item.evidencias.find(
          (candidate) => !candidate.validated && candidate.status !== "ANULADA",
        );
        setEvidenceId(evidence?.id ?? "");
      })
      .catch((caught) => {
        if (active) {
          showToast(caught instanceof ApiError ? caught.message : "No se pudo cargar la evidencia.", "error");
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [selected, showToast]);

  async function submitDictamen(approved: boolean) {
    if (!selected || !evidenceId || detail?.state !== REVIEW_STATE) return;
    const form = formRef.current ? new FormData(formRef.current) : new FormData();
    setSubmitting(true);
    try {
      const updated = await api.submitDictamen(selected, {
        evidence_id: evidenceId,
        approved,
        observaciones: String(form.get("observaciones") ?? ""),
      });
      await refreshQueue();
      setDetail(null);
      setEvidenceId("");
      showToast(
        approved
          ? `Evidencia aprobada. La recomendación quedó en estado ${updated.state}.`
          : `Evidencia rechazada. La recomendación volvió al estado ${updated.state}.`,
      );
    } catch (caught) {
      showToast(caught instanceof ApiError ? caught.message : "No se pudo registrar el dictamen.", "error");
    } finally {
      setSubmitting(false);
    }
  }

  async function openEvidence(item: Evidence, disposition: "inline" | "attachment") {
    const previewWindow = disposition === "inline" ? window.open("about:blank", "_blank") : null;
    if (disposition === "inline" && !previewWindow) {
      showToast("Permita las ventanas emergentes para previsualizar el PDF.", "error");
      return;
    }
    try {
      const blob = await api.getEvidenceFile(item.id, disposition);
      const url = URL.createObjectURL(blob);
      if (previewWindow) {
        previewWindow.location.href = url;
      } else {
        const anchor = document.createElement("a");
        anchor.href = url;
        anchor.download = item.filename;
        anchor.click();
      }
      window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (caught) {
      previewWindow?.close();
      showToast(caught instanceof ApiError ? caught.message : "No se pudo abrir el PDF.", "error");
    }
  }

  const selectableEvidence = detail?.evidencias.filter((item) => item.status !== "ANULADA") ?? [];
  const canIssueDecision = detail?.state === REVIEW_STATE && Boolean(evidenceId) && !loading && !submitting;

  return (
    <section className="card" aria-labelledby="revision-title">
      <h2 id="revision-title">Revisión UAI de evidencias</h2>
      <p>Revise los archivos adjuntos antes de aprobar o rechazar el cumplimiento.</p>
      <FormStepper
        currentStep={detail ? (evidenceId ? 3 : 2) : 1}
        steps={[
          {
            label: "Seleccione una recomendación",
            description: "Elija una recomendación en validación.",
          },
          {
            label: "Revise la evidencia PDF",
            description: "Abra el archivo y compruebe su integridad.",
          },
          {
            label: "Emita el dictamen",
            description: "Apruebe o rechace con observaciones.",
          },
        ]}
      />

      {recommendations.length === 0 ? (
        <p>No hay recomendaciones en validación por la UAI.</p>
      ) : (
        <>
          <label>
            Recomendación en validación
            <select value={selected} onChange={(event) => setSelected(event.target.value)}>
              {recommendations.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.number} · {item.unit_id}
                </option>
              ))}
            </select>
          </label>

          {loading ? (
            <p role="status">Cargando evidencias...</p>
          ) : detail ? (
            <div className="detail">
              <p>{detail.description}</p>
              <span className="state-badge state-en_validacion">En Validación</span>
              {detail.evidencias.length === 0 ? (
                <p>No hay evidencias adjuntas.</p>
              ) : (
                <ul className="evidence-list">
                  {detail.evidencias.map((item) => (
                    <li key={item.id}>
                      <div>
                        <strong>{item.filename}</strong>
                        <small>
                          {item.type ?? "Evidencia"} · {item.status ?? "VIGENTE"} · {item.validated ? "Validada" : "Pendiente"}
                        </small>
                        <small className="hash">SHA-256: {item.sha256}</small>
                      </div>
                      <div className="actions">
                        <button type="button" className="secondary" onClick={() => openEvidence(item, "inline")}>
                          Vista previa
                        </button>
                        <button type="button" className="secondary" onClick={() => openEvidence(item, "attachment")}>
                          Descargar
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              )}

              {selectableEvidence.length > 0 && detail.state === REVIEW_STATE ? (
                <>
                  <label>
                    Evidencia para dictamen
                    <select value={evidenceId} onChange={(event) => setEvidenceId(event.target.value)}>
                      {selectableEvidence.map((item) => (
                        <option key={item.id} value={item.id}>
                          {item.filename} · {item.validated ? "validada" : "pendiente"}
                        </option>
                      ))}
                    </select>
                  </label>
                  <form ref={formRef} className="form-grid">
                    <label className="full-width">
                      Observaciones
                      <textarea name="observaciones" rows={3} placeholder="Obligatorias al rechazar" />
                    </label>
                  </form>
                  <div className="actions">
                    <button
                      type="button"
                      onClick={() => submitDictamen(true)}
                      disabled={!canIssueDecision}
                      title={
                        canIssueDecision
                          ? "Aprobar la evidencia validada."
                          : "Seleccione una evidencia vigente para habilitar el dictamen."
                      }
                      aria-describedby="decision-help"
                    >
                      Aprobar
                    </button>
                    <button
                      type="button"
                      className="secondary"
                      onClick={() => submitDictamen(false)}
                      disabled={!canIssueDecision}
                      title={
                        canIssueDecision
                          ? "Rechazar la evidencia y devolver la recomendación a ejecución."
                          : "Seleccione una evidencia vigente para habilitar el dictamen."
                      }
                      aria-describedby="decision-help"
                    >
                      Rechazar
                    </button>
                  </div>
                  {!canIssueDecision && (
                    <p id="decision-help" className="button-help">
                      Seleccione una evidencia vigente y espere a que termine la carga para emitir el dictamen.
                    </p>
                  )}
                </>
              ) : (
                <p className="state-notice">No hay evidencias vigentes disponibles para dictamen.</p>
              )}
            </div>
          ) : null}
        </>
      )}
      <Toast toast={toast} onClose={dismissToast} />
    </section>
  );
}
