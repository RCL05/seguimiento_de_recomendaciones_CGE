import { ChangeEvent, useState } from "react";

import { api, ApiError, Evidence } from "../../../api/client";
import { Toast } from "../../../components/Toast";
import { useToast } from "../../../hooks/useToast";

export const MAX_PDF_BYTES = 30 * 1024 * 1024;

type EvidenceUploadProps = {
  recommendationId: string;
  onUploaded?: (evidence: Evidence) => void;
  disabled?: boolean;
  disabledMessage?: string;
};

export function EvidenceUpload({
  recommendationId,
  onUploaded,
  disabled = false,
  disabledMessage,
}: EvidenceUploadProps) {
  const [status, setStatus] = useState<"idle" | "uploading" | "done" | "error">("idle");
  const [hash, setHash] = useState("");
  const { toast, showToast, dismissToast } = useToast();

  async function handleChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }
    if (file.type !== "application/pdf") {
      setStatus("error");
      showToast("Solo se permiten archivos PDF.", "error");
      return;
    }
    if (file.size > MAX_PDF_BYTES) {
      setStatus("error");
      showToast("El archivo supera el límite de 30 MB.", "error");
      return;
    }

    setStatus("uploading");
    setHash("");
    try {
      const evidence = await api.uploadEvidence(recommendationId, file);
      setStatus("done");
      setHash(evidence.sha256);
      showToast(`Evidencia ${evidence.filename} cargada correctamente.`);
      window.dispatchEvent(new Event("sitra:dashboard-refresh"));
      onUploaded?.(evidence);
    } catch (caught) {
      setStatus("error");
      showToast(messageFromError(caught), "error");
    }
  }

  return (
    <div className="evidence-upload">
      <label>
        Cargar evidencia PDF (máximo 30 MB)
        <input
          type="file"
          accept="application/pdf,.pdf"
          onChange={handleChange}
          disabled={disabled || status === "uploading"}
        />
      </label>
      <p className="hint">Al cargarla, la recomendación pasa a validación de la UAI y se calcula su huella SHA-256.</p>
      {disabledMessage && <p className="notice warning" role="status">{disabledMessage}</p>}
      {status === "uploading" && (
        <p className="notice info" role="status">Validando y cargando evidencia...</p>
      )}
      {hash && (
        <p className="hash" title={hash}>
          SHA-256: {hash}
        </p>
      )}
      <Toast toast={toast} onClose={dismissToast} />
    </div>
  );
}

function messageFromError(error: unknown) {
  return error instanceof ApiError ? error.message : "No se pudo cargar la evidencia.";
}
