import { Role } from "../api/client";

export const ROLE_LABELS: Record<Role, string> = {
  UAI: "Auditoría Interna (UAI)",
  EJECUTOR: "Ejecutor de unidad",
  RECTORADO: "Rectorado",
  CGE_AUDITOR: "Auditor CGE",
  DTI: "Administración DTI",
};

export const ROLES: Role[] = ["UAI", "EJECUTOR", "RECTORADO", "CGE_AUDITOR", "DTI"];
