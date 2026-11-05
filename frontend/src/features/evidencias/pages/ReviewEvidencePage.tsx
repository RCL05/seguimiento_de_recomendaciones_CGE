import { useCallback, useEffect, useRef, useState } from "react";

import { api, ApiError, Evidence, Recommendation, RecommendationDetail } from "../../../api/client";
import { Toast } from "../../../components/Toast";
import { formatDate, formatDateTime, stateLabel } from "../../../components/format";
import { EmptyState, Notice, PageHeader, RecommendationBadges, RecommendationQueue } from "../../../components/ui";
import { useToast } from "../../../hooks/useToast";

const REVIEW_STATE = "EN_VALIDACION";

function formatSize(bytes: number) {
  return bytes >= 1024 * 1024 ? `${(bytes / (1024 * 1024)).toFixed(1)} MB` : `${Math.max(1, Math.round(bytes / 1024))} KB`;
}

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
        const evidence = item.evidencias.find((candidate) => !candidate.validated && candidate.status !== "ANULADA");
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
    const observaciones = String(form.get("observaciones") ?? "");
    if (!approved && !observaciones.trim()) {
      showToast("Escriba las observaciones para el ejecutor antes de rechazar.", "error");
      return;
    }
    setSubmitting(true);
    try {
      const updated = await api.submitDictamen(selected, { evidence_id: evidenceId, approved, observaciones });
      await refreshQueue();
      setDetail(null);
      setEvidenceId("");
      formRef.current?.reset();
      showToast(
        approved
          ? `Evidencia aprobada. La recomendación quedó en estado ${stateLabel(updated.state)}.`
          : `Evidencia rechazada. La recomendación volvió al estado ${stateLabel(updated.state)}.`,
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
    <>
      <PageHeader
        eyebrow="Unidad de Auditoría Interna"
        title="Revisión de evidencias"
        description="Revise el PDF de respaldo y emita el dictamen. Solo una evidencia aprobada lleva la recomendación a Cumplida."
      />

      {recommendations.length === 0 ? (
        <EmptyState title="No hay evidencias pendientes de revisión">
          <p>Las recomendaciones aparecen aquí cuando el ejecutor carga una evidencia.</p>
        </EmptyState>
      ) : (
        <div className="split">
          <section className="card" aria-labelledby="cola-title">
            <div className="card-header">
              <div>
                <h2 id="cola-title">Pendientes de dictamen</h2>
                <p>{recommendations.length} en validación</p>
              </div>
            </div>
            <RecommendationQueue
              items={recommendations}
              selected={selected}
              onSelect={setSelected}
              label="Recomendaciones en validación"
            />
          </section>

          <section className="card" aria-labelledby="revision-title" aria-busy={loading}>
            {loading || !detail ? (
              <p role="status" className="muted">
                Cargando evidencias...
              </p>
            ) : (
              <>
                <div className="card-header">
                  <div>
                    <p className="eyebrow">Recomendación {detail.number}</p>
                    <h2 id="revision-title">{detail.description}</h2>
                  </div>
                  <RecommendationBadges item={detail} />
                </div>
                <dl className="detail-meta">
                  <div>
                    <dt>Unidad</dt>
                    <dd>{detail.unit_id}</dd>
                  </div>
                  <div>
                    <dt>Vence</dt>
                    <dd>{formatDate(detail.due_date)}</dd>
                  </div>
                  <div>
                    <dt>Evidencias</dt>
                    <dd>{detail.evidencias.length}</dd>
                  </div>
                </dl>

                <h3>Evidencias adjuntas</h3>
                {detail.evidencias.length === 0 ? (
                  <p className="muted">No hay evidencias adjuntas.</p>
                ) : (
                  <ul className="evidence-list">
                    {detail.evidencias.map((item) => (
                      <li key={item.id}>
                        <div>
                          <strong>{item.filename}</strong>
                          <small className="muted">
                            {item.type ?? "Evidencia"} · {formatSize(item.size_bytes)} · {formatDateTime(item.uploaded_at)}
                            {" · "}
                            {item.status === "ANULADA" ? "Anulada" : item.validated ? "Validada" : "Pendiente"}
                          </small>
                          <small className="hash">SHA-256: {item.sha256}</small>
                        </div>
                        <div className="actions">
                          <button type="button" className="secondary" onClick={() => openEvidence(item, "inline")}>
                            Vista previa
                          </button>
                          <button type="button" className="ghost" onClick={() => openEvidence(item, "attachment")}>
                            Descargar
                          </button>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}

                {selectableEvidence.length > 0 && detail.state === REVIEW_STATE ? (
                  <div className="decision">
                    <h3>Dictamen UAI</h3>
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
                    <form ref={formRef}>
                      <label>
                        Observaciones
                        <textarea
                          name="observaciones"
                          rows={3}
                          placeholder="Obligatorias al rechazar: indique qué debe corregir el ejecutor."
                        />
                      </label>
                    </form>
                    <div className="actions">
                      <button
                        type="button"
                        onClick={() => submitDictamen(true)}
                        disabled={!canIssueDecision}
                        aria-describedby="decision-help"
                      >
                        Aprobar
                      </button>
                      <button
                        type="button"
                        className="danger"
                        onClick={() => submitDictamen(false)}
                        disabled={!canIssueDecision}
                        aria-describedby="decision-help"
                      >
                        Rechazar
                      </button>
                    </div>
                    <p id="decision-help" className="hint">
                      {canIssueDecision
                        ? "Aprobar marca la evidencia como validada; rechazar devuelve la recomendación a En proceso."
                        : "Seleccione una evidencia vigente y espere a que termine la carga para emitir el dictamen."}
                    </p>
                  </div>
                ) : (
                  <Notice tone="warning">No hay evidencias vigentes disponibles para dictamen.</Notice>
                )}
              </>
            )}
          </section>
        </div>
      )}
      <Toast toast={toast} onClose={dismissToast} />
    </>
  );
}
