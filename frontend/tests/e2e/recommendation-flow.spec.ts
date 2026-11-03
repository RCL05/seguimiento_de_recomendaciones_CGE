import { expect, test, type Page } from "@playwright/test";

function envelope<T>(data: T) {
  return {
    success: true,
    message: "ok",
    data,
    errors: null,
    meta: {
      request_id: "e2e-request",
      timestamp: "2026-10-26T10:00:00Z",
      version: "v1",
    },
  };
}

async function mockApi(page: Page) {
  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;

    if (path.endsWith("/reportes/tablero")) {
      return route.fulfill({
        json: envelope({
          total: 4,
          cumplimiento_porcentaje: 75,
          semaforo_riesgo: "AMARILLO",
          en_mora: 1,
          en_revision_interna: 2,
          por_estado: { APROBADA: 3, EN_REVISION_INTERNA: 1 },
        }),
      });
    }
    if (path.endsWith("/auditoria")) {
      return route.fulfill({ json: envelope([]) });
    }
    if (path.endsWith("/notificaciones/configuracion")) {
      return route.fulfill({
        json: envelope({
          umbral_dias: 5,
          notificaciones_activas: true,
          canal_interno_activo: true,
          canal_email_activo: false,
          destinatarios_vencimiento: ["UAI"],
          destinatarios_mora: ["UAI", "RECTORADO"],
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
      return route.fulfill({ json: envelope([]) });
    }
    return route.fulfill({ json: envelope({ id: "e2e-id", state: "REGISTRADA" }) });
  });
}

test("recorre las vistas institucionales sin errores de red", async ({ page }) => {
  await mockApi(page);
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Seguimiento de recomendaciones" })).toBeVisible();
  await expect(page.getByLabel("Número de informe")).toBeVisible();

  await page.getByLabel("Vista institucional").selectOption("EJECUTOR");
  await expect(page.getByRole("heading", { name: "Bandeja del ejecutor" })).toBeVisible();

  await page.getByLabel("Vista institucional").selectOption("RECTORADO");
  await expect(page.getByRole("heading", { name: "Tablero ejecutivo de Rectorado" })).toBeVisible();
  await expect(page.getByText("AMARILLO")).toBeVisible();

  await page.getByLabel("Vista institucional").selectOption("CGE_AUDITOR");
  await expect(page.getByRole("heading", { name: "Historial y matriz CGE" })).toBeVisible();

  await page.getByLabel("Vista institucional").selectOption("DTI");
  await expect(
    page.getByRole("heading", { name: "Configuración de notificaciones" }),
  ).toBeVisible();

  expect(errors).toEqual([]);
});
