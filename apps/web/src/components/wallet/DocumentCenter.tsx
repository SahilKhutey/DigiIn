import { useMemo, useState } from "react";
import type { WalletDocument } from "../../types";
import { DocumentUploadZone } from "../upload/DocumentUploadZone";
import { TrustSignalModal } from "./TrustSignalModal";
import { WalletCard } from "./WalletCard";

type DocumentCenterProps = {
  walletDocuments: WalletDocument[];
  onSelectForCorrection: (docId: string) => void;
  onRefreshWallet?: () => void;
  onSwitchToVerifier?: () => void;
  onEkycVerify?: (doc: WalletDocument) => void;
};

export function DocumentCenter({
  walletDocuments,
  onSelectForCorrection,
  onRefreshWallet,
  onSwitchToVerifier,
  onEkycVerify,
}: DocumentCenterProps) {

  const [filter, setFilter] = useState<string>("ALL");
  const [inspectedDoc, setInspectedDoc] = useState<WalletDocument | null>(null);
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  const filteredDocs = useMemo(() => {
    if (filter === "ALL") return walletDocuments;
    if (filter === "GOVERNMENT_ISSUED")
      return walletDocuments.filter((d) => d.source === "GOVERNMENT_ISSUED");
    if (filter === "VERIFIED")
      return walletDocuments.filter((d) => d.authenticity === "VERIFIED");
    if (filter === "EXPIRED")
      return walletDocuments.filter((d) => d.validityStatus === "EXPIRED");
    if (filter === "CITIZEN_UPLOAD")
      return walletDocuments.filter((d) => d.source === "CITIZEN_UPLOAD");
    return walletDocuments;
  }, [walletDocuments, filter]);

  const verifiedCount = walletDocuments.filter((d) => d.authenticity === "VERIFIED").length;
  const expiredCount = walletDocuments.filter((d) => d.validityStatus === "EXPIRED").length;
  const uploadCount = walletDocuments.filter((d) => d.source === "CITIZEN_UPLOAD").length;

  return (
    <section id="wallet" className="card wallet-section" aria-labelledby="wallet-heading">
      <div className="card-heading">
        <div>
          <p className="eyebrow">CITIZEN DOCUMENT CENTER</p>
          <h2 id="wallet-heading">My Document Wallet & Trust Signals</h2>
        </div>
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <button
            type="button"
            className="primary-action"
            onClick={() => setIsUploadOpen(true)}
            style={{ margin: 0, padding: "8px 16px", fontSize: ".88rem" }}
          >
            + Upload & Classify File
          </button>
          <span className="badge active">5-Signal Trust Engine</span>
        </div>
      </div>


      <p className="summary">
        Trust in DigiIn is multi-dimensional. We explicitly separate{" "}
        <strong>Source</strong>, <strong>Authenticity</strong>, <strong>Validity Status</strong>,{" "}
        <strong>Verification Level (0–5)</strong>, and <strong>Version</strong> so that expired
        credentials, unverified uploads, and official records are never confused.
      </p>

      {/* Wallet Posture Metrics */}
      <div className="wallet-posture-grid">
        <div className="posture-metric">
          <span className="posture-value">{walletDocuments.length}</span>
          <span className="posture-label">Total Documents</span>
        </div>
        <div className="posture-metric">
          <span className="posture-value text-success">{verifiedCount}</span>
          <span className="posture-label">Authentic & Verified</span>
        </div>
        <div className="posture-metric">
          <span className="posture-value text-warning">{expiredCount}</span>
          <span className="posture-label">Expired (Lapsed)</span>
        </div>
        <div className="posture-metric">
          <span className="posture-value text-muted">{uploadCount}</span>
          <span className="posture-label">Citizen Uploads</span>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="wallet-filter-bar" role="tablist" aria-label="Filter documents">
        <button
          type="button"
          className={`filter-btn ${filter === "ALL" ? "active" : ""}`}
          onClick={() => setFilter("ALL")}
          role="tab"
          aria-selected={filter === "ALL"}
        >
          All Records ({walletDocuments.length})
        </button>
        <button
          type="button"
          className={`filter-btn ${filter === "GOVERNMENT_ISSUED" ? "active" : ""}`}
          onClick={() => setFilter("GOVERNMENT_ISSUED")}
          role="tab"
          aria-selected={filter === "GOVERNMENT_ISSUED"}
        >
          Government Issued
        </button>
        <button
          type="button"
          className={`filter-btn ${filter === "VERIFIED" ? "active" : ""}`}
          onClick={() => setFilter("VERIFIED")}
          role="tab"
          aria-selected={filter === "VERIFIED"}
        >
          Verified Authenticity ({verifiedCount})
        </button>
        <button
          type="button"
          className={`filter-btn ${filter === "EXPIRED" ? "active" : ""}`}
          onClick={() => setFilter("EXPIRED")}
          role="tab"
          aria-selected={filter === "EXPIRED"}
        >
          Expired Validity ({expiredCount})
        </button>
        <button
          type="button"
          className={`filter-btn ${filter === "CITIZEN_UPLOAD" ? "active" : ""}`}
          onClick={() => setFilter("CITIZEN_UPLOAD")}
          role="tab"
          aria-selected={filter === "CITIZEN_UPLOAD"}
        >
          Citizen Uploads ({uploadCount})
        </button>
      </div>

      {/* Wallet Cards Grid */}
      <div className="wallet-grid">
        {filteredDocs.map((doc) => (
          <WalletCard
            key={doc.documentId}
            document={doc}
            onInspectTrust={setInspectedDoc}
            onSelectForCorrection={onSelectForCorrection}
            onEkycVerify={onEkycVerify}
          />
        ))}
      </div>


      {/* Detailed Modal */}
      <TrustSignalModal document={inspectedDoc} onClose={() => setInspectedDoc(null)} />

      {/* Document Upload & OCR Classifier Modal */}
      <DocumentUploadZone
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploadSuccess={() => {
          onRefreshWallet?.();
        }}
        onSwitchToVerifier={onSwitchToVerifier}
      />
    </section>
  );
}

