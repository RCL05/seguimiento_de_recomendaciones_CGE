import { FormEvent, useEffect, useState } from "react";

import { api, ApiError, NotificationPreference, NotificationSettings } from "../../../api/client";
import { Toast } from "../../../components/Toast";
import { formatDateTime } from "../../../components/format";
import { PageHeader } from "../../../components/ui";
import { useToast } from "../../../hooks/useToast";

const ALERT_LABELS: Record<NotificationPreference["tipo_alerta"], { title: string; text: string }> = {
  ALERTA_VENCIMIENTO: {
    title: "Alerta de vencimiento próximo",
    text: "Se envía cuando una recomendación está por vencer y aún no tiene evidencia presentada.",
  },
  EN_MORA: {
    title: "Recomendación vencida",
    text: "Se envía una vez cuando el plazo legal expira sin cumplimiento.",
  },
};

export function NotificationSettingsPage() {
  const [settings, setSettings] = useState<NotificationSettings | null>(null);
  const [preferences, setPreferences] = useState<NotificationPreference[]>([]);
  const [saving, setSaving] = useState(false);
  const { toast, showToast, dismissToast } = useToast();

  useEffect(() => {
    Promise.all([api.getNotificationSettings(), api.getPreferences()])
      .then(([loadedSettings, loadedPreferences]) => {
        setSettings(loadedSettings);
        setPreferences(loadedPreferences.preferencias);
      })
      .catch((caught) =>
        showToast(caught instanceof ApiError ? caught.message : "No se pudo cargar la configuración.", "error"),
      );
  }, [showToast]);

  async function saveSettings(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const roles = String(form.get("destinatarios_mora") ?? "")
      .split(",")
      .map((role) => role.trim())
      .filter(Boolean);
    setSaving(true);
    try {
      const updated = await api.updateNotificationSettings({
        umbral_dias: Number(form.get("umbral_dias")),
        notificaciones_activas: form.get("notificaciones_activas") === "on",
        canal_interno_activo: form.get("canal_interno_activo") === "on",
        canal_email_activo: form.get("canal_email_activo") === "on",
        destinatarios_mora: roles,
      });
      setSettings(updated);
      showToast("Configuración institucional actualizada y auditada.");
    } catch (caught) {
      showToast(caught instanceof ApiError ? caught.message : "No se pudo guardar.", "error");
    } finally {
      setSaving(false);
    }
  }

  async function togglePreference(preference: NotificationPreference, field: "notificar_email" | "notificar_interno") {
    try {
      const updated = await api.updatePreferences([{ ...preference, [field]: !preference[field] }]);
      setPreferences((current) => {
        const next = [...current];
        updated.preferencias.forEach((item) => {
          const index = next.findIndex((candidate) => candidate.tipo_alerta === item.tipo_alerta);
          if (index >= 0) next[index] = item;
        });
        return next;
      });
      showToast("Preferencia personal actualizada.");
    } catch (caught) {
      showToast(caught instanceof ApiError ? caught.message : "No se pudo guardar la preferencia.", "error");
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="Administración DTI"
        title="Configuración de notificaciones"
        description="Defina cuándo y por qué canales se alerta sobre vencimientos. Cada cambio queda registrado en la auditoría."
      />

      <section className="card" aria-labelledby="settings-title">
        <div className="card-header">
          <div>
            <h2 id="settings-title">Configuración institucional</h2>
            {settings && <p>Última actualización: {formatDateTime(settings.actualizado_en)}</p>}
          </div>
        </div>
        {settings ? (
          <form className="form-grid" onSubmit={saveSettings}>
            <label>
              Umbral de alerta (días)
              <input name="umbral_dias" type="number" min={1} max={90} defaultValue={settings.umbral_dias} required />
            </label>
            <label>
              Destinatarios de mora (roles separados por coma)
              <input name="destinatarios_mora" defaultValue={settings.destinatarios_mora.join(", ")} placeholder="UAI, RECTORADO" />
            </label>
            <fieldset className="form-section">
              <legend>Canales</legend>
              <label className="checkbox">
                <input name="notificaciones_activas" type="checkbox" defaultChecked={settings.notificaciones_activas} />
                Notificaciones activas
              </label>
              <label className="checkbox">
                <input name="canal_interno_activo" type="checkbox" defaultChecked={settings.canal_interno_activo} />
                Bandeja interna del sistema
              </label>
              <label className="checkbox">
                <input name="canal_email_activo" type="checkbox" defaultChecked={settings.canal_email_activo} />
                Correo institucional
              </label>
            </fieldset>
            <div className="form-footer">
              <button type="submit" disabled={saving}>
                {saving ? "Guardando..." : "Guardar configuración"}
              </button>
            </div>
          </form>
        ) : (
          <p role="status" className="muted">
            Cargando configuración...
          </p>
        )}
      </section>

      <section className="card" aria-labelledby="prefs-title">
        <div className="card-header">
          <div>
            <h2 id="prefs-title">Mis preferencias</h2>
            <p>Elija por dónde recibe cada tipo de alerta.</p>
          </div>
        </div>
        {preferences.length === 0 ? (
          <p className="muted">Sin preferencias registradas.</p>
        ) : (
          <ul className="evidence-list">
            {preferences.map((preference) => (
              <li key={preference.tipo_alerta}>
                <div>
                  <strong>{ALERT_LABELS[preference.tipo_alerta]?.title ?? preference.tipo_alerta}</strong>
                  <small className="muted">{ALERT_LABELS[preference.tipo_alerta]?.text}</small>
                </div>
                <div className="actions">
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
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
      <Toast toast={toast} onClose={dismissToast} />
    </>
  );
}
