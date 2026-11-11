import { ReactNode } from "react";

import { Role } from "./api/client";
import { NotificationSettingsPage } from "./features/administracion/pages/NotificationSettingsPage";
import { UserAdminPage } from "./features/administracion/pages/UserAdminPage";
import { AuditPage } from "./features/auditoria/pages/AuditPage";
import { DashboardKPIs } from "./features/dashboard/pages/DashboardKPIs";
import { ExecutiveDashboardPage } from "./features/dashboard/pages/ExecutiveDashboardPage";
import { ReviewEvidencePage } from "./features/evidencias/pages/ReviewEvidencePage";
import { PlanAccionPage } from "./features/planes/pages/PlanAccionPage";
import { RegistroRecomendacionPage } from "./features/recomendaciones/pages/RegistroRecomendacionPage";

export type AppRoute = {
  path: string;
  label: string;
  roles: Role[];
  page: (role: Role) => ReactNode;
};

// Los roles de cada sección coinciden con los permisos que valida el backend.
export const routes: AppRoute[] = [
  {
    path: "/tablero",
    label: "Dashboard de KPIs",
    roles: ["DTI", "UAI", "EJECUTOR", "RECTORADO", "CGE_AUDITOR"],
    // Rectorado ve el tablero ejecutivo institucional; el resto, los KPIs operativos.
    page: (role) => (role === "RECTORADO" ? <ExecutiveDashboardPage /> : <DashboardKPIs />),
  },
  { path: "/recomendaciones", label: "Recomendaciones", roles: ["UAI"], page: () => <RegistroRecomendacionPage /> },
  {
    path: "/evidencias/revisar",
    label: "Revisión de evidencias",
    roles: ["UAI"],
    page: () => <ReviewEvidencePage />,
  },
  { path: "/planes", label: "Mi bandeja", roles: ["EJECUTOR"], page: () => <PlanAccionPage /> },
  { path: "/auditoria", label: "Auditoría y matriz", roles: ["UAI", "CGE_AUDITOR"], page: () => <AuditPage /> },
  {
    path: "/administracion/notificaciones",
    label: "Notificaciones",
    roles: ["DTI"],
    page: () => <NotificationSettingsPage />,
  },
  {
    path: "/administracion/usuarios",
    label: "Usuarios y unidades",
    roles: ["DTI"],
    page: () => <UserAdminPage />,
  },
];

// Página de entrada de cada rol: su tarea principal, no siempre el primer enlace visible.
const LANDING_PATHS: Record<Role, string> = {
  UAI: "/recomendaciones",
  EJECUTOR: "/planes",
  RECTORADO: "/tablero",
  DTI: "/administracion/notificaciones",
  CGE_AUDITOR: "/tablero",
};

export function landingPath(role: Role) {
  return LANDING_PATHS[role] ?? routes.find((route) => route.roles.includes(role))?.path ?? "/";
}
