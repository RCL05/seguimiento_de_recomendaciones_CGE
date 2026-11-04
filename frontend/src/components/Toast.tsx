import { useEffect } from "react";

export type ToastMessage = {
  id: number;
  text: string;
  tone: "success" | "error";
};

type ToastProps = {
  toast: ToastMessage | null;
  onClose: () => void;
};

export function Toast({ toast, onClose }: ToastProps) {
  useEffect(() => {
    if (!toast) return;
    const timeout = window.setTimeout(onClose, 4000);
    return () => window.clearTimeout(timeout);
  }, [toast, onClose]);

  if (!toast) return null;

  return (
    <div className={`toast ${toast.tone}`} role={toast.tone === "error" ? "alert" : "status"}>
      <span>{toast.text}</span>
      <button type="button" className="toast-close" aria-label="Cerrar notificación" onClick={onClose}>
        ×
      </button>
    </div>
  );
}
