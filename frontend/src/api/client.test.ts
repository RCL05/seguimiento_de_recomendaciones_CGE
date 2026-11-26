import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const fetchMock = vi.fn<typeof fetch>();

function jsonResponse(data: unknown, status = 200, success = true) {
  return new Response(
    JSON.stringify({
      success,
      message: success ? "ok" : "Solicitud rechazada",
      data,
      errors: success ? null : { code: "AUTHENTICATION_REQUIRED", detail: "Sesión expirada" },
      meta: { request_id: "ape6", timestamp: "2026-11-26T12:00:00Z", version: "1.0.0" },
    }),
    { status, headers: { "Content-Type": "application/json" } },
  );
}

describe("configuración del cliente HTTP", () => {
  beforeEach(() => {
    vi.resetModules();
    vi.stubEnv("VITE_API_BASE", "");
    vi.stubGlobal("fetch", fetchMock);
    fetchMock.mockReset();
    sessionStorage.clear();
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
    sessionStorage.clear();
  });

  it("usa rutas relativas cuando la base está vacía para pasar por el proxy", async () => {
    fetchMock.mockResolvedValue(jsonResponse([]));
    const { api } = await import("./client");

    await expect(api.listRecommendations()).resolves.toEqual([]);

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("/api/v1/recomendaciones");
    expect(new Headers(init?.headers).has("Authorization")).toBe(false);
  });

  it("normaliza espacios y barras finales de la base en las solicitudes JSON y binarias", async () => {
    vi.stubEnv("VITE_API_BASE", "  https://api.example.test///  ");
    fetchMock.mockResolvedValue(jsonResponse([]));
    const { api } = await import("./client");

    await api.listRecommendations();
    expect(fetchMock.mock.calls[0][0]).toBe("https://api.example.test/api/v1/recomendaciones");

    fetchMock.mockResolvedValue(new Response("csv", { status: 200 }));
    await api.downloadMatriz();
    expect(fetchMock.mock.calls[1][0]).toBe("https://api.example.test/api/v1/reportes/matriz-cge");
  });

  it("envía Bearer y JSON con la sesión vigente", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ id: "rec-1" }, 201));
    const { api, setSession } = await import("./client");
    setSession({
      access_token: "jwt-de-prueba",
      token_type: "Bearer",
      expires_in: 3600,
      user_id: "uai-1",
      email: "uai@example.test",
      display_name: "Auditor de prueba",
      role: "UAI",
    });
    const payload = {
      report_id: "informe-1",
      number: "REC-01",
      description: "Recomendación de prueba",
      unit_id: "DEP-A",
      legal_days: 30,
      due_date: "2026-12-26",
    };

    await api.createRecommendation(payload);

    const [, init] = fetchMock.mock.calls[0];
    const headers = new Headers(init?.headers);
    expect(init?.method).toBe("POST");
    expect(headers.get("Authorization")).toBe("Bearer jwt-de-prueba");
    expect(headers.get("Content-Type")).toBe("application/json");
    expect(JSON.parse(init?.body as string)).toEqual(payload);
  });

  it("deja que el navegador defina el boundary de FormData", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ id: "informe-1" }, 201));
    const { api } = await import("./client");
    const form = new FormData();
    form.append("numero_informe", "INF-01");

    await api.createReport(form);

    const [, init] = fetchMock.mock.calls[0];
    expect(init?.body).toBe(form);
    expect(new Headers(init?.headers).has("Content-Type")).toBe(false);
  });

  it("limpia la sesión y notifica una respuesta 401", async () => {
    fetchMock.mockResolvedValue(jsonResponse(null, 401, false));
    const { api, getSession, setSession } = await import("./client");
    setSession({
      access_token: "jwt-expirado-en-servidor",
      token_type: "Bearer",
      expires_in: 3600,
      user_id: "uai-1",
      email: "uai@example.test",
      display_name: "Auditor de prueba",
      role: "UAI",
    });
    const expired = vi.fn();
    window.addEventListener("sitra:session-expired", expired, { once: true });

    await expect(api.listRecommendations()).rejects.toMatchObject({
      status: 401,
      code: "AUTHENTICATION_REQUIRED",
      message: "Sesión expirada",
    });
    expect(getSession()).toBeNull();
    expect(expired).toHaveBeenCalledOnce();
  });
});
