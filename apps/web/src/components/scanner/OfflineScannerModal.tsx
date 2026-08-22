import React, { useState, useEffect } from "react";
import { verifyProofTokenOffline, type OfflineVerificationResult } from "../../utils/offlineVerifier";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  initialToken?: string;
}

const PRESET_SCAN_SAMPLES = [
  {
    label: "🛡️ Valid NTA Exam Predicate Proof (Ed25519)",
    token:
      "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCIsImtpZCI6ImRpZ2lpbi1lZDI1NTE5LWtleS0yMDI2In0.eyJpc3MiOiJEaWdpSW4gU292ZXJlaWduIElzc3VlciIsInN1YiI6InN1YmpfZGVtb181YzdiOTAiLCJhdWQiOiJOVEFfQVBQTElDQVRJT05fUE9SVEFMIiwicHVycG9zZSI6Ik5hdGlvbmFsIEVsaWdpYmlsaXR5IFRlc3QgKE5FRVQvSkVFKSBBcHBsaWNhdGlvbiAyMDI2IiwiZGlzY2xvc3VyZV9tb2RlIjoiUFJFRElDQVRFX09OTFkiLCJpYXQiOiIyMDI2LTA4LTIyVDEyOjAwOjAwWiIsImV4cCI6IjIwMjYtMDgtMjJUMTg6MDA6MDBaIiwicHJlZGljYXRlX3Byb29mcyI6W3siY2xhaW1OYW1lIjoiQ0xBU1NfWElJIiwiZXhwcmVzc2lvbiI6IjEydGggQm9hcmQgUmVzdWx0ID09IFBBU1NFRCIsInNhdGlzZmllZCI6dHJ1ZSwicHJvb2ZUeXBlIjoiREVSSVZFRF9aRVJPX0tOT1dMRURHRV9QUkVESUNBVEUifSx7ImNsYWltTmFtZSI6IkFHRV9PVkVSXzE4IiwiZXhwcmVzc2lvbiI6IkFnZSA-PSAxOCBZZWFycyIsInNhdGlzZmllZCI6dHJ1ZSwicHJvb2ZUeXBlIjoiREVSSVZFRF9aRVJPX0tOT1dMRURHRV9QUkVESUNBVEUifV0sIm1hc2tlZF9hdHRyaWJ1dGVzIjpbInJvbGxfbnVtYmVyIiwiZGF0ZV9vZl9iaXJ0aCIsImFhZGhhYXJfcmVmIiwibWFya3MiXX0.DvSsxzm-T5cv20VpGGIk6DJ2dv8WyoY4pySDcFMNHIsKk79d2gv2IdyQcXTlmPW3TV8SX8oOYqH50nb9cDSVDw",
    description: "Authentic ZK predicate proof. Validates age and 12th passing status without exposing DOB or marks.",
  },
  {
    label: "⏳ Expired University Admission Proof",
    token:
      "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCIsImtpZCI6ImRpZ2lpbi1lZDI1NTE5LWtleS0yMDI2In0.eyJpc3MiOiJEaWdpSW4gU3ludGhldGljIFZlcmlmaWVyIiwic3ViIjoic3Vial9kZW1vXzVjN2I5MCIsImF1ZCI6IlVOSVZfQURNSVNTSU9OUyIsInB1cnBvc2UiOiJVbml2ZXJzaXR5IEFkbWlzc2lvbnMgMjAyNSIsImlhdCI6IjIwMjUtMDgtMjJUMTI6MDA6MDBaIiwiZXhwIjoiMjAyNS0wOC0yMlQxODowMDowMFoiLCJwcmVkaWNhdGVfcHJvb2ZzIjpbeyJjbGFpbU5hbWUiOiJDTEFTU19YSUkiLCJleHByZXNzaW9uIjoiMTJ0aCBCb2FyZCA9PSBQQVNTRUQiLCJzYXRpc2ZpZWQiOnRydWUsInByb29mVHlwZSI6IkRFUklWRURfWkVST19LTk9XTEVER0VfUFJFRElDQVRFIn1dfQ.O72DfHPoa7wk-0O8TBXh82gcJCx90yVpZEAyywY0FljnkMbmEZP81zxSn8nU3xMqoQ9Kj8ebbIWoOdzeZipWDA",
    description: "Proof token whose validity timestamp has expired.",
  },
  {
    label: "⚠️ Forged / Altered Payload Proof (Tampered)",
    token:
      "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCIsImtpZCI6ImRpZ2lpbi1lZDI1NTE5LWtleS0yMDI2In0.eyJpc3MiOiJEaWdpSW4gU3ludGhldGljIFZlcmlmaWVyIiwic3ViIjoic3Vial9GT1JHRURfVVNFUiIsImF1ZCI6IlRBTVAiLCJwdXJwb3NlIjoiRkFLRSAyMDI2IiwicHJlZGljYXRlX3Byb29mcyI6W3siY2xhaW1OYW1lIjoiQUdFIiwic2F0aXNmaWVkIjp0cnVlfV19.ZmFrZV9zaWduYXR1cmVfaW52YWxpZF9ieXRlc18wMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAw",
    description: "Payload with modified claims and non-matching signature bytes.",
  },
];

