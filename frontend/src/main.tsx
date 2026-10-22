import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

type Recommendation = {
  id: string;
  number: string;
  description: string;
  unit_id: string;
  state: string;
  due_date: string;
};

function App() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [role, setRole] = useState("UAI");

  useEffect(() => {
    fetch("/api/v1/recomendaciones")
      .then((response) => response.json())
      .then((body) => setRecommendations(body.data ?? []))
      .catch(() => setRecommendations([]));
  }, []);

  return (
    <main>
      <header>
        <p className="eyebrow">SITRA-CGE UNL</p>
        <h1>Seguimiento de recomendaciones</h1>
        <p>Consulta el estado, responsable y vencimiento de cada recomendación institucional.</p>
        <label>
          Vista institucional
          <select value={role} onChange={(event) => setRole(event.target.value)}>
            <option value="DTI">DTI · Administración</option>
            <option value="UAI">UAI · Revisión</option>
            <option value="EJECUTOR">Ejecutor · Evidencias</option>
            <option value="RECTORADO">Rectorado · Tablero</option>
            <option value="CGE_AUDITOR">Auditor CGE · Auditoría</option>
          </select>
        </label>
      </header>
      <section className="card role-panel">
        <h2>{roleLabel(role)}</h2>
        <p>{roleDescription(role)}</p>
        <div className="actions">
          {role === "UAI" && <button type="button">Registrar informe</button>}
          {role === "EJECUTOR" && <button type="button">Crear plan y cargar evidencia</button>}
          {role === "RECTORADO" && <button type="button">Consultar tablero de riesgos</button>}
          {role === "CGE_AUDITOR" && <button type="button">Ver historial y exportar CSV</button>}
          {role === "DTI" && <button type="button">Administrar usuarios y unidades</button>}
        </div>
      </section>
      <section className="card" aria-labelledby="recommendations-title">
        <h2 id="recommendations-title">Recomendaciones</h2>
        {recommendations.length === 0 ? (
          <p>No hay recomendaciones registradas.</p>
        ) : (
          <ul>
            {recommendations.map((item) => (
              <li key={item.id}>
                <strong>{item.number}</strong>
                <span>{item.description}</span>
                <small>{item.state} · {item.unit_id} · vence {item.due_date}</small>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}

function roleLabel(role: string) {
  return {
    DTI: "Panel DTI",
    UAI: "Panel UAI",
    EJECUTOR: "Panel del Ejecutor",
    RECTORADO: "Tablero de Rectorado",
    CGE_AUDITOR: "Panel del Auditor CGE",
  }[role] ?? "Panel institucional";
}

function roleDescription(role: string) {
  return {
    DTI: "Gestiona cuentas, roles, unidades y configuración institucional.",
    UAI: "Registra recomendaciones, revisa evidencias y emite dictámenes.",
    EJECUTOR: "Gestiona planes, hitos, evidencias y correcciones de su unidad.",
    RECTORADO: "Supervisa cumplimiento, riesgos y recomendaciones en mora.",
    CGE_AUDITOR: "Consulta la trazabilidad, integridad y matriz institucional.",
  }[role] ?? "";
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
