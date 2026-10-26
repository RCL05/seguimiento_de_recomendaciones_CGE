import { useState } from "react";

import { Role, setSession } from "./api/client";
import { NotificationSettingsPage } from "./features/administracion/pages/NotificationSettingsPage";
import { AuditPage } from "./features/auditoria/pages/AuditPage";
import { ExecutiveDashboardPage } from "./features/dashboard/pages/ExecutiveDashboardPage";
import { ReviewEvidencePage } from "./features/evidencias/pages/ReviewEvidencePage";
import { PlanAccionPage } from "./features/planes/pages/PlanAccionPage";
import { RegistroRecomendacionPage } from "./features/recomendaciones/pages/RegistroRecomendacionPage";

const ROLES: { value: Role; label: string }[] = [
  { value: "DTI", label: "DTI · Administración" },
  { value: "UAI", label: "UAI · Revisión" },
  { value: "EJECUTOR", label: "Ejecutor · Evidencias" },
  { value: "RECTORADO", label: "Rectorado · Tablero" },
  { value: "CGE_AUDITOR", label: "Auditor CGE · Auditoría" },
];

export function App() {
  const [role, setRole] = useState<Role>("UAI");

  function changeRole(nextRole: Role) {
    setRole(nextRole);
    setSession({
      role: nextRole,
      userId: `demo-${nextRole.toLowerCase()}`,
      unitId: nextRole,
    });
  }

  return (
    <main>
      <header>
        <p className="eyebrow">SITRA-CGE UNL</p>
        <h1>Seguimiento de recomendaciones</h1>
        <p>
          Registre, ejecute, revise y supervise las recomendaciones emitidas por la Contraloría
          General del Estado.
        </p>
        <label>
          Vista institucional
          <select
            aria-label="Vista institucional"
            value={role}
            onChange={(event) => changeRole(event.target.value as Role)}
          >
            {ROLES.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
        </label>
      </header>

      {role === "UAI" && <RegistroRecomendacionPage />}
      {role === "UAI" && <ReviewEvidencePage />}
      {role === "EJECUTOR" && <PlanAccionPage />}
      {role === "RECTORADO" && <ExecutiveDashboardPage />}
      {role === "CGE_AUDITOR" && <AuditPage />}
      {role === "DTI" && <NotificationSettingsPage />}
    </main>
  );
}
