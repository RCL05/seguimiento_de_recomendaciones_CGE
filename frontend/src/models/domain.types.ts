import type { Pagination } from "./api.types";

export type Role = "DTI" | "UAI" | "EJECUTOR" | "RECTORADO" | "CGE_AUDITOR";
export type RecommendationState = "PENDIENTE" | "EN_PROCESO" | "EN_VALIDACION" | "REABIERTA" | "CUMPLIDA";
export type Priority = "ALTA" | "MEDIA" | "BAJA";
export type EvidenceType = "BORRADOR" | "FINAL";
export type EvidenceStatus = "VIGENTE" | "ANULADA";
export type DictamenResult = "APROBADO" | "RECHAZADO";
export type AlertType = "ALERTA_VENCIMIENTO" | "EN_MORA";
export type RiskLight = "VERDE" | "AMARILLO" | "ROJO";

export type Session = {
  accessToken: string;
  expiresAt: number;
  role: Role;
  userId: string;
  email: string;
  displayName: string;
  unitId?: string;
};

export type LoginRequest = {
  credential: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: "Bearer";
  expires_in: number;
  user_id: string;
  email: string;
  display_name: string;
  role: Role;
  unit_id: string | null;
};

export type Recommendation = {
  id: string;
  report_id: string;
  number: string;
  description: string;
  unit_id: string;
  legal_days: number;
  due_date: string;
  priority: Priority;
  state: RecommendationState;
  /** Plazo legal vencido sin cumplir: indicador, no un estado del flujo. */
  vencida: boolean;
  overdue_registered_at: string | null;
};

export type RecommendationDetail = Recommendation & { evidencias: Evidence[] };

export type RecommendationCreateRequest = {
  report_id: string;
  number: string;
  description: string;
  unit_id: string;
  legal_days: number;
  due_date: string;
  priority?: Priority;
};

export type RecommendationQuery = {
  due_after?: string;
  due_before?: string;
  due_date?: string;
  page?: number;
  page_size?: number;
  priority?: Priority;
  state?: RecommendationState;
  unit_id?: string;
  vencida?: boolean;
};

export type RecommendationUpdateRequest =
  | { estado: "REABIERTA"; motivo: string }
  | { unit_id: string; motivo: string };

export type Milestone = {
  id: string;
  recommendation_id: string;
  descripcion_hito: string;
  fecha_compromiso: string;
  completado: boolean;
  created_by: string;
};

export type MilestoneCreateRequest = {
  descripcion_hito: string;
  fecha_compromiso: string;
};

export type Evidence = {
  id: string;
  recommendation_id: string;
  filename: string;
  mime_type: string;
  size_bytes: number;
  sha256: string;
  uploaded_at: string;
  uploaded_by: string;
  validated: boolean;
  type: EvidenceType;
  status: EvidenceStatus;
};

export type EvidenceCancellationRequest = {
  estado: "ANULADA";
  motivo: string;
};

export type EvidenceIntegrity = {
  evidence_id: string;
  integra: boolean;
  hash_registrado: string;
  hash_calculado: string;
};

export type Dictamen = {
  id: string;
  resultado: DictamenResult;
  evidence_id: string;
  evaluator_id: string;
  observaciones: string;
  fecha_dictamen: string;
  recomendacion: Recommendation;
};

export type DictamenCreateRequest = {
  evidence_id: string;
  approved: boolean;
  observaciones?: string;
};

export type Unit = {
  id: string;
  codigo: string;
  nombre: string;
};

export type UnitCreateRequest = {
  codigo: string;
  nombre: string;
};

export type AdminUser = {
  id: string;
  correo_institucional: string;
  nombres: string;
  rol: Role;
  unidad_codigo: string | null;
  activo: boolean;
};

export type UserUpdateRequest = {
  rol?: Role;
  unidad_codigo?: string;
};

export type Report = {
  id: string;
  numero_informe: string;
  periodo_auditado: string;
  fecha_notificacion: string;
  pdf_informe_url: string;
  creado_en: string;
};

export type ReportCreateRequest = {
  numero_informe: string;
  periodo_auditado: string;
  fecha_notificacion: string;
  pdf_informe_url?: string;
  pdf_informe?: File;
};

export type ReportCreateJsonRequest = Omit<ReportCreateRequest, "pdf_informe">;

export type PageQuery = {
  page?: number;
  page_size?: number;
};

export type PaginatedResult<T> = {
  items: T[];
  pagination: Pagination | null;
};

export type Dashboard = {
  total: number;
  cumplimiento_porcentaje: number;
  semaforo_riesgo: RiskLight;
  en_mora: number;
  en_revision_interna: number;
  por_estado: Record<string, number>;
  unidades_en_mora: { unidad_codigo: string; unidad_nombre: string; vencidas: number; total: number }[];
  fecha_corte: string;
};

export type DashboardKPIs = {
  total_recomendaciones: number;
  recomendaciones_por_estado: Record<string, number>;
  tasa_cumplimiento_porcentaje: number;
  recomendaciones_vencidas_o_en_mora: number;
  total_informes_cge: number;
};

export type AuditLogEntry = {
  id: number;
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
  ip_origen: string | null;
};

export type AuditQuery = {
  entity?: string;
  entity_id?: string;
  limit?: number;
};

export type Notification = {
  id: string;
  type: string;
  status: string;
  scheduled_at: string;
  attempts: number;
  recommendation_id: string | null;
};

export type NotificationPreference = {
  id: string | null;
  usuario_id: string;
  tipo_alerta: AlertType;
  notificar_interno: boolean;
  notificar_email: boolean;
  activo: boolean;
  actualizado_en: string | null;
};

export type Preferences = {
  usuario_id: string;
  preferencias: NotificationPreference[];
};

export type PreferencesUpdateRequest = {
  usuario_id?: string;
  preferencias: Array<Pick<NotificationPreference, "tipo_alerta" | "notificar_interno" | "notificar_email" | "activo">>;
};

export type NotificationSettings = {
  umbral_dias: number;
  notificaciones_activas: boolean;
  canal_interno_activo: boolean;
  canal_email_activo: boolean;
  destinatarios_vencimiento: string[];
  destinatarios_mora: string[];
  actualizado_en: string;
};

export type NotificationSettingsUpdateRequest = Partial<
  Omit<NotificationSettings, "actualizado_en">
>;

export type Health = {
  status: "ok";
};
