export type Pagination = {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
};

export type ApiMeta = {
  request_id: string;
  timestamp: string;
  version: string;
  pagination: Pagination | null;
};

export type ApiErrorCode =
  | "VALIDATION_ERROR"
  | "AUTHENTICATION_REQUIRED"
  | "PERMISSION_DENIED"
  | "RESOURCE_NOT_FOUND"
  | "METHOD_NOT_ALLOWED"
  | "BUSINESS_RULE_VIOLATION"
  | "CONFLICT"
  | "PAYLOAD_TOO_LARGE"
  | "UNSUPPORTED_MEDIA_TYPE"
  | "INTERNAL_ERROR";

export type ApiErrorDetails = {
  code: ApiErrorCode;
  detail: string;
  fields?: Record<string, unknown>;
};

export type ApiEnvelope<T> = {
  success: boolean;
  message: string;
  data: T | null;
  errors: ApiErrorDetails | null;
  meta: ApiMeta;
};

export type ApiResult<T> = {
  data: T;
  message: string;
  meta: ApiMeta;
};
