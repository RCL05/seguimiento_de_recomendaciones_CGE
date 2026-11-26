import type { PageQuery, PaginatedResult, Report, ReportCreateJsonRequest } from "../models";
import { request, requestBlob, requestResult, serializeQuery } from "./apiClient";

export const reportsService = {
  list: async (query: PageQuery = {}): Promise<Report[]> =>
    (await requestResult<Report[]>("/api/v1/informes" + serializeQuery(query))).data,

  listPage: async (query: PageQuery = {}): Promise<PaginatedResult<Report>> => {
    const result = await requestResult<Report[]>("/api/v1/informes" + serializeQuery(query));
    return { items: result.data, pagination: result.meta.pagination };
  },

  create: (payload: FormData | ReportCreateJsonRequest): Promise<Report> =>
    request("/api/v1/informes", {
      method: "POST",
      body: payload instanceof FormData ? payload : JSON.stringify(payload),
    }),

  get: (reportId: string): Promise<Report> =>
    request(`/api/v1/informes/${encodeURIComponent(reportId)}`),

  downloadDocument: (reportId: string): Promise<Blob> =>
    requestBlob(`/api/v1/informes/${encodeURIComponent(reportId)}/documento`),
};
