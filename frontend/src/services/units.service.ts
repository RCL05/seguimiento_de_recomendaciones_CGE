import type { Unit, UnitCreateRequest } from "../models";
import { request } from "./apiClient";

export const unitsService = {
  list: (): Promise<Unit[]> => request("/api/v1/unidades"),

  create: (payload: UnitCreateRequest): Promise<Unit> =>
    request("/api/v1/unidades", { method: "POST", body: JSON.stringify(payload) }),
};
