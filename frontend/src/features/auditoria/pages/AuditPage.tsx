import { useEffect, useMemo, useState } from "react";

import { api, ApiError, AuditLogEntry } from "../../../api/client";
import { formatDateTime, stateLabel } from "../../../components/format";
import { EmptyState, Notice, PageHeader } from "../../../components/ui";

const ACTION_LABELS: Record<string, string> = {
  CREATE: "Registro",
  CREATE_PLAN: "Hito del plan",
  UPLOAD_EVIDENCE: "Carga de evidencia",
  ISSUE_DICTAMEN: "Dictamen UAI",
  ANULAR_EVIDENCIA: "Anulación de evidencia",
  REOPEN: "Reapertura",
  MARK_OVERDUE: "Vencimiento registrado",
  VERIFY_INTEGRITY: "Verificación de integridad",
  LOGIN_SSO: "Inicio de sesión",
  ACCESS_DENIED: "Acceso denegado",
  ASSIGN_ROLE: "Asignación de rol",
  REASSIGN_USER: "Cambio de unidad",
  MANAGE_UNIT: "Gestión de unidad",
};

export function AuditPage() {
  const [entries, setEntries] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [action, setAction] = useState("");

  useEffect(() => {
    api
      .getAuditLog({ limit: 200 })
      .then(setEntries)
      .catch((caught) =>
        setError(caught instanceof ApiError ? caught.message : "No se pudo consultar la auditoría."),
      )
      .finally(() => setLoading(false));
  }, []);

  const actions = useMemo(() => [...new Set(entries.map((entry) => entry.accion))].sort(), [entries]);
  const visible = action ? entries.filter((entry) => entry.accion === action) : entries;

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

  return (
    <>
      <PageHeader
        eyebrow="Trazabilidad"
        title="Historial y matriz CGE"
        description="Bitácora inmutable de las operaciones del sistema y exportación de la matriz institucional de cumplimiento."
        actions={
          <button type="button" onClick={exportMatriz}>
            Exportar matriz CSV UTF-8
          </button>
        }
      />
      {error && <Notice tone="error">{error}</Notice>}

      <section className="card" aria-labelledby="audit-title">
        <div className="card-header">
          <div>
            <h2 id="audit-title">Eventos de auditoría</h2>
            <p>Últimos {entries.length} eventos, del más reciente al más antiguo.</p>
          </div>
          <label>
            Operación
            <select value={action} onChange={(event) => setAction(event.target.value)}>
              <option value="">Todas</option>
              {actions.map((item) => (
                <option key={item} value={item}>
                  {ACTION_LABELS[item] ?? item}
                </option>
              ))}
            </select>
          </label>
        </div>

        {loading ? (
          <p role="status" className="muted">
            Consultando la bitácora...
          </p>
        ) : visible.length === 0 ? (
          <EmptyState title="No hay eventos de auditoría registrados" />
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Operación</th>
                  <th>Entidad</th>
                  <th>Cambio de estado</th>
                  <th>Usuario</th>
                  <th>Resultado</th>
                </tr>
              </thead>
              <tbody>
                {visible.map((entry) => (
                  <tr key={entry.id}>
                    <td className="nowrap">{formatDateTime(entry.timestamp_utc)}</td>
                    <td>
                      <div className="cell-title">{ACTION_LABELS[entry.accion] ?? entry.accion}</div>
                      <div className="cell-sub">{entry.modulo}</div>
                    </td>
                    <td>{entry.entidad}</td>
                    <td>
                      {entry.estado_anterior || entry.estado_nuevo
                        ? `${entry.estado_anterior ? stateLabel(entry.estado_anterior) : "—"} → ${
                            entry.estado_nuevo ? stateLabel(entry.estado_nuevo) : "—"
                          }`
                        : "—"}
                    </td>
                    <td>{entry.usuario ?? "Sistema"}</td>
                    <td>
                      <span className={`badge ${entry.resultado === "OK" ? "state-cumplida" : "danger"}`}>
                        {entry.resultado === "OK" ? "Correcto" : entry.resultado}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}
