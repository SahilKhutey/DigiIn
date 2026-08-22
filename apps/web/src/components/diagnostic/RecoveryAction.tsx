import type { Diagnostic } from "../../types";

type RecoveryActionProps = {
  diagnostic: Diagnostic;
  onRetry: () => void;
  onCopyEvidence: () => void;
  onOpenSupportSheet?: () => void;
};

export function RecoveryAction({
  diagnostic,
  onRetry,
  onCopyEvidence,
  onOpenSupportSheet,
}: RecoveryActionProps) {
  return (
    <div className="recovery">
      <p className="eyebrow">RECOVERY ACTION</p>
      <h3>{diagnostic.recovery.label}</h3>
      <p>{diagnostic.recovery.guidance}</p>
      {diagnostic.fallbackAvailable && (
        <p className="fallback">
          An authorised official fallback route is available in a production integration.
        </p>
      )}
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", margin: "14px 0" }}>
        <button
          type="button"
          onClick={onRetry}
          disabled={diagnostic.overallStatus === "resolved"}
        >
          Try targeted demo retry
        </button>
        <button className="secondary" type="button" onClick={onCopyEvidence}>
          Copy support reference
        </button>
        {onOpenSupportSheet && (
          <button
            type="button"
            className="secondary"
            onClick={onOpenSupportSheet}
            style={{ borderColor: "#0b5d9b", color: "#0b5d9b" }}
          >
            📄 Print Official Support Report
          </button>
        )}
      </div>
      <p className="reference">
        Support reference: <code>{diagnostic.supportReference}</code>
      </p>
    </div>
  );
}

