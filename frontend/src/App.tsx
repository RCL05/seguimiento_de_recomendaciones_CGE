import { FormEvent, ReactNode, useCallback, useEffect, useState } from "react";

import { api, clearSession, getSession, Role, Session } from "./api/client";
import { Notice } from "./components/ui";
import { NotificationSettingsPage } from "./features/administracion/pages/NotificationSettingsPage";
import { AuditPage } from "./features/auditoria/pages/AuditPage";
import { DashboardKPIs } from "./features/dashboard/pages/DashboardKPIs";
import { ReviewEvidencePage } from "./features/evidencias/pages/ReviewEvidencePage";
import { PlanAccionPage } from "./features/planes/pages/PlanAccionPage";
import { RegistroRecomendacionPage } from "./features/recomendaciones/pages/RegistroRecomendacionPage";

type AppRoute = {
  path: string;
  label: string;
  roles: Role[];
  page: ReactNode;
};

// Los roles de cada sección coinciden con los permisos que valida el backend.
const routes: AppRoute[] = [
  { path: "/tablero", label: "Dashboard de KPIs", roles: ["DTI", "UAI", "EJECUTOR", "RECTORADO", "CGE_AUDITOR"], page: <DashboardKPIs /> },
  { path: "/recomendaciones", label: "Recomendaciones", roles: ["UAI"], page: <RegistroRecomendacionPage /> },
  { path: "/evidencias/revisar", label: "Revisión de evidencias", roles: ["UAI"], page: <ReviewEvidencePage /> },
  { path: "/planes", label: "Mi bandeja", roles: ["EJECUTOR"], page: <PlanAccionPage /> },
  { path: "/auditoria", label: "Auditoría y matriz", roles: ["UAI", "CGE_AUDITOR"], page: <AuditPage /> },
  {
    path: "/administracion/notificaciones",
    label: "Notificaciones",
    roles: ["DTI"],
    page: <NotificationSettingsPage />,
  },
];

const ROLE_LABELS: Record<Role, string> = {
  UAI: "Auditoría Interna (UAI)",
  EJECUTOR: "Ejecutor de unidad",
  RECTORADO: "Rectorado",
  CGE_AUDITOR: "Auditor CGE",
  DTI: "Administración DTI",
};

const DEV_TOKENS: { token: string; label: string }[] = [
  { token: "uai-sso-token", label: "UAI" },
  { token: "ejecutor-sso-token", label: "Ejecutor" },
  { token: "rectorado-sso-token", label: "Rectorado" },
  { token: "dti-sso-token", label: "DTI" },
];

function landingPath(role: Role) {
  return routes.find((route) => route.roles.includes(role))?.path ?? "/";
}

