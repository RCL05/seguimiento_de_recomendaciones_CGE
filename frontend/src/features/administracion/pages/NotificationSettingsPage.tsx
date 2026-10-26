import { FormEvent, useEffect, useState } from "react";

import { api, ApiError, NotificationPreference, NotificationSettings } from "../../../api/client";

export function NotificationSettingsPage() {
  const [settings, setSettings] = useState<NotificationSettings | null>(null);
  const [preferences, setPreferences] = useState<NotificationPreference[]>([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.getNotificationSettings(), api.getPreferences()])
      .then(([loadedSettings, loadedPreferences]) => {
        setSettings(loadedSettings);
        setPreferences(loadedPreferences.preferencias);
      })
      .catch((caught) =>
        setError(
          caught instanceof ApiError ? caught.message : "No se pudo cargar la configuración.",
        ),
      );
  }, []);

  async function saveSettings(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");
    const form = new FormData(event.currentTarget);
    const roles = String(form.get("destinatarios_mora") ?? "")
      .split(",")
      .map((role) => role.trim())
      .filter(Boolean);
    try {
      const updated = await api.updateNotificationSettings({
        umbral_dias: Number(form.get("umbral_dias")),
        notificaciones_activas: form.get("notificaciones_activas") === "on",
        canal_interno_activo: form.get("canal_interno_activo") === "on",
        canal_email_activo: form.get("canal_email_activo") === "on",
        destinatarios_mora: roles,
      });
      setSettings(updated);
      setMessage("Configuración institucional actualizada y auditada.");
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "No se pudo guardar.");
    }
  }

  async function togglePreference(
    preference: NotificationPreference,
    field: "notificar_email" | "notificar_interno",
  ) {
    setError("");
    try {
      const updated = await api.updatePreferences([{ ...preference, [field]: !preference[field] }]);
      setPreferences((current) => {
        const next = [...current];
        updated.preferencias.forEach((item) => {
          const index = next.findIndex((candidate) => candidate.tipo_alerta === item.tipo_alerta);
          if (index >= 0) {
            next[index] = item;
          }
        });
        return next;
      });
      setMessage("Preferencia personal actualizada.");
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "No se pudo guardar la preferencia.");
    }
  }

  return (
    <section className="card" aria-labelledby="settings-title">
      <h2 id="settings-title">Configuración de notificaciones</h2>

      {settings && (
        <form className="form-grid" onSubmit={saveSettings}>
          <label>
            Umbral de alerta (días)
            <input
              name="umbral_dias"
              type="number"
              min={1}
              max={90}
              defaultValue={settings.umbral_dias}
              required
            />
          </label>
          <label>
            Destinatarios de mora (roles separados por coma)
            <input
              name="destinatarios_mora"
              defaultValue={settings.destinatarios_mora.join(", ")}
            />
          </label>
          <label className="checkbox">
            <input
              name="notificaciones_activas"
              type="checkbox"
              defaultChecked={settings.notificaciones_activas}
            />
            Notificaciones activas
          </label>
          <label className="checkbox">
            <input
              name="canal_interno_activo"
              type="checkbox"
              defaultChecked={settings.canal_interno_activo}
            />
            Canal interno
          </label>
          <label className="checkbox">
            <input
              name="canal_email_activo"
              type="checkbox"
              defaultChecked={settings.canal_email_activo}
            />
            Canal correo institucional
          </label>
          <button type="submit">Guardar configuración</button>
        </form>
      )}

      <h3>Preferencias personales</h3>
      {preferences.length === 0 ? (
        <p>Sin preferencias registradas.</p>
      ) : (
        <ul className="preference-list">
          {preferences.map((preference) => (
            <li key={preference.tipo_alerta}>
              <strong>{preference.tipo_alerta}</strong>
              <label className="checkbox">
                <input
                  type="checkbox"
                  checked={preference.notificar_interno}
                  onChange={() => togglePreference(preference, "notificar_interno")}
                />
                Bandeja interna
              </label>
              <label className="checkbox">
                <input
                  type="checkbox"
                  checked={preference.notificar_email}
                  onChange={() => togglePreference(preference, "notificar_email")}
                />
                Correo
              </label>
            </li>
          ))}
        </ul>
      )}

      {message && <p className="feedback success">{message}</p>}
      {error && <p className="feedback error">{error}</p>}
    </section>
  );
}
