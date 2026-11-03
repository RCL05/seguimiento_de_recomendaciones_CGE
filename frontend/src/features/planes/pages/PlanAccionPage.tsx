import { FormEvent, useEffect, useState } from "react";

import { api, ApiError, Recommendation } from "../../../api/client";
import { EvidenceUpload } from "../../evidencias/components/EvidenceUpload";

export function PlanAccionPage() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [selected, setSelected] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .listRecommendations()
      .then((items) => {
        setRecommendations(items);
        if (items.length > 0) {
          setSelected(items[0].id);
        }
      })
      .catch((caught) =>
        setError(caught instanceof ApiError ? caught.message : "No se pudo cargar la bandeja."),
      );
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");
    const form = new FormData(event.currentTarget);
    try {
      await api.createPlan(selected, {
        descripcion_hito: String(form.get("descripcion_hito")),
        fecha_compromiso: String(form.get("fecha_compromiso")),
      });
      setMessage("Hito del plan registrado correctamente.");
      event.currentTarget.reset();
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "No se pudo registrar el plan.");
    }
  }

  const current = recommendations.find((item) => item.id === selected);

  return (
    <section className="card" aria-labelledby="plan-title">
      <h2 id="plan-title">Bandeja del ejecutor</h2>
      <p>Seleccione una recomendación de su unidad, registre hitos y adjunte evidencias PDF.</p>

      {recommendations.length === 0 ? (
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
            <p className="hint">
              {current.description} · Unidad {current.unit_id}
            </p>
          )}

          <form className="form-grid" onSubmit={handleSubmit}>
            <label className="full-width">
              Descripción del hito
              <textarea name="descripcion_hito" required rows={3} />
            </label>
            <label>
              Fecha de compromiso
              <input name="fecha_compromiso" type="date" required />
            </label>
            <button type="submit">Agregar hito</button>
          </form>

          {selected && (
            <EvidenceUpload
              recommendationId={selected}
              onUploaded={(evidence) =>
                setMessage(`Evidencia cargada. SHA-256: ${evidence.sha256.slice(0, 16)}...`)
              }
            />
          )}
        </>
      )}

      {message && <p className="feedback success">{message}</p>}
      {error && <p className="feedback error">{error}</p>}
    </section>
  );
}