function LoginPage({ onLogin }: { onLogin: (session: Session) => void }) {
  const [credential, setCredential] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function login(value: string) {
    setError("");
    setSubmitting(true);
    try {
      onLogin(await api.login(value));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "No se pudo iniciar sesión.");
    } finally {
      setSubmitting(false);
    }
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void login(credential);
  }

  return (
    <div className="login-page">
      <section className="login-brand" aria-label="SITRA-CGE UNL">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">
            S
          </span>
          <span className="brand-text">
            <strong>SITRA-CGE</strong>
            <small>Universidad Nacional de Loja</small>
          </span>
        </div>
        <h1>Seguimiento de recomendaciones de la Contraloría</h1>
        <p>
          Registre las recomendaciones de la CGE, asigne responsables, respalde el cumplimiento con
          evidencias y mantenga la trazabilidad de cada decisión.
        </p>
        <ul>
          <li>Plan de acción y evidencias PDF con huella SHA-256</li>
          <li>Dictamen de la Unidad de Auditoría Interna</li>
          <li>Alertas de vencimiento y tablero institucional</li>
        </ul>
      </section>

      <main className="login-panel">
        <form className="card login-card" onSubmit={submit}>
          <div>
            <p className="eyebrow">Acceso institucional</p>
            <h2>Iniciar sesión</h2>
            <p className="muted">Ingrese la credencial emitida por el SSO de la UNL.</p>
          </div>
          <label htmlFor="sso-credential">
            Credencial de acceso SSO
            <input
              id="sso-credential"
              type="password"
              autoComplete="current-password"
              required
              value={credential}
              onChange={(event) => setCredential(event.target.value)}
            />
          </label>
          {error && <Notice tone="error">{error}</Notice>}
          <button type="submit" disabled={submitting}>
            {submitting ? "Validando…" : "Ingresar"}
          </button>

          {import.meta.env.DEV && (
            <div className="dev-tokens">
              <p>Entorno de desarrollo: ingrese con un rol de prueba.</p>
              <div className="actions">
                {DEV_TOKENS.map((item) => (
                  <button
                    key={item.token}
                    type="button"
                    className="secondary"
                    disabled={submitting}
                    onClick={() => {
                      setCredential(item.token);
                      void login(item.token);
                    }}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>
          )}
        </form>
      </main>
    </div>
  );
}

export function App() {
  const [pathname, setPathname] = useState(window.location.pathname);
  const [session, setActiveSession] = useState<Session | null>(() => getSession());

  const navigate = useCallback((path: string, replace = false) => {
    if (replace) window.history.replaceState(null, "", path);
    else window.history.pushState(null, "", path);
    setPathname(path);
  }, []);

  useEffect(() => {
    const onPopState = () => setPathname(window.location.pathname);
    const onSessionExpired = () => {
      setActiveSession(null);
      navigate("/login", true);
    };
    window.addEventListener("popstate", onPopState);
    window.addEventListener("sitra:session-expired", onSessionExpired);
    return () => {
      window.removeEventListener("popstate", onPopState);
      window.removeEventListener("sitra:session-expired", onSessionExpired);
    };
  }, [navigate]);

  useEffect(() => {
    if (!session && pathname !== "/login") navigate("/login", true);
    else if (session && (pathname === "/login" || pathname === "/")) navigate(landingPath(session.role), true);
  }, [navigate, pathname, session]);

  useEffect(() => {
    if (!session) return;
    const timeout = window.setTimeout(() => {
      clearSession();
      setActiveSession(null);
      navigate("/login", true);
    }, Math.max(0, session.expiresAt - Date.now()));
    return () => window.clearTimeout(timeout);
  }, [navigate, session]);

  useEffect(() => {
    const route = routes.find((item) => item.path === pathname);
    document.title = route ? `${route.label} · SITRA-CGE UNL` : "SITRA-CGE UNL";
  }, [pathname]);

  function handleLogin(nextSession: Session) {
    setActiveSession(nextSession);
    navigate(landingPath(nextSession.role), true);
  }

  function logout() {
    clearSession();
    setActiveSession(null);
    navigate("/login", true);
  }

  if (!session) {
    return <LoginPage onLogin={handleLogin} />;
  }

  const visibleRoutes = routes.filter((route) => route.roles.includes(session.role));
  const activeRoute = routes.find((route) => route.path === pathname);
  const canAccessRoute = activeRoute?.roles.includes(session.role) ?? false;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">
            S
          </span>
          <span className="brand-text">
            <strong>SITRA-CGE</strong>
            <small>Seguimiento de recomendaciones</small>
          </span>
        </div>
        <nav className="nav" aria-label="Secciones">
          {visibleRoutes.map((route) => (
            <a
              key={route.path}
              className="nav-link"
              href={route.path}
              aria-current={route.path === pathname ? "page" : undefined}
              onClick={(event) => {
                event.preventDefault();
                navigate(route.path);
              }}
            >
              {route.label}
            </a>
          ))}
        </nav>
        <div className="external-links" aria-label="Documentación y arquitectura">
          <a className="nav-link external-link" href="http://localhost:8000/api/docs/" target="_blank" rel="noreferrer">
            Documentación API (Swagger)
          </a>
          <a className="nav-link external-link" href="http://localhost:8001/" target="_blank" rel="noreferrer">
            Arquitectura C4
          </a>
        </div>
        <div className="user-card">
          <div>
            <strong>{session.displayName}</strong>
            <br />
            <small>
              {ROLE_LABELS[session.role]}
              {session.unitId ? ` · ${session.unitId}` : ""}
            </small>
          </div>
          <button type="button" className="button" onClick={logout}>
            Cerrar sesión
          </button>
        </div>
      </aside>

      <main className="content">
        {canAccessRoute ? (
          activeRoute?.page
        ) : (
          <Notice tone="error">No tiene permisos para acceder a esta sección.</Notice>
        )}
      </main>
    </div>
  );
}
