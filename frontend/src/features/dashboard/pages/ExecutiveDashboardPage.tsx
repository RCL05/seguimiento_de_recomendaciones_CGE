import { useEffect, useState } from "react";

import { api, ApiError, Dashboard } from "../../../api/client";
import { formatDate, STATE_OPTIONS } from "../../../components/format";
import { EmptyState, Notice, PageHeader } from "../../../components/ui";

const SEMAPHORE: Record<Dashboard["semaforo_riesgo"], { icon: string; title: string; text: string }> = {
  VERDE: { icon: "✓", title: "Riesgo bajo", text: "El cumplimiento institucional está en un nivel aceptable (≥ 75 %)." },
  AMARILLO: { icon: "!", title: "Riesgo moderado", text: "El cumplimiento está entre 40 % y 75 %: conviene priorizar seguimientos." },
  ROJO: { icon: "×", title: "Riesgo crítico", text: "Menos del 40 % de las recomendaciones está cumplido." },
};

export function ExecutiveDashboardPage() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .getDashboard()
      .then(setDashboard)
      .catch((caught) => setError(caught instanceof ApiError ? caught.message : "No se pudo cargar el tablero."));
  }, []);

  async function exportMatriz() {
    try {
      const blob = await api.downloadMatriz();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "matriz-cge.csv";
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "No se pudo exportar la matriz.");
    }
  }

  const header = (
    <PageHeader
      eyebrow="Supervisión institucional"
      title="Tablero ejecutivo"
      description="Estado del cumplimiento de las recomendaciones de la Contraloría y unidades con plazos vencidos."
      actions={
        <button type="button" className="secondary" onClick={exportMatriz}>
          Exportar matriz CSV
        </button>
      }
    />
  );

  if (error) {
    return (
      <>
        {header}
        <Notice tone="error">{error}</Notice>
      </>
    );
  }

  if (!dashboard) {
    return (
      <>
        {header}
        <p role="status" className="muted">
          Consultando indicadores institucionales...
        </p>
      </>
    );
  }

  const semaphore = SEMAPHORE[dashboard.semaforo_riesgo];
  // Orden fijo del flujo; los estados sin recomendaciones se muestran con 0.
  const distribution = STATE_OPTIONS.map((option) => ({
    ...option,
    total: dashboard.por_estado[option.value] ?? 0,
  }));
  const maxTotal = Math.max(1, ...distribution.map((item) => item.total));

  return (
    <>
      {header}

      <div className={`semaphore ${dashboard.semaforo_riesgo.toLowerCase()}`} role="status">
        <span className="semaphore-light" aria-hidden="true">
          {semaphore.icon}
        </span>
        <div>
          <strong>
            Semáforo {dashboard.semaforo_riesgo.toLowerCase()} · {semaphore.title}
          </strong>
          <span>{semaphore.text}</span>
        </div>
      </div>

      <dl className="kpis">
        <div className="kpi">
          <dt>Recomendaciones</dt>
          <dd>{dashboard.total}</dd>
          <small>registradas en el sistema</small>
        </div>
        <div className="kpi">
          <dt>Cumplimiento</dt>
          <dd>{dashboard.cumplimiento_porcentaje}%</dd>
          <small>{dashboard.por_estado.CUMPLIDA ?? 0} cumplidas</small>
        </div>
        <div className="kpi">
          <dt>Vencidas</dt>
          <dd>{dashboard.en_mora}</dd>
          <small>plazo legal expirado sin cumplir</small>
        </div>
        <div className="kpi">
          <dt>En validación UAI</dt>
          <dd>{dashboard.en_revision_interna}</dd>
          <small>evidencias pendientes de dictamen</small>
        </div>
      </dl>

      <div className="split">
        <section className="card" aria-labelledby="estado-title">
          <div className="card-header">
            <div>
              <h2 id="estado-title">Recomendaciones por estado</h2>
              <p>Corte al {formatDate(dashboard.fecha_corte)}</p>
            </div>
          </div>
          {dashboard.total === 0 ? (
            <EmptyState title="Sin recomendaciones registradas" />
          ) : (
            <ul className="bar-chart" aria-label="Recomendaciones por estado">
              {distribution.map((item) => (
                <li
                  key={item.value}
                  className="bar-row"
                  title={`${item.label}: ${item.total} de ${dashboard.total}`}
                >
                  <span className="bar-label">{item.label}</span>
                  <span className="bar-track" aria-hidden="true">
                    <span
                      className="bar-fill"
                      style={{ width: item.total ? `${(item.total / maxTotal) * 100}%` : 0, display: "block" }}
                    />
                  </span>
                  <span className="bar-value">{item.total}</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="card" aria-labelledby="mora-title">
          <div className="card-header">
            <div>
              <h2 id="mora-title">Unidades en mora</h2>
              <p>Unidades con recomendaciones vencidas, de mayor a menor.</p>
            </div>
          </div>
          {dashboard.unidades_en_mora.length === 0 ? (
            <EmptyState title="Ninguna unidad en mora">
              <p>Todas las recomendaciones están dentro de su plazo legal o cumplidas.</p>
            </EmptyState>
          ) : (
            <div className="table-wrap">
              <table aria-label="Unidades en mora">
                <thead>
                  <tr>
                    <th>Unidad</th>
                    <th className="num">Vencidas</th>
                    <th className="num">Total</th>
                    <th className="num">% vencido</th>
                  </tr>
                </thead>
                <tbody>
                  {dashboard.unidades_en_mora.map((unidad) => (
                    <tr key={unidad.unidad_codigo}>
                      <td>
                        <div className="cell-title">{unidad.unidad_codigo}</div>
                        <div className="cell-sub">{unidad.unidad_nombre}</div>
                      </td>
                      <td className="num">{unidad.vencidas}</td>
                      <td className="num">{unidad.total}</td>
                      <td className="num">{Math.round((unidad.vencidas / unidad.total) * 100)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
      <p className="hint" style={{ marginTop: "1rem" }}>
        “Vencida” es un indicador de plazo, no un estado: una recomendación vencida conserva su estado de cumplimiento.
      </p>
    </>
  );
}
