import type { LoginRequest, LoginResponse, Session } from "../models";
import { request, setSession } from "./apiClient";

export const authService = {
  login: async (credential: string): Promise<Session> => {
    const payload = await request<LoginResponse>("/api/v1/sesiones", {
      method: "POST",
      body: JSON.stringify({ credential } satisfies LoginRequest),
    });
    return setSession(payload);
  },
};
