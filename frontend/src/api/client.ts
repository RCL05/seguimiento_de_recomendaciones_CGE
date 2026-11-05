export type Role = "DTI" | "UAI" | "EJECUTOR" | "RECTORADO" | "CGE_AUDITOR";

export type Session = {
  accessToken: string;
  expiresAt: number;
  role: Role;
  userId: string;
  email: string;
  displayName: string;
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
  priority?: "ALTA" | "MEDIA" | "BAJA";
  state: "PENDIENTE" | "EN_PROCESO" | "EN_VALIDACION" | "REABIERTA" | "CUMPLIDA" | string;
  /** Plazo legal vencido sin cumplir: indicador, no un estado del flujo. */
  vencida?: boolean;
  overdue_registered_at?: string | null;
};

export type Milestone = {
  id: string;
  recommendation_id: string;
  descripcion_hito: string;
  fecha_compromiso: string;
  completado: boolean;
  created_by: string;
};

export type Dictamen = {
  id: string;
  resultado: "APROBADO" | "RECHAZADO";
  evidence_id: string;
  evaluator_id: string;
  observaciones: string;
  fecha_dictamen: string;
  recomendacion: Recommendation;
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
  type?: "BORRADOR" | "FINAL";
  status?: "VIGENTE" | "ANULADA";
  file_url?: string;
};

export type Unit = {
  id: string;
  codigo: string;
  nombre: string;
};

export type Report = {
  id: string;
  numero_informe: string;
  pdf_informe_url: string;
};

export type RecommendationDetail = Recommendation & { evidencias: Evidence[] };

export type Dashboard = {
  total: number;
  cumplimiento_porcentaje: number;
  semaforo_riesgo: "VERDE" | "AMARILLO" | "ROJO";
  en_mora: number;
  en_revision_interna: number;
  por_estado: Record<string, number>;
  unidades_en_mora: { unidad_codigo: string; unidad_nombre: string; vencidas: number; total: number }[];
  fecha_corte: string;
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
  actualizado_en?: string;
};

type Envelope<T> = {
  success: boolean;
  message: string;
  data: T;
  errors: { code?: string; detail?: string } | null;
  meta: {
    request_id: string;
    timestamp: string;
    version: string;
    pagination: {
      page: number;
      page_size: number;
      total: number;
      total_pages: number;
      has_next: boolean;
      has_previous: boolean;
    } | null;
  };
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
const SESSION_KEY = "sitra.session";

type LoginResponse = {
  access_token: string;
  token_type: "Bearer";
  expires_in: number;
  user_id: string;
  email: string;
  display_name: string;
  role: Role;
  unit_id?: string | null;
};

export function getSession(): Session | null {
  const stored = sessionStorage.getItem(SESSION_KEY);
  if (!stored) return null;
  try {
    const session = JSON.parse(stored) as Session;
    if (!session.accessToken || session.expiresAt <= Date.now()) {
      clearSession();
      return null;
    }
    return session;
  } catch {
    clearSession();
    return null;
  }
}

export function setSession(response: LoginResponse): Session {
  const session: Session = {
    accessToken: response.access_token,
    expiresAt: Date.now() + response.expires_in * 1000,
    role: response.role,
    userId: response.user_id,
    email: response.email,
    displayName: response.display_name,
    unitId: response.unit_id ?? undefined,
  };
  sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
  return session;
}

export function clearSession() {
  sessionStorage.removeItem(SESSION_KEY);
}

function authHeaders(): Record<string, string> {
  const session = getSession();
  return session ? { Authorization: `Bearer ${session.accessToken}` } : {};
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (response.status === 401) {
    clearSession();
    window.dispatchEvent(new Event("sitra:session-expired"));
  }
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
  if (
    init.body &&
    !(init.body instanceof Blob) &&
    !(init.body instanceof File) &&
    !(init.body instanceof FormData)
  ) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers });
  return parseResponse<T>(response);
}

export const api = {
  login: async (credential: string): Promise<Session> => {
    const response = await fetch(`${API_BASE}/api/v1/auth/login-sso`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ credential }),
    });
    const payload = await parseResponse<LoginResponse>(response);
    return setSession(payload);
  },

  listRecommendations: () => request<Recommendation[]>("/api/v1/recomendaciones"),

  listUnits: () => request<Unit[]>("/api/v1/unidades"),

  getRecommendation: (id: string) => request<RecommendationDetail>(`/api/v1/recomendaciones/${id}`),

  createReport: (payload: FormData) =>
    request<Report>("/api/v1/informes", {
      method: "POST",
      body: payload,
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

  listPlan: (recommendationId: string) =>
    request<Milestone[]>(`/api/v1/recomendaciones/${recommendationId}/plan-accion`),

  createPlan: (
    recommendationId: string,
    payload: { descripcion_hito: string; fecha_compromiso: string },
  ) =>
    request<{ id: string; recommendation_id: string }>(
      `/api/v1/recomendaciones/${recommendationId}/plan-accion`,
      { method: "POST", body: JSON.stringify(payload) },
    ),

  uploadEvidence: async (
    recommendationId: string,
    file: File,
    evidenceType: Evidence["type"] = "FINAL",
  ): Promise<Evidence> => {
    const response = await fetch(
      `${API_BASE}/api/v1/recomendaciones/${recommendationId}/evidencias`,
      {
        method: "POST",
        headers: {
          ...authHeaders(),
          "X-Filename": file.name,
          "X-Evidence-Type": evidenceType,
        },
        body: file,
      },
    );
    return parseResponse<Evidence>(response);
  },

  getEvidenceFile: async (evidenceId: string, disposition: "inline" | "attachment" = "inline") => {
    const response = await fetch(
      `${API_BASE}/api/v1/evidencias/${evidenceId}/archivo?disposition=${disposition}`,
      { headers: authHeaders() },
    );
    if (!response.ok) {
      await parseResponse<never>(response);
      throw new ApiError("No se pudo abrir la evidencia.", "INTERNAL_ERROR", response.status);
    }
    return response.blob();
  },

  submitDictamen: async (
    recommendationId: string,
    payload: { evidence_id: string; approved: boolean; observaciones?: string },
  ): Promise<Recommendation> => {
    // El dictamen es un recurso nuevo: POST /dictamenes -> 201 con la recomendación actualizada.
    const dictamen = await request<Dictamen>(
      `/api/v1/recomendaciones/${recommendationId}/dictamenes`,
      { method: "POST", body: JSON.stringify(payload) },
    );
    return dictamen.recomendacion;
  },

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
      method: "GET",
      headers: authHeaders(),
    });
    if (!response.ok) {
      if (response.status === 401) {
        clearSession();
        window.dispatchEvent(new Event("sitra:session-expired"));
      }
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
