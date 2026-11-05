import { ReactNode } from "react";

import { Recommendation } from "../api/client";
import { formatDate, stateLabel } from "./format";

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
}) {
  return (
    <header className="page-header">
      <div>
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {actions && <div className="actions">{actions}</div>}
    </header>
  );
}

export function StateBadge({ state }: { state: string }) {
  return <span className={`badge state-${state.toLowerCase()}`}>{stateLabel(state)}</span>;
}

export function RecommendationBadges({ item }: { item: Pick<Recommendation, "state" | "vencida" | "priority"> }) {
  return (
    <span className="badge-row">
      <StateBadge state={item.state} />
      {item.vencida && <span className="badge overdue">Vencida</span>}
      {item.priority && (
        <span className={`badge priority-${item.priority.toLowerCase()}`}>
          Prioridad {item.priority.toLowerCase()}
        </span>
      )}
    </span>
  );
}

export function EmptyState({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="empty-state">
      <strong>{title}</strong>
      {children}
    </div>
  );
}

export function Notice({
  tone = "info",
  children,
}: {
  tone?: "info" | "warning" | "error" | "success";
  children: ReactNode;
}) {
  return (
    <p className={`notice ${tone}`} role={tone === "error" ? "alert" : "status"}>
      <span>{children}</span>
    </p>
  );
}

/** Lista seleccionable de recomendaciones para bandejas (UAI y ejecutor). */
export function RecommendationQueue({
  items,
  selected,
  onSelect,
  label,
}: {
  items: Recommendation[];
  selected: string;
  onSelect: (id: string) => void;
  label: string;
}) {
  return (
    <ul className="queue" aria-label={label}>
      {items.map((item) => (
        <li key={item.id}>
          <button
            type="button"
            className="queue-item"
            aria-pressed={item.id === selected}
            onClick={() => onSelect(item.id)}
          >
            <span className="queue-top">
              <strong>{item.number}</strong>
              <small className="muted">vence {formatDate(item.due_date)}</small>
            </span>
            <span className="queue-desc">{item.description}</span>
            <RecommendationBadges item={item} />
          </button>
        </li>
      ))}
    </ul>
  );
}
