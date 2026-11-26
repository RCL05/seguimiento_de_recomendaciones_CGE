import type { AdminUser, Role, UserUpdateRequest } from "../models";
import { request } from "./apiClient";

export const usersService = {
  list: (): Promise<AdminUser[]> => request("/api/v1/usuarios"),

  update: (userId: string, payload: UserUpdateRequest): Promise<AdminUser> =>
    request(`/api/v1/usuarios/${encodeURIComponent(userId)}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
};

export type { Role };
