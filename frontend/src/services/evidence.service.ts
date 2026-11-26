import type { Evidence, EvidenceCancellationRequest, EvidenceIntegrity, EvidenceType } from "../models";
import { request, requestBlob } from "./apiClient";

export const evidenceService = {
  upload: (
    recommendationId: string,
    file: File,
    evidenceType: EvidenceType = "FINAL",
  ): Promise<Evidence> => {
    const headers = new Headers({
      "X-Filename": file.name,
      "X-Evidence-Type": evidenceType,
    });
    // The API contract requires a raw application/pdf body for evidence uploads.
    return request(`/api/v1/recomendaciones/${encodeURIComponent(recommendationId)}/evidencias`, {
      method: "POST",
      headers,
      body: file,
    });
  },

  getFile: (
    evidenceId: string,
    disposition: "inline" | "attachment" = "inline",
  ): Promise<Blob> =>
    requestBlob(
      `/api/v1/evidencias/${encodeURIComponent(evidenceId)}/archivo?disposition=${disposition}`,
    ),

  cancel: (evidenceId: string, payload: EvidenceCancellationRequest): Promise<Evidence> =>
    request(`/api/v1/evidencias/${encodeURIComponent(evidenceId)}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  verifyIntegrity: (evidenceId: string): Promise<EvidenceIntegrity> =>
    request(`/api/v1/evidencias/${encodeURIComponent(evidenceId)}/integridad`),
};