export const OfflineScannerModal: React.FC<Props> = ({

  isOpen,
  onClose,
  initialToken = "",
}) => {
  const [activeTab, setActiveTab] = useState<"CAMERA" | "FILE" | "PASTE">("PASTE");
  const [tokenInput, setTokenInput] = useState(initialToken);
  const [isAirGapped, setIsAirGapped] = useState(true);
  const [scanResult, setScanResult] = useState<OfflineVerificationResult | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);

  useEffect(() => {
    if (initialToken) {
      setTokenInput(initialToken);
      runVerification(initialToken);
    }
  }, [initialToken, isOpen]);

  const runVerification = async (tok: string) => {
    if (!tok.trim()) {
      setScanResult(null);
      return;
    }
    setIsVerifying(true);
    try {
      const res = await verifyProofTokenOffline(tok);
      setScanResult(res);
    } finally {
      setIsVerifying(false);
    }
  };

  const handlePresetSelect = (tok: string) => {
    setTokenInput(tok);
    runVerification(tok);
  };

  const handleTamperToken = () => {
    if (!tokenInput || tokenInput.split(".").length !== 3) return;
    const parts = tokenInput.split(".");
    const p = parts[1];
    const tamperedP = p.slice(0, 10) + (p[10] === "a" ? "b" : "a") + p.slice(11);
    const forgedSig = "ZmFrZV9zaWduYXR1cmVfaW52YWxpZF9ieXRlc18wMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAw";
    const forged = `${parts[0]}.${tamperedP}.${forgedSig}`;
    setTokenInput(forged);
    runVerification(forged);
  };


  if (!isOpen) return null;

  return (
    <div className="modal-overlay scanner-overlay" role="dialog" aria-modal="true" aria-label="Offline QR Code Scanner">
      <div className="modal-content scanner-modal-content">
        <div className="modal-header">
          <div className="scanner-title-block">
            <p className="eyebrow">AIR-GAPPED FIELD VERIFICATION</p>
            <h3>Offline QR Code Verifier Scanner</h3>
          </div>
          <div className="header-badge-group">
            <label className="airgap-toggle-label">
              <input
                type="checkbox"
                checked={isAirGapped}
                onChange={(e) => setIsAirGapped(e.target.checked)}
              />
              <span className="airgap-badge">
                {isAirGapped ? "📡 100% Offline (0 Network Calls)" : "🌐 Online Sync"}
              </span>
            </label>
            <button type="button" className="modal-close" onClick={onClose} aria-label="Close modal">
              &times;
            </button>
          </div>
        </div>

        <p className="scanner-desc">
          Field officers verify citizen credentials instantly without network connectivity by mathematically checking the asymmetric Ed25519 digital signature against pre-cached public JWKS keys.
        </p>

        {/* Input Methods */}
        <div className="scanner-tabs-bar" role="tablist">
          <button
            type="button"
            className={`scanner-tab-btn ${activeTab === "PASTE" ? "active" : ""}`}
            onClick={() => setActiveTab("PASTE")}
          >
            📋 JWS Token & Tamper Sandbox
          </button>
          <button
            type="button"
            className={`scanner-tab-btn ${activeTab === "CAMERA" ? "active" : ""}`}
            onClick={() => setActiveTab("CAMERA")}
          >
            📷 Camera Viewfinder Simulation
          </button>
          <button
            type="button"
            className={`scanner-tab-btn ${activeTab === "FILE" ? "active" : ""}`}
            onClick={() => setActiveTab("FILE")}
          >
            🖼️ Upload QR Image
          </button>
        </div>

        {/* Tab 1: Token Paste & Interactive Tamper Test */}
        {activeTab === "PASTE" && (
          <div className="scanner-paste-section">
            {/* Quick Sample Presets */}
            <div className="preset-scans-row">
              <span className="preset-label">Quick Scan Presets:</span>
              <div className="preset-buttons">
                {PRESET_SCAN_SAMPLES.map((sample, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="preset-scan-btn"
                    onClick={() => handlePresetSelect(sample.token)}
                  >
                    {sample.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="token-input-box">
              <label>
                <strong>Paste Scanned Compact Proof String (JWS):</strong>
                <textarea
                  value={tokenInput}
                  onChange={(e) => {
                    setTokenInput(e.target.value);
                    runVerification(e.target.value);
                  }}
                  rows={4}
                  placeholder="Paste eyJhbGciOiJFZERTQ... token string here"
                  className="token-scan-textarea"
                />
              </label>
            </div>

            <div className="sandbox-actions-row">
              <button
                type="button"
                className="secondary verify-trigger-btn"
                onClick={() => runVerification(tokenInput)}
                disabled={!tokenInput || isVerifying}
              >
                {isVerifying ? "Verifying..." : "⚡ Run Cryptographic Check"}
              </button>

              <button
                type="button"
                className="danger tamper-test-btn"
                onClick={handleTamperToken}
                disabled={!tokenInput}
                title="Modifies 1 character in the payload to simulate forgery"
              >
                🧪 Simulate Payload Tamper (Mutate 1 Byte)
              </button>
            </div>
          </div>
        )}

        {/* Tab 2: Camera Viewfinder Simulation */}
        {activeTab === "CAMERA" && (
          <div className="camera-viewfinder-box">
            <div className="viewfinder-frame">
              <div className="laser-scanner-line" />
              <div className="viewfinder-overlay-text">
                <span className="camera-icon">📷</span>
                <strong>Live QR Camera Stream</strong>
                <small>Align verifiable credential QR code within the viewfinder frame</small>
              </div>
            </div>
            <div className="viewfinder-actions">
              <button
                type="button"
                className="primary-action"
                onClick={() => handlePresetSelect(PRESET_SCAN_SAMPLES[0].token)}
              >
                📸 Capture Sample QR Code (NTA Exam Proof)
              </button>
            </div>
          </div>
        )}

        {/* Tab 3: Upload QR Image */}
        {activeTab === "FILE" && (
          <div className="upload-qr-dropzone">
            <span className="dropzone-icon">🖼️</span>
            <strong>Drop QR Code Image File Here (PNG, JPG)</strong>
            <p>Or click to select an image from your device storage.</p>
            <button
              type="button"
              className="secondary"
              onClick={() => handlePresetSelect(PRESET_SCAN_SAMPLES[0].token)}
            >
              Simulate Loading 'digiin_qr_exam.png'
            </button>
          </div>
        )}

        {/* Verification Result Receipt Card */}
        {scanResult && (
          <div
            className={`scanner-verdict-card ${
              scanResult.status === "VALID_OFFLINE"
                ? "verdict-valid"
                : scanResult.status === "EXPIRED_PROOF"
                ? "verdict-expired"
                : "verdict-tampered"
            }`}
          >
            <div className="verdict-header">
              <div>
                <span
                  className={`verdict-badge ${
                    scanResult.status === "VALID_OFFLINE"
                      ? "badge-valid"
                      : scanResult.status === "EXPIRED_PROOF"
                      ? "badge-expired"
                      : "badge-tampered"
                  }`}
                >
                  {scanResult.status === "VALID_OFFLINE"
                    ? "✓ AUTHENTIC (OFFLINE ED25519 VERIFIED)"
                    : scanResult.status === "EXPIRED_PROOF"
                    ? "⏳ EXPIRED PROOF"
                    : "⚠️ TAMPERED / FORGED SIGNATURE"}
                </span>
                <h4 className="verdict-title">
                  {scanResult.status === "VALID_OFFLINE"
                    ? "Cryptographic Signature Mathematically Valid"
                    : scanResult.errorMessage || "Digital signature validation failed."}
                </h4>
              </div>
              <div className="verdict-meta-badges">
                <span className="meta-pill">⚡ {scanResult.latencyMs}ms Latency</span>
                <span className="meta-pill">Key: {scanResult.keyId}</span>
              </div>
            </div>

            {scanResult.status === "VALID_OFFLINE" && (
              <>
                <div className="verdict-details-grid">
                  <div>
                    <span className="meta-label">Issuing Authority:</span>
                    <strong>{scanResult.issuer}</strong>
                  </div>
                  {scanResult.purpose && (
                    <div>
                      <span className="meta-label">Bounded Purpose:</span>
                      <span>{scanResult.purpose}</span>
                    </div>
                  )}
                  {scanResult.audience && (
                    <div>
                      <span className="meta-label">Bound Audience:</span>
                      <code>{scanResult.audience}</code>
                    </div>
                  )}
                </div>

                {/* Verified Predicates List */}
                {scanResult.predicateProofs.length > 0 && (
                  <div className="verified-predicates-panel">
                    <h5>🛡️ Verified Zero-Knowledge Boolean Claims:</h5>
                    <ul className="predicates-checklist">
                      {scanResult.predicateProofs.map((p, idx) => (
                        <li key={idx} className="predicate-check-item">
                          <span className="check-mark">✓</span>
                          <div>
                            <strong>{p.expression}</strong>
                            <small className="zk-proof-tag">Proof: {p.proofType} (PASS)</small>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Masked PII Assurance */}
                {scanResult.maskedAttributes.length > 0 && (
                  <div className="masked-assurance-box">
                    <span className="masked-label">🔒 Sovereign Privacy Guarantee:</span>
                    <p>
                      The following sensitive attributes were <strong>never exposed</strong> in this QR token:{" "}
                      <code>{scanResult.maskedAttributes.join(", ")}</code>.
                    </p>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
