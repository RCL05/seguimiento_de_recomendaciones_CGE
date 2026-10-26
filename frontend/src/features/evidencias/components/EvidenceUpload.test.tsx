import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../../../api/client";
import { EvidenceUpload, MAX_PDF_BYTES } from "./EvidenceUpload";

vi.mock("../../../api/client", () => ({
  api: { uploadEvidence: vi.fn() },
  ApiError: class ApiError extends Error {},
}));

const uploadedEvidence = {
  id: "e-1",
  recommendation_id: "r-1",
  filename: "evidencia.pdf",
  mime_type: "application/pdf",
  size_bytes: 1200,
  sha256: "a".repeat(64),
  uploaded_at: "2026-10-26T10:00:00Z",
  validated: false,
};

describe("EvidenceUpload", () => {
  beforeEach(() => {
    vi.mocked(api.uploadEvidence).mockReset();
  });

  it("rechaza archivos que no son PDF", async () => {
    render(<EvidenceUpload recommendationId="r-1" />);

    const input = screen.getByLabelText(/Cargar evidencia PDF/i);
    fireEvent.change(input, {
      target: { files: [new File(["texto"], "nota.txt", { type: "text/plain" })] },
    });

    expect(screen.getByText("Solo se permiten archivos PDF.")).toBeInTheDocument();
    expect(api.uploadEvidence).not.toHaveBeenCalled();
  });

  it("rechaza archivos mayores a 30 MB", async () => {
    const user = userEvent.setup();
    render(<EvidenceUpload recommendationId="r-1" />);

    const oversized = new File(["x"], "grande.pdf", { type: "application/pdf" });
    Object.defineProperty(oversized, "size", { value: MAX_PDF_BYTES + 1 });
    await user.upload(screen.getByLabelText(/Cargar evidencia PDF/i), oversized);

    expect(screen.getByText(/supera el límite de 30 MB/i)).toBeInTheDocument();
    expect(api.uploadEvidence).not.toHaveBeenCalled();
  });

  it("muestra el hash cuando la carga es exitosa", async () => {
    vi.mocked(api.uploadEvidence).mockResolvedValue(uploadedEvidence);
    const user = userEvent.setup();
    const onUploaded = vi.fn();
    render(<EvidenceUpload recommendationId="r-1" onUploaded={onUploaded} />);

    const file = new File(["%PDF-1.7"], "evidencia.pdf", { type: "application/pdf" });
    await user.upload(screen.getByLabelText(/Cargar evidencia PDF/i), file);

    expect(await screen.findByText(/cargada correctamente/i)).toBeInTheDocument();
    expect(screen.getByText(new RegExp(uploadedEvidence.sha256))).toBeInTheDocument();
    expect(api.uploadEvidence).toHaveBeenCalledWith("r-1", file);
    expect(onUploaded).toHaveBeenCalledWith(uploadedEvidence);
  });
});
