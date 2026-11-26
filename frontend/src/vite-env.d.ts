/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Origen de la API, sin /api/v1. Vacío para usar el mismo origen y el proxy. */
  readonly VITE_API_BASE?: string;
  /** Destino del proxy de desarrollo; Compose utiliza http://backend:8000. */
  readonly VITE_BACKEND_PROXY_TARGET?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
