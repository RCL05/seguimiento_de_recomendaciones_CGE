import { FormEvent, useEffect, useRef, useState } from "react";

import { api, ApiError, Evidence, Recommendation, RecommendationDetail } from "../../../api/client";

const REVIEW_STATE = "EN_REVISION_INTERNA";

export function ReviewEvidencePage() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [selected, setSelected] = useState("");
  const [detail, setDetail] = useState<RecommendationDetail | null>(null);
  const [evidenceId, setEvidenceId] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    api
      .listRecommendations()
      .then((items) => {
        const pending = items.filter((item) => item.state === REVIEW_STATE);
        setRecommendations(pending);
        if (pending.length > 0) {
          setSelected(pending[0].id);
        }
      })
      .catch((caught) =>
        setError(caught instanceof ApiError ? caught.message : "No se pudo cargar la revisión."),
      );
  }, []);

  useEffect(() => {
    if (!selected) {
      setDetail(null);
      setEvidenceId("");
      return;
    }
    api
      .getRecommendation(selected)
      .then((item) => {
        setDetail(item);
        const evidence = item.evidencias.find((candidate) => !candidate.validated);
        setEvidenceId(evidence?.id ?? item.evidencias[0]?.id ?? "");
      })
      .catch((caught) =>
        setError(caught instanceof ApiError ? caught.message : "No se pudo cargar la evidencia."),
      );
  }, [selected]);

  async function handleDictamen(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await submitDictamen(true);
  }

  async function submitDictamen(approved: boolean) {
    setError("");
    setMessage("");
    const form = formRef.current ? new FormData(formRef.current) : new FormData();
    try {
      const updated = await api.submitDictamen(selected, {
        evidence_id: evidenceId,
        approved,
        observaciones: String(form.get("observaciones") ?? ""),
      });
      setMessage(
        approved
          ? `Evidencia aprobada. La recomendación quedó en estado ${updated.state}.`
          : `Evidencia devuelta. La recomendación quedó en estado ${updated.state}.`,
      );
      setRecommendations((items) => items.filter((item) => item.id !== selected));
      setSelected("");
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "No se pudo registrar el dictamen.");
    }
  }

  function selectedEvidence(): Evidence | undefined {
    return detail?.evidencias.find((item) => item.id === evidenceId);
  }

  return (
    <section className="card" aria-labelledby="revision-title">
      <h2 id="revision-title">Revisión UAI de evidencias</h2>
      <p>La UAI aprueba o rechaza la evidencia con observaciones oficiales.</p>

      {recommendations.length === 0 ? (
        <p>No hay recomendaciones en revisión interna.</p>
      ) : (
        <>
          <label>
            Recomendación en revisión
            <select value={selected} onChange={(event) => setSelected(event.target.value)}>
              {recommendations.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.number} · {item.unit_id}
                </option>
              ))}
            </select>
          </label>

          {detail && (
            <div className="detail">
              <p>{detail.description}</p>
              {detail.evidencias.length === 0 ? (
                <p>No hay evidencias cargadas para esta recomendación.</p>
              ) : (
                <label>
                  Evidencia
                  <select
                    value={evidenceId}
                    onChange={(event) => setEvidenceId(event.target.value)}
                  >
                    {detail.evidencias.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.filename} · {item.validated ? "validada" : "pendiente"}
                      </option>
                    ))}
                  </select>
                </label>
              )}
              {selectedEvidence() && (
                <p className="hash" title={selectedEvidence()!.sha256}>
                  SHA-256: {selectedEvidence()!.sha256}
                </p>
              )}
            </div>
          )}

          <form ref={formRef} className="form-grid" onSubmit={handleDictamen}>
            <label className="full-width">
              Observaciones
              <textarea name="observaciones" rows={3} placeholder="Obligatorias al rechazar" />
            </label>
            <div className="actions">
              <button type="button" onClick={() => submitDictamen(true)} disabled={!evidenceId}>
                Aprobar
              </button>
              <button
                type="button"
                className="secondary"
                onClick={() => submitDictamen(false)}
                disabled={!evidenceId}
              >
                Rechazar y solicitar corrección
              </button>
            </div>
          </form>
        </>
      )}

      {message && <p className="feedback success">{message}</p>}
      {error && <p className="feedback error">{error}</p>}
    </section>
  );
}
