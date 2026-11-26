import type { Dictamen, DictamenCreateRequest, Recommendation } from "../models";
import { request } from "./apiClient";

export const dictamenesService = {
  create: async (recommendationId: string, payload: DictamenCreateRequest): Promise<Recommendation> => {
    const dictamen = await request<Dictamen>(
      `/api/v1/recomendaciones/${encodeURIComponent(recommendationId)}/dictamenes`,
      { method: "POST", body: JSON.stringify(payload) },
    );
    return dictamen.recomendacion;
  },

  get: (recommendationId: string, dictamenId: string): Promise<Dictamen> =>
    request(
      `/api/v1/recomendaciones/${encodeURIComponent(recommendationId)}/dictamenes/${encodeURIComponent(dictamenId)}`,
    ),
};
