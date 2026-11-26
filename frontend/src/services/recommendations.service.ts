import type {
  PaginatedResult,
  Recommendation,
  RecommendationCreateRequest,
  RecommendationDetail,
  RecommendationQuery,
  RecommendationUpdateRequest,
} from "../models";
import { request, requestResult, serializeQuery } from "./apiClient";

export const recommendationsService = {
  list: async (filters: RecommendationQuery = {}): Promise<Recommendation[]> =>
    (await requestResult<Recommendation[]>("/api/v1/recomendaciones" + serializeQuery(filters))).data,

  listPage: async (filters: RecommendationQuery = {}): Promise<PaginatedResult<Recommendation>> => {
    const result = await requestResult<Recommendation[]>("/api/v1/recomendaciones" + serializeQuery(filters));
    return { items: result.data, pagination: result.meta.pagination };
  },

  get: (id: string): Promise<RecommendationDetail> =>
    request(`/api/v1/recomendaciones/${encodeURIComponent(id)}`),

  create: (payload: RecommendationCreateRequest): Promise<Recommendation> =>
    request("/api/v1/recomendaciones", { method: "POST", body: JSON.stringify(payload) }),

  update: (id: string, payload: RecommendationUpdateRequest): Promise<Recommendation> =>
    request(`/api/v1/recomendaciones/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
};
