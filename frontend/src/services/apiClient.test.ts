import { beforeEach, describe, expect, it, vi } from "vitest";

import type { ApiEnvelope, Pagination } from "../models";
import { setSession } from "./apiClient";
import { recommendationsService } from "./recommendations.service";
import { reportsService } from "./reports.service";

const mockFetch = vi.fn<typeof fetch>();

function jsonResponse<T>(data: T, pagination: Pagination | null = null): Response {
  const body: ApiEnvelope<T> = {
    success: true,
    message: "OK",
    data,
    errors: null,
    meta: {
      request_id: "request-1",
      timestamp: "2026-11-26T13:00:00Z",
      version: "v1",
      pagination,
    },
  };
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

describe("API services", () => {
  beforeEach(() => {
    mockFetch.mockReset();
    vi.stubGlobal("fetch", mockFetch);
    sessionStorage.clear();
  });

  it("adds the bearer token and exposes pagination while sending query filters", async () => {
    const pagination: Pagination = {
      page: 2,
      page_size: 10,
      total: 11,
      total_pages: 2,
      has_next: false,
      has_previous: true,
    };
    mockFetch.mockResolvedValueOnce(jsonResponse([], pagination));
    setSession({
      access_token: "access-token",
      token_type: "Bearer",
      expires_in: 3600,
      user_id: "user-1",
      email: "user@example.com",
      display_name: "Usuario",
      role: "UAI",
      unit_id: null,
    });

    const result = await recommendationsService.listPage({
      page: 2,
      page_size: 10,
      state: "EN_VALIDACION",
    });

    expect(result).toEqual({ items: [], pagination });
    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/recomendaciones?page=2&page_size=10&state=EN_VALIDACION",
      expect.any(Object),
    );
    const init = mockFetch.mock.calls[0][1];
    expect(new Headers(init?.headers).get("Authorization")).toBe("Bearer access-token");
  });

  it("keeps FormData uploads multipart without overriding the browser content type", async () => {
    mockFetch.mockResolvedValueOnce(jsonResponse({ id: "report-1" }));
    const formData = new FormData();
    formData.set("numero_informe", "INF-001");

    await reportsService.create(formData);

    const init = mockFetch.mock.calls[0][1];
    expect(init?.body).toBe(formData);
    expect(new Headers(init?.headers).has("Content-Type")).toBe(false);
  });
});
