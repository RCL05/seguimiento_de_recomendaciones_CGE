import type { AuditLogEntry, AuditQuery } from "../models";
import { request, requestBlob } from "./apiClient";

export const auditService = {
  list: (filters: AuditQuery = {}): Promise<AuditLogEntry[]> => {
    const params = new URLSearchParams();
    for (const [key, value] of Object.entries(filters)) {
      if (value !== undefined && value !== "") params.set(key, String(value));
    }
    const query = params.toString();
    return request(`/api/v1/auditoria${query ? `?${query}` : ""}`);
  },

  downloadMatrix: (): Promise<Blob> => requestBlob("/api/v1/reportes/matriz-cge"),
};
