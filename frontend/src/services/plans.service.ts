import type { Milestone, MilestoneCreateRequest } from "../models";
import { request } from "./apiClient";

export const plansService = {
  list: (recommendationId: string): Promise<Milestone[]> =>
    request(`/api/v1/recomendaciones/${encodeURIComponent(recommendationId)}/hitos`),

  create: (recommendationId: string, payload: MilestoneCreateRequest): Promise<Milestone> =>
    request(`/api/v1/recomendaciones/${encodeURIComponent(recommendationId)}/hitos`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
