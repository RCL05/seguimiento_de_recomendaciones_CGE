import { FormEvent, ReactNode, useCallback, useEffect, useState } from "react";

import { api, clearSession, getSession, Role, Session } from "./api/client";
import { NotificationSettingsPage } from "./features/administracion/pages/NotificationSettingsPage";
import { AuditPage } from "./features/auditoria/pages/AuditPage";
import { ExecutiveDashboardPage } from "./features/dashboard/pages/ExecutiveDashboardPage";
import { ReviewEvidencePage } from "./features/evidencias/pages/ReviewEvidencePage";
import { PlanAccionPage } from "./features/planes/pages/PlanAccionPage";
import { RegistroRecomendacionPage } from "./features/recomendaciones/pages/RegistroRecomendacionPage";

type AppRoute = {
  path: string;
  label: string;
  roles: Role[];
  page: ReactNode;
};

const routes: AppRoute[] = [
  {
    path: "/recomendaciones",
    label: "Recomendaciones",
    roles: ["UAI"],
    page: <RegistroRecomendacionPage />,
  },
  {
    path: "/evidencias/revisar",
    label: "Revisión de evidencias",
    roles: ["UAI"],
    page: <ReviewEvidencePage />,
  },
  { path: "/planes", label: "Planes de acción", roles: ["EJECUTOR"], page: <PlanAccionPage /> },
  {
    path: "/tablero",
    label: "Tablero ejecutivo",
    roles: ["RECTORADO"],
    page: <ExecutiveDashboardPage />,
  },
  { path: "/auditoria", label: "Auditoría", roles: ["CGE_AUDITOR"], page: <AuditPage /> },
  {
    path: "/administracion/notificaciones",
    label: "Notificaciones",
    roles: ["DTI"],
    page: <NotificationSettingsPage />,
  },
];

function landingPath(role: Role) {
  return routes.find((route) => route.roles.includes(role))?.path ?? "/";
}

function LoginPage({ onLogin }: { onLogin: (session: Session) => void }) {
  const [credential, setCredential] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      onLogin(await api.login(credential));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "No se pudo iniciar sesión.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main>
      <header>
        <p className="eyebrow">SITRA-CGE UNL</p>
        <h1>Iniciar sesión</h1>
        <p>Acceda con su credencial institucional.</p>
      </header>
      <form onSubmit={submit}>
        <label htmlFor="sso-credential">Credencial de acceso SSO</label>
        <input
          id="sso-credential"
          type="password"
          autoComplete="current-password"
          required
          value={credential}
          onChange={(event) => setCredential(event.target.value)}
        />
        {error && <p role="alert">{error}</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? "Validando…" : "Ingresar"}
        </button>
      </form>
    </main>
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
    else if (session && pathname === "/login") navigate(landingPath(session.role), true);
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

  const activeRoute = routes.find((route) => route.path === pathname);
  const canAccessRoute = activeRoute?.roles.includes(session.role) ?? pathname === "/";

  return (
    <main>
      <header>
        <p className="eyebrow">SITRA-CGE UNL</p>
        <h1>Seguimiento de recomendaciones</h1>
        <p>
          Registre, ejecute, revise y supervise las recomendaciones emitidas por la Contraloría
          General del Estado.
        </p>
        <p>
          Sesión: {session.displayName} · {session.role}
        </p>
        <nav aria-label="Secciones">
          {routes
            .filter((route) => route.roles.includes(session.role))
            .map((route) => (
              <a
                key={route.path}
                href={route.path}
                onClick={(event) => {
                  event.preventDefault();
                  navigate(route.path);
                }}
              >
                {route.label}
              </a>
            ))}
          <button type="button" onClick={logout}>
            Cerrar sesión
          </button>
        </nav>
      </header>
      {canAccessRoute ? (
        (activeRoute?.page ?? <p>Seleccione una sección.</p>)
      ) : (
        <p role="alert">No tiene permisos para acceder a esta sección.</p>
      )}
    </main>
  );
}
