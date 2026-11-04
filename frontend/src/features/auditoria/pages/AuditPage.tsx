import { useEffect, useState } from "react";

import { api, ApiError, AuditLogEntry } from "../../../api/client";

export function AuditPage() {
  const [entries, setEntries] = useState<AuditLogEntry[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .getAuditLog({ limit: 100 })
      .then(setEntries)
      .catch((caught) =>
        setError(
          caught instanceof ApiError ? caught.message : "No se pudo consultar la auditoría.",
        ),
      );
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

  return (
    <section className="card" aria-labelledby="audit-title">
      <h2 id="audit-title">Historial y matriz CGE</h2>
      <button type="button" onClick={exportMatriz}>
        Exportar matriz CSV UTF-8
      </button>
      {error && <p className="feedback error">{error}</p>}
      {entries.length === 0 ? (
        <p>No hay eventos de auditoría registrados.</p>
      ) : (
        <ul className="audit-list">
          {entries.map((entry) => (
            <li key={entry.id}>
              <strong>{entry.accion}</strong>
              <span>
                {entry.entidad}
                {entry.estado_nuevo ? ` · ${entry.estado_nuevo}` : ""}
              </span>
              <small>
                {entry.timestamp_utc} · {entry.usuario ?? "sistema"} · {entry.resultado}
              </small>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
