import type { WalletDocument } from "../../types";

type WalletCardProps = {
  document: WalletDocument;
  onInspectTrust: (doc: WalletDocument) => void;
  onSelectForCorrection: (docId: string) => void;
};

export function WalletCard({
  document,
  onInspectTrust,
  onSelectForCorrection,
}: WalletCardProps) {
  const sourceLabel =
    document.source === "GOVERNMENT_ISSUED"
      ? "Government Issued"
      : document.source === "LEGACY_RECORD"
      ? "Legacy Record"
      : "Citizen Upload";

  const sourceBadgeClass =
    document.source === "GOVERNMENT_ISSUED"
      ? "active"
      : document.source === "LEGACY_RECORD"
      ? "pending"
      : "warning";

  const authBadgeClass =
    document.authenticity === "VERIFIED"
      ? "active"
      : document.authenticity === "UNKNOWN"
      ? "unavailable"
      : "danger";

  const validityBadgeClass =
    document.validityStatus === "ACTIVE"
      ? "active"
      : document.validityStatus === "EXPIRED"
      ? "expired"
      : document.validityStatus === "REVOKED"
      ? "danger"
      : "superseded";

  const levelLabels: Record<number, string> = {
    0: "Level 0: Uploaded (Unverified)",
    1: "Level 1: OCR & Classified",
    2: "Level 2: Identity Matched",
    3: "Level 3: Issuer Matched",
    4: "Level 4: Government Verified",
    5: "Level 5: Cryptographically Signed",
  };

  const levelPercent = (document.verificationLevel / 5) * 100;

  return (
    <article className="wallet-card" aria-label={`Wallet document ${document.title}`}>
      <div className="wallet-card-header">
        <div>
          <span className="wallet-doc-type">{document.documentType}</span>
          <h3 className="wallet-card-title">{document.title}</h3>
          <p className="wallet-issuer">{document.issuer}</p>
        </div>
        <span className="wallet-version-pill">v{document.currentVersion}</span>
      </div>

      {/* 5-Signal Trust Badge Cluster */}
      <div className="trust-cluster" aria-label="Discrete trust signals">
        <div className="trust-cluster-item">
          <span className="trust-cluster-label">1. Source</span>
          <span className={`badge ${sourceBadgeClass}`}>{sourceLabel}</span>
        </div>
        <div className="trust-cluster-item">
          <span className="trust-cluster-label">2. Authenticity</span>
          <span className={`badge ${authBadgeClass}`}>{document.authenticity}</span>
        </div>
        <div className="trust-cluster-item">
          <span className="trust-cluster-label">3. Validity</span>
          <span className={`badge ${validityBadgeClass}`}>{document.validityStatus}</span>
        </div>
        <div className="trust-cluster-item">
          <span className="trust-cluster-label">4. Version</span>
          <span className="badge version-badge">Version {document.currentVersion}</span>
        </div>
      </div>

      {/* 5th Signal: Verification Level Meter */}
      <div className="level-container">
        <div className="level-header">
          <span className="trust-cluster-label">5. Verification Level</span>
          <strong className="level-text">
            {levelLabels[document.verificationLevel] ?? `Level ${document.verificationLevel}`}
          </strong>
        </div>
        <div className="level-track" aria-hidden="true">
          <div
            className="level-fill"
            style={{
              width: `${Math.max(levelPercent, 8)}%`,
              backgroundColor:
                document.verificationLevel >= 4
                  ? "#16a34a"
                  : document.verificationLevel >= 2
                  ? "#2563eb"
                  : "#94a3b8",
            }}
          />
        </div>
        <p className="level-subtext">{document.verificationMethod}</p>
      </div>

      {/* Metadata Preview */}
      <div className="wallet-metadata-preview">
        <strong>Extracted Claims: </strong>
        <code>
          {Object.entries(document.extractedMetadata)
            .slice(0, 3)
            .map(([k, v]) => `${k}: ${String(v)}`)
            .join(" • ") || "No claims extracted"}
        </code>
      </div>

      {/* Card Footer Actions */}
      <div className="wallet-card-actions">
        <button
          type="button"
          className="secondary-action"
          onClick={() => onInspectTrust(document)}
        >
          Inspect Trust Signals
        </button>
        <button
          type="button"
          className="primary-action"
          onClick={() => onSelectForCorrection(document.documentId)}
        >
          Fix Error (v{document.currentVersion})
        </button>
      </div>
    </article>
  );
}
