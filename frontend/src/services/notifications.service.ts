import type {
  Notification,
  NotificationPreference,
  NotificationSettings,
  NotificationSettingsUpdateRequest,
  Preferences,
  PreferencesUpdateRequest,
} from "../models";
import { request, serializeQuery } from "./apiClient";

export const notificationsService = {
  list: (): Promise<Notification[]> => request("/api/v1/notificaciones"),

  getPreferences: (usuarioId?: string): Promise<Preferences> =>
    request(`/api/v1/notificaciones/preferencias${serializeQuery({ usuario_id: usuarioId })}`),

  updatePreferences: (preferences: NotificationPreference[]): Promise<Preferences> =>
    request("/api/v1/notificaciones/preferencias", {
      method: "PUT",
      body: JSON.stringify({ preferencias: preferences } satisfies Pick<PreferencesUpdateRequest, "preferencias">),
    }),

  getSettings: (): Promise<NotificationSettings> =>
    request("/api/v1/notificaciones/configuracion"),

  updateSettings: (payload: NotificationSettingsUpdateRequest): Promise<NotificationSettings> =>
    request("/api/v1/notificaciones/configuracion", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
};
