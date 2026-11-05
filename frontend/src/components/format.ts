const STATE_LABELS: Record<string, string> = {
  PENDIENTE: "Pendiente",
  EN_PROCESO: "En proceso",
  EN_VALIDACION: "En validación",
  REABIERTA: "Reabierta",
  CUMPLIDA: "Cumplida",
};

export function stateLabel(state: string) {
  return STATE_LABELS[state] ?? state;
}

export const STATE_OPTIONS = Object.entries(STATE_LABELS).map(([value, label]) => ({ value, label }));

export function formatDate(value?: string | null) {
  if (!value) return "—";
  const [year, month, day] = value.slice(0, 10).split("-");
  return `${day}/${month}/${year}`;
}

export function formatDateTime(value?: string | null) {
  if (!value) return "—";
  return new Date(value).toLocaleString("es-EC", { dateStyle: "short", timeStyle: "short" });
}
