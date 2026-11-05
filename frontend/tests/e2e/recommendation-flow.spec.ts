import { expect, test, type Page } from "@playwright/test";

type Role = "UAI" | "EJECUTOR" | "RECTORADO" | "DTI";

const TOKENS: Record<Role, string> = {
  UAI: "uai-sso-token",
  EJECUTOR: "ejecutor-sso-token",
  RECTORADO: "rectorado-sso-token",
  DTI: "dti-sso-token",
};

function envelope<T>(data: T) {
  return {
    success: true,
    message: "ok",
    data,
    errors: null,
    meta: { request_id: "e2e-request", timestamp: "2026-10-26T10:00:00Z", version: "v1", pagination: null },
  };
}

const recommendation = {
  id: "r-1",
  report_id: "rep-1",
  number: "R-01",
  description: "Actualizar el reglamento de bienes.",
  unit_id: "DEP-A",
  legal_days: 30,
  due_date: "2026-12-30",
  priority: "ALTA",
  state: "EN_PROCESO",
  vencida: false,
  overdue_registered_at: null,
};

async function mockApi(page: Page) {
  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;

    if (path.endsWith("/auth/login-sso")) {
      const credential = (request.postDataJSON() as { credential: string }).credential;
      const role = (Object.keys(TOKENS) as Role[]).find((key) => TOKENS[key] === credential) ?? "UAI";
      return route.fulfill({
        json: envelope({
          access_token: `jwt-${role}`,
          token_type: "Bearer",
          expires_in: 3600,
          user_id: `u-${role}`,
          email: `${role.toLowerCase()}@unl.edu.ec`,
          display_name: `Usuario ${role}`,
          role,
          unit_id: role === "EJECUTOR" ? "DEP-A" : role,
        }),
      });
    }
    if (path.endsWith("/reportes/tablero")) {
      return route.fulfill({
        json: envelope({
          total: 4,
          cumplimiento_porcentaje: 50,
          semaforo_riesgo: "AMARILLO",
          en_mora: 1,
          en_revision_interna: 1,
          por_estado: { CUMPLIDA: 2, EN_VALIDACION: 1, EN_PROCESO: 1 },
          unidades_en_mora: [{ unidad_codigo: "DEP-A", unidad_nombre: "Departamento A", vencidas: 1, total: 2 }],
          fecha_corte: "2026-11-05",
        }),
      });
    }
    if (path.endsWith("/auditoria")) return route.fulfill({ json: envelope([]) });
    if (path.endsWith("/unidades")) {
      return route.fulfill({ json: envelope([{ id: "u-1", codigo: "DEP-A", nombre: "Departamento A" }]) });
    }
    if (path.endsWith("/plan-accion")) return route.fulfill({ json: envelope([]) });
    if (path.endsWith("/notificaciones/configuracion")) {
      return route.fulfill({
        json: envelope({
          umbral_dias: 15,
          notificaciones_activas: true,
          canal_interno_activo: true,
          canal_email_activo: false,
          destinatarios_vencimiento: ["UAI"],
          destinatarios_mora: ["UAI", "RECTORADO"],
          actualizado_en: "2026-11-05T10:00:00Z",
        }),
      });
    }
    if (path.endsWith("/notificaciones/preferencias")) {
      return route.fulfill({
        json: envelope({
          usuario_id: "demo",
          preferencias: [
            {
              id: null,
              usuario_id: "demo",
              tipo_alerta: "ALERTA_VENCIMIENTO",
              notificar_interno: true,
              notificar_email: false,
              activo: true,
            },
          ],
        }),
      });
    }
    if (request.method() === "GET" && path.endsWith("/recomendaciones")) {
      return route.fulfill({ json: envelope([recommendation]) });
    }
    return route.fulfill({ json: envelope({}) });
  });
}

async function loginAs(page: Page, role: Role) {
  await page.goto("/login");
  await page.getByLabel("Credencial de acceso SSO").fill(TOKENS[role]);
  await page.getByRole("button", { name: "Ingresar" }).click();
}

async function logout(page: Page) {
  await page.getByRole("button", { name: "Cerrar sesión" }).click();
  await expect(page.getByRole("heading", { name: "Iniciar sesión" })).toBeVisible();
}

test("recorre las vistas de cada rol sin errores", async ({ page }) => {
  await mockApi(page);
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));

  await loginAs(page, "UAI");
  await expect(page.getByRole("heading", { name: "Recomendaciones CGE" })).toBeVisible();
  await expect(page.getByRole("cell", { name: /R-01/ })).toBeVisible();
  await page.getByRole("button", { name: "+ Nueva recomendación" }).click();
  await expect(page.getByLabel("Número de informe")).toBeVisible();
  await page.getByRole("link", { name: "Auditoría y matriz" }).click();
  await expect(page.getByRole("heading", { name: "Historial y matriz CGE" })).toBeVisible();
  await logout(page);

  await loginAs(page, "EJECUTOR");
  await expect(page.getByRole("heading", { name: "Mi bandeja" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Agregar hito" })).toBeVisible();
  await logout(page);

  await loginAs(page, "RECTORADO");
  await expect(page.getByRole("heading", { name: "Tablero ejecutivo" })).toBeVisible();
  await expect(page.getByText(/Semáforo amarillo/)).toBeVisible();
  await expect(page.getByRole("table", { name: "Unidades en mora" })).toContainText("DEP-A");
  await logout(page);

  await loginAs(page, "DTI");
  await expect(page.getByRole("heading", { name: "Configuración de notificaciones" })).toBeVisible();

  expect(errors).toEqual([]);
});
