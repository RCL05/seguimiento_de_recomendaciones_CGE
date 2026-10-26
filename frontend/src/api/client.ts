export type Role = "DTI" | "UAI" | "EJECUTOR" | "RECTORADO" | "CGE_AUDITOR";

export type Session = {
  role: Role;
  userId: string;
  unitId?: string;
};

export type Recommendation = {
  id: string;
  report_id: string;
  number: string;
  description: string;
  unit_id: string;
  legal_days: number;
  due_date: string;
  state: string;
};

export type Evidence = {
  id: string;
  recommendation_id: string;
  filename: string;
  mime_type: string;
  size_bytes: number;
  sha256: string;
  uploaded_at: string;
  validated: boolean;
};

export type RecommendationDetail = Recommendation & { evidencias: Evidence[] };

export type Dashboard = {
  total: number;
  cumplimiento_porcentaje: number;
  semaforo_riesgo: "VERDE" | "AMARILLO" | "ROJO";
  en_mora: number;
  en_revision_interna: number;
  por_estado: Record<string, number>;
};

export type AuditLogEntry = {
  id: string;
  request_id: string;
  timestamp_utc: string;
  usuario: string | null;
  modulo: string;
  accion: string;
  entidad: string;
  entidad_id: string | null;
  estado_anterior: string | null;
  estado_nuevo: string | null;
  resultado: string;
};

export type NotificationPreference = {
  id: string | null;
  usuario_id: string;
  tipo_alerta: "ALERTA_VENCIMIENTO" | "EN_MORA";
  notificar_interno: boolean;
  notificar_email: boolean;
  activo: boolean;
};

export type NotificationSettings = {
  umbral_dias: number;
  notificaciones_activas: boolean;
  canal_interno_activo: boolean;
  canal_email_activo: boolean;
  destinatarios_vencimiento: string[];
  destinatarios_mora: string[];
};

type Envelope<T> = {
  success: boolean;
  message: string;
  data: T;
  errors: { code?: string; detail?: string } | null;
  meta: { request_id: string; timestamp: string; version: string };
};

export class ApiError extends Error {
  code: string;
  status: number;

  constructor(message: string, code = "INTERNAL_ERROR", status = 500) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
  }
}

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

let session: Session = { role: "UAI", userId: "demo-uai", unitId: "UAI" };

export function setSession(next: Partial<Session>) {
  session = { ...session, ...next };
}

export function getSession(): Session {
  return session;
}

function authHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    "X-Role": session.role,
    "X-User-ID": session.userId,
  };
  if (session.unitId) {
    headers["X-Unit-ID"] = session.unitId;
  }
  return headers;
}

async function parseResponse<T>(response: Response): Promise<T> {
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) {
    if (!response.ok) {
      throw new ApiError(`Error HTTP ${response.status}`, "INTERNAL_ERROR", response.status);
    }
    return undefined as T;
  }
  const body = (await response.json()) as Envelope<T>;
  if (!response.ok || !body.success) {
    throw new ApiError(
      body.errors?.detail ?? body.message ?? "Error inesperado",
      body.errors?.code ?? "INTERNAL_ERROR",
      response.status,
    );
  }
  return body.data;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  for (const [key, value] of Object.entries(authHeaders())) {
    headers.set(key, value);
  }
  if (init.body && !(init.body instanceof Blob) && !(init.body instanceof File)) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers });
  return parseResponse<T>(response);
}

export const api = {
  listRecommendations: () => request<Recommendation[]>("/api/v1/recomendaciones"),

  getRecommendation: (id: string) => request<RecommendationDetail>(`/api/v1/recomendaciones/${id}`),

  createReport: (payload: {
    numero_informe: string;
    periodo_auditado: string;
    fecha_notificacion: string;
    pdf_informe_url: string;
  }) =>
    request<{ id: string }>("/api/v1/informes", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  createRecommendation: (payload: {
    report_id: string;
    number: string;
    description: string;
    unit_id: string;
    legal_days: number;
    due_date: string;
    priority?: string;
  }) =>
    request<Recommendation>("/api/v1/recomendaciones", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  createPlan: (
    recommendationId: string,
    payload: { descripcion_hito: string; fecha_compromiso: string },
  ) =>
    request<{ id: string; recommendation_id: string }>(
      `/api/v1/recomendaciones/${recommendationId}/plan-accion`,
      { method: "POST", body: JSON.stringify(payload) },
    ),

  uploadEvidence: async (recommendationId: string, file: File): Promise<Evidence> => {
    const response = await fetch(
      `${API_BASE}/api/v1/recomendaciones/${recommendationId}/evidencias`,
      {
        method: "POST",
        headers: { ...authHeaders(), "X-Filename": file.name },
        body: file,
      },
    );
    return parseResponse<Evidence>(response);
  },

  submitDictamen: (
    recommendationId: string,
    payload: { evidence_id: string; approved: boolean; observaciones?: string },
  ) =>
    request<Recommendation>(`/api/v1/recomendaciones/${recommendationId}/dictamen`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  getDashboard: () => request<Dashboard>("/api/v1/reportes/tablero"),

  getAuditLog: (filters: { entity?: string; entity_id?: string; limit?: number } = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== "") {
        params.set(key, String(value));
      }
    });
    const query = params.toString();
    return request<AuditLogEntry[]>(`/api/v1/auditoria${query ? `?${query}` : ""}`);
  },

  downloadMatriz: async (): Promise<Blob> => {
    const response = await fetch(`${API_BASE}/api/v1/reportes/matriz-cge`, {
      method: "POST",
      headers: authHeaders(),
    });
    if (!response.ok) {
      throw new ApiError("No se pudo exportar la matriz CGE.", "FORBIDDEN", response.status);
    }
    return response.blob();
  },

  getPreferences: (usuarioId?: string) => {
    const query = usuarioId ? `?usuario_id=${encodeURIComponent(usuarioId)}` : "";
    return request<{ usuario_id: string; preferencias: NotificationPreference[] }>(
      `/api/v1/notificaciones/preferencias${query}`,
    );
  },

  updatePreferences: (preferences: Partial<NotificationPreference>[]) =>
    request<{ usuario_id: string; preferencias: NotificationPreference[] }>(
      "/api/v1/notificaciones/preferencias",
      { method: "PUT", body: JSON.stringify({ preferencias: preferences }) },
    ),

  getNotificationSettings: () =>
    request<NotificationSettings>("/api/v1/notificaciones/configuracion"),

  updateNotificationSettings: (payload: Partial<NotificationSettings>) =>
    request<NotificationSettings>("/api/v1/notificaciones/configuracion", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
};
