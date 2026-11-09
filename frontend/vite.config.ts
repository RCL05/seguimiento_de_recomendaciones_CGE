import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

const proxyTarget =
  (globalThis as { process?: { env?: Record<string, string | undefined> } }).process?.env
    ?.VITE_BACKEND_PROXY_TARGET ?? "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": proxyTarget,
      "/health": proxyTarget,
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/test/setup.ts",
    include: ["src/**/*.test.{ts,tsx}"],
  },
});
