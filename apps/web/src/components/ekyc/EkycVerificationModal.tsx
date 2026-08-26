import React, { useState, useEffect } from "react";
import { generateEkycOtp, verifyEkycOtp } from "../../api/client";
import type { EkycOtpResponse, EkycVerifyResponse } from "../../types";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  documentId?: string;
  documentTitle?: string;
  onVerificationSuccess?: (result: EkycVerifyResponse) => void;
}

/**
 * Demo Identity Verification modal.
 *
 * SANDBOX DEMO — No connection to Aadhaar, UIDAI, or any real government identity service.
 * All identities, OTPs, and credentials are synthetic demo fixtures for demonstration only.
 */
const PRESET_IDENTITIES = [
  {
    label: "👤 Demo Citizen A (DIN-DEMO-001)",
    ref: "DEMO-ID-001",
    name: "DEMO CITIZEN A",
    dob: "2006-01-01",
    mobile: "+91 ******0001",
    otp: "000000",
  },
  {
    label: "👤 Demo Citizen B (DIN-DEMO-002)",
    ref: "DEMO-ID-002",
    name: "DEMO CITIZEN B",
    dob: "1978-01-01",
    mobile: "+91 ******0002",
    otp: "000000",
  },
];

export const EkycVerificationModal: React.FC<Props> = ({
  isOpen,
  onClose,
  documentId,
  documentTitle,
  onVerificationSuccess,
}) => {
  const [step, setStep] = useState<"ENTER_REF" | "ENTER_OTP" | "VERIFIED_RECEIPT">("ENTER_REF");
  const [demoRef, setDemoRef] = useState("DEMO-ID-001");
  const [otp, setOtp] = useState("");
  const [txnData, setTxnData] = useState<EkycOtpResponse | null>(null);
  const [verifyResult, setVerifyResult] = useState<EkycVerifyResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [countdown, setCountdown] = useState(600);

  useEffect(() => {
    if (!isOpen) {
      setStep("ENTER_REF");
      setDemoRef("DEMO-ID-001");
      setOtp("");
      setTxnData(null);
      setVerifyResult(null);
      setErrorMessage(null);
      setCountdown(600);
    }
  }, [isOpen]);

  useEffect(() => {
    let timer: ReturnType<typeof setInterval>;
    if (step === "ENTER_OTP" && countdown > 0) {
      timer = setInterval(() => setCountdown((c) => Math.max(0, c - 1)), 1000);
    }
    return () => clearInterval(timer);
  }, [step, countdown]);

  if (!isOpen) return null;

  const handleGenerateOtp = async (refToUse?: string) => {
    setLoading(true);
    setErrorMessage(null);
    const targetRef = refToUse || demoRef;
    try {
      const res = await generateEkycOtp(targetRef, `Demo verification of ${documentTitle || "citizen document"}`);
      setTxnData(res);
      setCountdown(res.expiresInSeconds);
      setStep("ENTER_OTP");
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to generate Demo OTP");
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async () => {
    if (!txnData) return;
    setLoading(true);
    setErrorMessage(null);
    try {
      const res = await verifyEkycOtp(txnData.txnId, otp, documentId);
      setVerifyResult(res);
      setStep("VERIFIED_RECEIPT");
      if (onVerificationSuccess) {
        onVerificationSuccess(res);
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Demo OTP verification failed");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPreset = (p: typeof PRESET_IDENTITIES[0]) => {
    setDemoRef(p.ref);
    handleGenerateOtp(p.ref);
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-container ekyc-modal-content" role="dialog" aria-modal="true" aria-label="DigiIn Demo Identity Verification">
        <div className="modal-header">
          <div>
            {/* SANDBOX badge row */}
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
              <span className="trust-level-pill" style={{ background: "#f0fdf4", color: "#166534" }}>
                🧪 DigiIn Demo Verification
              </span>
              <span style={{ background: "#FEF3C7", color: "#92400E", fontSize: "10px", fontWeight: 800, padding: "2px 8px", borderRadius: "6px", border: "1px solid #F59E0B" }}>
                ⚠️ SANDBOX — No real identity service connected
              </span>
            </div>
            <h3>Demo Identity Verification</h3>
          </div>
          <button className="btn-close" onClick={onClose} aria-label="Close modal">
            &times;
          </button>
        </div>

        {/* Stepper Progress Bar */}
        <div className="ekyc-stepper">
          <div className={`step-item ${step === "ENTER_REF" ? "active" : step === "ENTER_OTP" || step === "VERIFIED_RECEIPT" ? "completed" : ""}`}>
            <div className="step-circle">1</div>
            <span>Demo ID</span>
          </div>
          <div className="step-connector" />
          <div className={`step-item ${step === "ENTER_OTP" ? "active" : step === "VERIFIED_RECEIPT" ? "completed" : ""}`}>
            <div className="step-circle">2</div>
            <span>Demo OTP</span>
          </div>
          <div className="step-connector" />
          <div className={`step-item ${step === "VERIFIED_RECEIPT" ? "completed active" : ""}`}>
            <div className="step-circle">3</div>
            <span>Demo Match</span>
          </div>
        </div>

        {/* Privacy Assurance Banner */}
        <div className="privacy-assurance-box">
          <strong>🛡️ Synthetic Data Only:</strong> This demo uses fictional identities and synthetic credentials.
          No real identity data, Aadhaar numbers, or government records are accessed or stored.
        </div>

        {errorMessage && (
          <div className="error-alert" role="alert">
            ⚠️ {errorMessage}
          </div>
        )}

        {/* STEP 1: Enter Demo Identity Reference */}
        {step === "ENTER_REF" && (
          <div className="ekyc-step-content">
            <p className="step-instruction">
              Select a demo identity to simulate verification of{" "}
              <strong>{documentTitle || "your document"}</strong>.
              This demonstrates DigiIn's verification flow using synthetic sandbox data.
            </p>

            <div className="form-group">
              <label htmlFor="demo-ref-input">
                <strong>Demo Identity Reference:</strong>
              </label>
              <input
                id="demo-ref-input"
                type="text"
                className="input-field"
                placeholder="e.g. DEMO-ID-001"
                value={demoRef}
                onChange={(e) => setDemoRef(e.target.value)}
              />
            </div>

            <div className="quick-presets-section">
              <span className="preset-label">Quick Demo Profiles:</span>
              <div className="preset-buttons-row">
                {PRESET_IDENTITIES.map((p) => (
                  <button
                    key={p.ref}
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={() => handleSelectPreset(p)}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="modal-actions" style={{ marginTop: "1.5rem" }}>
              <button className="btn btn-outline" onClick={onClose}>
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={() => handleGenerateOtp()}
                disabled={loading || !demoRef}
              >
                {loading ? "Generating..." : "📲 Generate Demo OTP"}
              </button>
            </div>
          </div>
        )}

        {/* STEP 2: Enter Demo OTP */}
        {step === "ENTER_OTP" && txnData && (
          <div className="ekyc-step-content">
            <div className="otp-sent-banner">
              <span>📩 Demo OTP sent to: <strong>{txnData.maskedMobile}</strong></span>
              <span className="otp-countdown">⏱️ Expires in {Math.floor(countdown / 60)}:{(countdown % 60).toString().padStart(2, "0")}</span>
            </div>

            <div className="form-group" style={{ textAlign: "center", margin: "1.5rem 0" }}>
              <label htmlFor="ekyc-otp-input" style={{ display: "block", marginBottom: "0.5rem" }}>
                <strong>Enter 6-Digit Demo OTP:</strong>
              </label>
              <input
                id="ekyc-otp-input"
                type="text"
                maxLength={6}
                className="input-field otp-input"
                placeholder="• • • • • •"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                autoFocus
              />
            </div>

            <div className="demo-hint-box">
              <span>💡 Demo hint: OTP is <code>{txnData.demoOtpHint}</code></span>
              <button
                type="button"
                className="btn btn-sm btn-outline"
                style={{ marginLeft: "0.75rem" }}
                onClick={() => setOtp(txnData.demoOtpHint)}
              >
                Auto-fill
              </button>
            </div>

            <div className="modal-actions" style={{ marginTop: "1.5rem" }}>
              <button className="btn btn-outline" onClick={() => setStep("ENTER_REF")}>
                Back
              </button>
              <button
                className="btn btn-primary btn-verify-otp"
                onClick={handleVerifyOtp}
                disabled={loading || otp.length !== 6}
              >
                {loading ? "Verifying..." : "🔐 Verify Demo Identity"}
              </button>
            </div>
          </div>
        )}

        {/* STEP 3: Demo Verification Receipt */}
        {step === "VERIFIED_RECEIPT" && verifyResult && (
          <div className="ekyc-step-content verified-receipt-section">
            <div className="ekyc-success-banner">
              <div className="success-icon">✓</div>
              <div>
                <h4>Demo Identity Verification Complete</h4>
                <p>Demo credential matched against synthetic sandbox fixture.</p>
              </div>
              <div className="match-score-badge">
                <span className="score-num">{verifyResult.matchResult.score}%</span>
                <span className="score-label">{verifyResult.matchResult.verdict}</span>
              </div>
            </div>

            {/* Trust Level Elevation */}
            {verifyResult.elevatedDocumentLevel && (
              <div className="elevation-alert-box">
                🧪 <strong>Verified by DigiIn Demo Issuer</strong>
                <p style={{ margin: "0.25rem 0 0 0", fontSize: "0.85rem" }}>
                  Document bound to synthetic demo assertion signed with Ed25519. (Sandbox only)
                </p>
              </div>
            )}

            {/* Demographics Comparison Table */}
            <h4 style={{ margin: "1rem 0 0.5rem 0" }}>📋 Demo Credential Comparison</h4>
            <div className="demographics-diff-table">
              <div className="diff-header-row">
                <span>Attribute</span>
                <span>Document Value</span>
                <span>Demo Issuer Record</span>
                <span>Status</span>
              </div>
              <div className="diff-data-row">
                <span className="attr-name">Full Name</span>
                <span>{verifyResult.matchResult.claimedValues.name || "DEMO CITIZEN A"}</span>
                <span>{verifyResult.identitySnapshot.name}</span>
                <span className="badge-match">✓ {verifyResult.matchResult.nameMatch ? "MATCHED" : "MISMATCH"}</span>
              </div>
              <div className="diff-data-row">
                <span className="attr-name">Date of Birth</span>
                <span>{verifyResult.matchResult.claimedValues.dob || "2006-01-01"}</span>
                <span>{verifyResult.identitySnapshot.dob}</span>
                <span className="badge-match">✓ {verifyResult.matchResult.dobMatch ? "VERIFIED" : "DISCREPANCY"}</span>
              </div>
              <div className="diff-data-row">
                <span className="attr-name">Demo ID Reference</span>
                <span>—</span>
                <span>{verifyResult.identitySnapshot.maskedAadhaar || "DEMO-ID-***"}</span>
                <span className="badge-match">🧪 SANDBOX</span>
              </div>
              <div className="diff-data-row">
                <span className="attr-name">Jurisdiction / State</span>
                <span>{verifyResult.matchResult.claimedValues.state || "Demo State"}</span>
                <span>{verifyResult.identitySnapshot.state}</span>
                <span className="badge-match">✓ RESIDENT</span>
              </div>
            </div>

            {/* Demo Cryptographic Assertion */}
            <div className="ekyc-crypto-token-box">
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.25rem" }}>
                <strong>Demo Signed Assertion ({verifyResult.algorithm})</strong>
                <span className="key-id-tag">Key: {verifyResult.keyId}</span>
              </div>
              <code>{verifyResult.ekycProofToken}</code>
            </div>

            <div className="modal-actions" style={{ marginTop: "1.5rem" }}>
              <button className="btn btn-primary" onClick={onClose}>
                ✓ Done &amp; Return to Wallet
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
