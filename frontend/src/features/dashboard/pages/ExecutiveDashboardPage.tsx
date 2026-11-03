import { useEffect, useState } from "react";

import { api, ApiError, Dashboard } from "../../../api/client";

const SEMAPHORE_LABEL: Record<Dashboard["semaforo_riesgo"], string> = {
  VERDE: "Cumplimiento institucional en nivel aceptable",
  AMARILLO: "Cumplimiento institucional en riesgo moderado",
  ROJO: "Cumplimiento institucional crítico",
};

export function ExecutiveDashboardPage() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .getDashboard()
      .then(setDashboard)
      .catch((caught) =>
        setError(caught instanceof ApiError ? caught.message : "No se pudo cargar el tablero."),
      );
  }, []);

  if (error) {
    return (
      <section className="card">
        <h2>Tablero ejecutivo</h2>
        <p className="feedback error">{error}</p>
      </section>
    );
  }

  if (!dashboard) {
    return (
      <section className="card">
        <h2>Tablero ejecutivo</h2>
        <p>Consultando indicadores institucionales...</p>
      </section>
    );
  }

  return (
    <section className="card" aria-labelledby="dashboard-title">
      <h2 id="dashboard-title">Tablero ejecutivo de Rectorado</h2>
      <div className={`semaphore ${dashboard.semaforo_riesgo.toLowerCase()}`}>
        <strong>{dashboard.semaforo_riesgo}</strong>
        <span>{SEMAPHORE_LABEL[dashboard.semaforo_riesgo]}</span>
      </div>

      <dl className="metrics">
        <div>
          <dt>Recomendaciones</dt>
          <dd>{dashboard.total}</dd>
        </div>
        <div>
          <dt>Cumplimiento</dt>
          <dd>{dashboard.cumplimiento_porcentaje}%</dd>
        </div>
        <div>
          <dt>En mora</dt>
          <dd>{dashboard.en_mora}</dd>
        </div>
        <div>
          <dt>En revisión interna</dt>
          <dd>{dashboard.en_revision_interna}</dd>
        </div>
      </dl>

      <h3>Distribución por estado</h3>
      {Object.keys(dashboard.por_estado).length === 0 ? (
        <p>No hay recomendaciones registradas.</p>
      ) : (
        <ul>
          {Object.entries(dashboard.por_estado).map(([state, total]) => (
            <li key={state}>
              <strong>{state}</strong>
              <span>{total}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
