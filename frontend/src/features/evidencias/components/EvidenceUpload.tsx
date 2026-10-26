import { ChangeEvent, useState } from "react";

import { api, ApiError, Evidence } from "../../../api/client";

export const MAX_PDF_BYTES = 30 * 1024 * 1024;

type EvidenceUploadProps = {
  recommendationId: string;
  onUploaded?: (evidence: Evidence) => void;
};

export function EvidenceUpload({ recommendationId, onUploaded }: EvidenceUploadProps) {
  const [status, setStatus] = useState<"idle" | "uploading" | "done" | "error">("idle");
  const [message, setMessage] = useState("");
  const [hash, setHash] = useState("");

  async function handleChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }
    if (file.type !== "application/pdf") {
      setStatus("error");
      setMessage("Solo se permiten archivos PDF.");
      return;
    }
    if (file.size > MAX_PDF_BYTES) {
      setStatus("error");
      setMessage("El archivo supera el límite de 30 MB.");
      return;
    }

    setStatus("uploading");
    setMessage("Validando y cargando evidencia...");
    setHash("");
    try {
      const evidence = await api.uploadEvidence(recommendationId, file);
      setStatus("done");
      setMessage(`Evidencia ${evidence.filename} cargada correctamente.`);
      setHash(evidence.sha256);
      onUploaded?.(evidence);
    } catch (caught) {
      setStatus("error");
      setMessage(caught instanceof ApiError ? caught.message : "No se pudo cargar la evidencia.");
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
          disabled={status === "uploading"}
        />
      </label>
      {status !== "idle" && (
        <p className={`feedback ${status === "error" ? "error" : "success"}`}>{message}</p>
      )}
      {hash && (
        <p className="hash" title={hash}>
          SHA-256: {hash}
        </p>
      )}
    </div>
  );
}
