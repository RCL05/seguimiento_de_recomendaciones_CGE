import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { api, Evidence, Recommendation } from "../../../api/client";
import { ReviewEvidencePage } from "./ReviewEvidencePage";

vi.mock("../../../api/client", () => ({
  api: {
    listRecommendations: vi.fn(),
    getRecommendation: vi.fn(),
    submitDictamen: vi.fn(),
  },
  ApiError: class ApiError extends Error {},
}));

const pending: Recommendation = {
  id: "r-1",
  report_id: "rep-1",
  number: "REC-001",
  description: "Implementar controles de inventario.",
  unit_id: "UAI",
  legal_days: 30,
  due_date: "2026-11-30",
  priority: "MEDIA",
  state: "EN_VALIDACION",
  vencida: false,
  overdue_registered_at: null,
};

const closed: Recommendation = { ...pending, id: "r-2", number: "REC-002", state: "CUMPLIDA" };

const evidence: Evidence = {
  id: "e-1",
  recommendation_id: "r-1",
  filename: "acta.pdf",
  mime_type: "application/pdf",
  size_bytes: 2048,
  sha256: "b".repeat(64),
  uploaded_at: "2026-10-26T10:00:00Z",
  uploaded_by: "user-1",
  validated: false,
  type: "FINAL",
  status: "VIGENTE",
};

describe("ReviewEvidencePage", () => {
  beforeEach(() => {
    vi.mocked(api.listRecommendations).mockReset();
    vi.mocked(api.getRecommendation).mockReset();
    vi.mocked(api.submitDictamen).mockReset();
    vi.mocked(api.listRecommendations).mockResolvedValue([pending, closed]);
    vi.mocked(api.getRecommendation).mockResolvedValue({ ...pending, evidencias: [evidence] });
  });

  it("solo muestra recomendaciones en revisión interna", async () => {
    render(<ReviewEvidencePage />);

    expect(await screen.findByRole("heading", { name: /Implementar controles/i })).toBeInTheDocument();
    expect(screen.queryByText(/REC-002/)).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /REC-001/ })).toHaveAttribute("aria-pressed", "true");
  });

  it("registra el dictamen de aprobación con la evidencia seleccionada", async () => {
    vi.mocked(api.submitDictamen).mockResolvedValue({ ...pending, state: "CUMPLIDA" });
    const user = userEvent.setup();
    render(<ReviewEvidencePage />);

    const observations = await screen.findByLabelText(/Observaciones/i);
    await user.type(observations, "Evidencia suficiente.");
    await user.click(screen.getByRole("button", { name: "Aprobar" }));

    expect(api.submitDictamen).toHaveBeenCalledWith("r-1", {
      evidence_id: "e-1",
      approved: true,
      observaciones: "Evidencia suficiente.",
    });
    expect(await screen.findByText(/quedó en estado Cumplida/i)).toBeInTheDocument();
  });

  it("registra el rechazo con observaciones", async () => {
    vi.mocked(api.submitDictamen).mockResolvedValue({ ...pending, state: "EN_PROCESO" });
    const user = userEvent.setup();
    render(<ReviewEvidencePage />);

    await user.type(await screen.findByLabelText(/Observaciones/i), "Falta firma.");
    await user.click(screen.getByRole("button", { name: /Rechazar/i }));

    expect(api.submitDictamen).toHaveBeenCalledWith("r-1", {
      evidence_id: "e-1",
      approved: false,
      observaciones: "Falta firma.",
    });
  });
});
