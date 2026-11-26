import type { Dashboard, DashboardKPIs, Health } from "../models";
import { request } from "./apiClient";

export const dashboardService = {
  get: (): Promise<Dashboard> => request("/api/v1/reportes/tablero"),
  getKPIs: (): Promise<DashboardKPIs> => request("/api/v1/dashboard/kpis"),
  getHealth: (): Promise<Health> => request("/health/"),
};
