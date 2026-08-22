import type { WalletDocument } from "../../types";

type TrustSignalModalProps = {
  document: WalletDocument | null;
  onClose: () => void;
};

export function TrustSignalModal({ document, onClose }: TrustSignalModalProps) {
  if (!document) return null;

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div className="modal-content">
        <div className="modal-header">
          <div>
            <p className="eyebrow">DEEP TRUST BREAKDOWN</p>
            <h2 id="modal-title">{document.title}</h2>
          </div>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Close dialog">
            &times;
          </button>
        </div>

        <p className="modal-desc">
          DigiIn rejects binary "verified/unverified" flags. Trust is evaluated across 5
          independent dimensions to ensure citizens and government relying parties have total clarity
          on provenance, validity, and verification routes.
        </p>

        <div className="signal-grid">
          <div className="signal-card">
            <h4>1. Source Provenance</h4>
            <span className="badge active">{document.source}</span>
            <p>
              {document.source === "GOVERNMENT_ISSUED"
                ? "Directly originated by an authorized state or central government issuer."
                : document.source === "LEGACY_RECORD"
                ? "Pre-digital historical record audited and converted from physical departmental archives."
                : "Uploaded by the citizen. DigiIn never presents an unverified upload as an official government record."}
            </p>
          </div>

          <div className="signal-card">
            <h4>2. Authenticity</h4>
            <span
              className={`badge ${
                document.authenticity === "VERIFIED" ? "active" : "unavailable"
              }`}
            >
              {document.authenticity}
            </span>
            <p>
              {document.authenticity === "VERIFIED"
                ? "Record claims have been corroborated by authoritative registries or officer audit."
                : "Authenticity is currently unknown because the file has not yet undergone official issuer review."}
            </p>
          </div>

          <div className="signal-card">
            <h4>3. Validity Status</h4>
            <span
              className={`badge ${
                document.validityStatus === "ACTIVE"
                  ? "active"
                  : document.validityStatus === "EXPIRED"
                  ? "expired"
                  : "danger"
              }`}
            >
              {document.validityStatus}
            </span>
            <p>
              {document.validityStatus === "EXPIRED"
                ? "This document was authentic when issued, but its legal validity period has lapsed."
                : document.validityStatus === "ACTIVE"
                ? "This record is currently in force and legally valid."
                : `Document is currently ${document.validityStatus.toLowerCase()}.`}
            </p>
          </div>

          <div className="signal-card">
            <h4>4. Verification Level (0 to 5)</h4>
            <span className="badge version-badge">Level {document.verificationLevel} / 5</span>
            <p>
              <strong>Route:</strong> {document.verificationMethod}
            </p>
          </div>
        </div>

        <div className="signal-card" style={{ marginTop: "16px" }}>
          <h4>5. Version Provenance (v{document.currentVersion})</h4>
          <p>
            When a record discrepancy is corrected, previous versions transition to{" "}
            <strong>SUPERSEDED</strong> rather than being overwritten. This document is currently at{" "}
            <strong>version {document.currentVersion}</strong>.
          </p>
        </div>

        <div className="modal-claims">
          <h4>Full Attribute Snapshot</h4>
          <pre>{JSON.stringify(document.extractedMetadata, null, 2)}</pre>
        </div>

        <div style={{ marginTop: "20px", textAlign: "right" }}>
          <button type="button" onClick={onClose}>
            Close Breakdown
          </button>
        </div>
      </div>
    </div>
  );
}
