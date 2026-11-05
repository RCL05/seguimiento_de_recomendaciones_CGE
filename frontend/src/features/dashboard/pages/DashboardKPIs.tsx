import { useCallback, useEffect, useState } from "react";

import { api, ApiError, DashboardKPIs as DashboardKPIsData } from "../../../api/client";
import { stateLabel, STATE_OPTIONS } from "../../../components/format";
import { Notice, PageHeader } from "../../../components/ui";

export function DashboardKPIs() {
  const [metrics, setMetrics] = useState<DashboardKPIsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setMetrics(await api.getDashboardKPIs());
    } catch (caught) {
      setError(
        caught instanceof ApiError ? caught.message : "No se pudieron cargar los indicadores.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const handleRefresh = () => void refresh();
    window.addEventListener("sitra:dashboard-refresh", handleRefresh);
    return () => window.removeEventListener("sitra:dashboard-refresh", handleRefresh);
  }, [refresh]);

  const percentage = Math.min(100, Math.max(0, metrics?.tasa_cumplimiento_porcentaje ?? 0));

  return (
    <>
      <PageHeader
        eyebrow="Supervisión institucional"
        title="Dashboard de KPIs"
        description="Indicadores consolidados del seguimiento de recomendaciones de la Contraloría."
        actions={
          <button
            type="button"
            className="secondary refresh-button"
            onClick={() => void refresh()}
            disabled={loading}
          >
            <span aria-hidden="true">↻</span> {loading ? "Actualizando..." : "Actualizar métricas"}
          </button>
        }
      />

      {error && (
        <Notice tone="error">
          {error}{" "}
          <button type="button" className="ghost inline-action" onClick={() => void refresh()}>
            Reintentar
          </button>
        </Notice>
      )}

      <div className="kpi-dashboard" aria-busy={loading}>
        <section className="kpi-card kpi-card-primary" aria-labelledby="total-recomendaciones">
          <div className="kpi-card-heading">
            <span className="kpi-icon" aria-hidden="true">
              R
            </span>
            <span className="kpi-label">Total de recomendaciones</span>
          </div>
          <strong id="total-recomendaciones" className="kpi-value">
            {metrics?.total_recomendaciones ?? "—"}
          </strong>
          <div className="kpi-badges" aria-label="Desglose por estado">
            {STATE_OPTIONS.map((state) => (
              <span className={`kpi-badge status-${state.value.toLowerCase()}`} key={state.value}>
                {stateLabel(state.value)}{" "}
                <strong>{metrics?.recomendaciones_por_estado[state.value] ?? 0}</strong>
              </span>
            ))}
          </div>
        </section>

        <section className="kpi-card" aria-labelledby="cumplimiento-institucional">
          <div className="kpi-card-heading">
            <span className="kpi-icon kpi-icon-success" aria-hidden="true">
              %
            </span>
            <span className="kpi-label">Cumplimiento institucional</span>
          </div>
          <strong id="cumplimiento-institucional" className="kpi-value">
            {metrics ? `${percentage}%` : "—"}
          </strong>
          <div
            className="progress-track"
            role="progressbar"
            aria-valuenow={percentage}
            aria-valuemin={0}
            aria-valuemax={100}
          >
            <span className="progress-fill" style={{ width: `${percentage}%` }} />
          </div>
          <p className="kpi-support">Recomendaciones con evidencia aprobada</p>
        </section>

        <section
          className={`kpi-card ${metrics?.recomendaciones_vencidas_o_en_mora ? "kpi-card-alert" : ""}`}
          aria-labelledby="alertas-vencimiento"
        >
          <div className="kpi-card-heading">
            <span className="kpi-icon kpi-icon-alert" aria-hidden="true">
              !
            </span>
            <span className="kpi-label">Alertas de vencimiento</span>
          </div>
          <strong id="alertas-vencimiento" className="kpi-value">
            {metrics?.recomendaciones_vencidas_o_en_mora ?? "—"}
          </strong>
          <p className="kpi-support">
            {metrics?.recomendaciones_vencidas_o_en_mora
              ? "Recomendaciones en mora requieren atención."
              : "No hay recomendaciones vencidas."}
          </p>
        </section>

        <section className="kpi-card" aria-labelledby="informes-auditados">
          <div className="kpi-card-heading">
            <span className="kpi-icon kpi-icon-info" aria-hidden="true">
              C
            </span>
            <span className="kpi-label">Informes CGE auditados</span>
          </div>
          <strong id="informes-auditados" className="kpi-value">
            {metrics?.total_informes_cge ?? "—"}
          </strong>
          <p className="kpi-support">Informes registrados y trazables en el sistema</p>
        </section>
      </div>
    </>
  );
}
