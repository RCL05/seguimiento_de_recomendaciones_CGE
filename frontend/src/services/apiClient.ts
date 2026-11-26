import type { ApiEnvelope, ApiMeta, ApiResult, LoginResponse, Role, Session } from "../models";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";
const SESSION_KEY = "sitra.session";
const ROLES: readonly Role[] = ["DTI", "UAI", "EJECUTOR", "RECTORADO", "CGE_AUDITOR"];

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

function isSession(value: unknown): value is Session {
  if (typeof value !== "object" || value === null) return false;
  const session = value as Record<string, unknown>;
  return (
    typeof session.accessToken === "string" &&
    typeof session.expiresAt === "number" &&
    typeof session.role === "string" &&
    ROLES.includes(session.role as Role) &&
    typeof session.userId === "string" &&
    typeof session.email === "string" &&
    typeof session.displayName === "string" &&
    (session.unitId === undefined || typeof session.unitId === "string")
  );
}

export function getSession(): Session | null {
  const stored = sessionStorage.getItem(SESSION_KEY);
  if (!stored) return null;

  try {
    const parsed: unknown = JSON.parse(stored);
    if (!isSession(parsed) || parsed.expiresAt <= Date.now()) {
      clearSession();
      return null;
    }
    return parsed;
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

export function clearSession(): void {
  sessionStorage.removeItem(SESSION_KEY);
}

function handleUnauthorized(status: number): void {
  if (status === 401) {
    clearSession();
    window.dispatchEvent(new Event("sitra:session-expired"));
  }
}

function authHeaders(): Headers {
  const headers = new Headers();
  const session = getSession();
  if (session) headers.set("Authorization", `Bearer ${session.accessToken}`);
  return headers;
}

function isFormData(body: BodyInit | null | undefined): body is FormData {
  return typeof FormData !== "undefined" && body instanceof FormData;
}

function isBlob(body: BodyInit | null | undefined): body is Blob {
  return typeof Blob !== "undefined" && body instanceof Blob;
}

function toApiError<T>(body: ApiEnvelope<T>, status: number): ApiError {
  return new ApiError(
    body.errors?.detail ?? body.message ?? `Error HTTP ${status}`,
    body.errors?.code ?? "INTERNAL_ERROR",
    status,
  );
}

async function readEnvelope<T>(response: Response): Promise<ApiEnvelope<T>> {
  handleUnauthorized(response.status);
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) {
    throw new ApiError(`Se esperaba una respuesta JSON (HTTP ${response.status}).`, "INTERNAL_ERROR", response.status);
  }

  const body = (await response.json()) as ApiEnvelope<T>;
  if (!response.ok || !body.success) throw toApiError(body, response.status);
  if (body.data === null || !body.meta) {
    throw new ApiError("La respuesta de la API no cumple el contrato esperado.", "INTERNAL_ERROR", response.status);
  }
  return body;
}

export async function requestResult<T>(path: string, init: RequestInit = {}): Promise<ApiResult<T>> {
  const headers = new Headers(init.headers);
  for (const [key, value] of authHeaders()) headers.set(key, value);

  if (init.body && !isBlob(init.body) && !isFormData(init.body) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE}${path}`, { ...init, headers });
  const envelope = await readEnvelope<T>(response);
  return { data: envelope.data as T, message: envelope.message, meta: envelope.meta as ApiMeta };
}

export async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  return (await requestResult<T>(path, init)).data;
}

export async function requestBlob(path: string, init: RequestInit = {}): Promise<Blob> {
  const headers = new Headers(init.headers);
  for (const [key, value] of authHeaders()) headers.set(key, value);
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers });
  handleUnauthorized(response.status);
  if (!response.ok) {
    const contentType = response.headers.get("content-type") ?? "";
    if (contentType.includes("application/json")) {
      const body = (await response.json()) as ApiEnvelope<null>;
      throw toApiError(body, response.status);
    }
    throw new ApiError(`Error HTTP ${response.status}`, "INTERNAL_ERROR", response.status);
  }
  return response.blob();
}

export function serializeQuery(query: Record<string, string | number | boolean | undefined>): string {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined) params.set(key, String(value));
  }
  const serialized = params.toString();
  return serialized ? `?${serialized}` : "";
}
