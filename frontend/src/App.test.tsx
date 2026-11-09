import type { ReactElement } from "react";
import { describe, expect, it } from "vitest";

import { DashboardKPIs } from "./features/dashboard/pages/DashboardKPIs";
import { ExecutiveDashboardPage } from "./features/dashboard/pages/ExecutiveDashboardPage";
import { NotificationSettingsPage } from "./features/administracion/pages/NotificationSettingsPage";
import { PlanAccionPage } from "./features/planes/pages/PlanAccionPage";
import { RegistroRecomendacionPage } from "./features/recomendaciones/pages/RegistroRecomendacionPage";
import { landingPath, routes } from "./routes";

function pageAt(path: string) {
  return routes.find((route) => route.path === path)!.page;
}

describe("ruteo por rol", () => {
  it("Rectorado recibe el tablero ejecutivo en /tablero", () => {
    const page = pageAt("/tablero")("RECTORADO") as ReactElement;

    expect(page.type).toBe(ExecutiveDashboardPage);
    expect(landingPath("RECTORADO")).toBe("/tablero");
  });

  it("los demás roles reciben los KPIs operativos en /tablero", () => {
    const page = pageAt("/tablero")("UAI") as ReactElement;

    expect(page.type).toBe(DashboardKPIs);
  });

  it("cada rol aterriza en su tarea principal", () => {
    expect((pageAt(landingPath("UAI"))("UAI") as ReactElement).type).toBe(RegistroRecomendacionPage);
    expect((pageAt(landingPath("EJECUTOR"))("EJECUTOR") as ReactElement).type).toBe(PlanAccionPage);
    expect((pageAt(landingPath("DTI"))("DTI") as ReactElement).type).toBe(NotificationSettingsPage);
  });
});
