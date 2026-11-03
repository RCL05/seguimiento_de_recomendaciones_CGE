import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../../../api/client";
import { ReviewEvidencePage } from "./ReviewEvidencePage";

vi.mock("../../../api/client", () => ({
  api: {
    listRecommendations: vi.fn(),
    getRecommendation: vi.fn(),
    submitDictamen: vi.fn(),
  },
  ApiError: class ApiError extends Error {},
}));

const pending = {
  id: "r-1",
  report_id: "rep-1",
  number: "REC-001",
  description: "Implementar controles de inventario.",
  unit_id: "UAI",
  legal_days: 30,
  due_date: "2026-11-30",
  state: "EN_REVISION_INTERNA",
};

const closed = { ...pending, id: "r-2", number: "REC-002", state: "APROBADA" };

const evidence = {
  id: "e-1",
  recommendation_id: "r-1",
  filename: "acta.pdf",
  mime_type: "application/pdf",
  size_bytes: 2048,
  sha256: "b".repeat(64),
  uploaded_at: "2026-10-26T10:00:00Z",
  validated: false,
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

    expect(await screen.findByText(/Implementar controles/i)).toBeInTheDocument();
    expect(screen.queryByText(/REC-002/)).not.toBeInTheDocument();
    expect(screen.getByRole("option", { name: /REC-001/ })).toBeInTheDocument();
  });

  it("registra el dictamen de aprobación con la evidencia seleccionada", async () => {
    vi.mocked(api.submitDictamen).mockResolvedValue({ ...pending, state: "APROBADA" });
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
    expect(await screen.findByText(/quedó en estado APROBADA/i)).toBeInTheDocument();
  });

  it("registra el rechazo con observaciones", async () => {
    vi.mocked(api.submitDictamen).mockResolvedValue({ ...pending, state: "DEVUELTA" });
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
