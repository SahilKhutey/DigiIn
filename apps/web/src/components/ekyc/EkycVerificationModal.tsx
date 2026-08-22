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

const PRESET_IDENTITIES = [
  {
    label: "👤 Sahil Khutey (Candidate)",
    ref: "9100-2026-9921",
    name: "SAHIL KHUTEY",
    dob: "2006-05-14",
    mobile: "+91 ******9921",
    otp: "202601",
  },
  {
    label: "👤 Ramesh Patel (Citizen)",
    ref: "8200-1998-4412",
    name: "RAMESH PATEL",
    dob: "1978-11-20",
    mobile: "+91 ******4412",
    otp: "199801",
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
  const [aadhaarRef, setAadhaarRef] = useState("9100-2026-9921");
  const [otp, setOtp] = useState("");
  const [txnData, setTxnData] = useState<EkycOtpResponse | null>(null);
  const [verifyResult, setVerifyResult] = useState<EkycVerifyResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [countdown, setCountdown] = useState(600);

  useEffect(() => {
    if (!isOpen) {
      setStep("ENTER_REF");
      setOtp("");
      setTxnData(null);
      setVerifyResult(null);
      setErrorMessage(null);
    }
  }, [isOpen]);

  useEffect(() => {
    let timer: any;
    if (step === "ENTER_OTP" && countdown > 0) {
      timer = setInterval(() => setCountdown((c) => Math.max(0, c - 1)), 1000);
    }
    return () => clearInterval(timer);
  }, [step, countdown]);

  if (!isOpen) return null;

  const handleGenerateOtp = async (refToUse?: string) => {
    setLoading(true);
    setErrorMessage(null);
    const targetRef = refToUse || aadhaarRef;
    try {
      const res = await generateEkycOtp(targetRef, `Verification of ${documentTitle || "Citizen Document"}`);
      setTxnData(res);
      setCountdown(res.expiresInSeconds);
      setStep("ENTER_OTP");
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to generate eKYC OTP");
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
      setErrorMessage(err.message || "OTP verification failed");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPreset = (p: typeof PRESET_IDENTITIES[0]) => {
    setAadhaarRef(p.ref);
    handleGenerateOtp(p.ref);
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-container ekyc-modal-content" role="dialog" aria-modal="true" aria-label="Aadhaar eKYC Gateway">
        <div className="modal-header">
          <div>
            <span className="trust-level-pill" style={{ background: "#eff6ff", color: "#1d4ed8" }}>
              🔐 SOVEREIGN IDENTITY GATEWAY
            </span>
            <h3>Aadhaar / eKYC Identity Verification</h3>
          </div>
          <button className="btn-close" onClick={onClose} aria-label="Close modal">
            &times;
          </button>
        </div>

        {/* Stepper Progress Bar */}
        <div className="ekyc-stepper">
          <div className={`step-item ${step === "ENTER_REF" ? "active" : step === "ENTER_OTP" || step === "VERIFIED_RECEIPT" ? "completed" : ""}`}>
            <div className="step-circle">1</div>
            <span>Virtual ID</span>
          </div>
          <div className="step-connector" />
          <div className={`step-item ${step === "ENTER_OTP" ? "active" : step === "VERIFIED_RECEIPT" ? "completed" : ""}`}>
            <div className="step-circle">2</div>
            <span>OTP Auth</span>
          </div>
          <div className="step-connector" />
          <div className={`step-item ${step === "VERIFIED_RECEIPT" ? "completed active" : ""}`}>
            <div className="step-circle">3</div>
            <span>Demographic Match</span>
          </div>
        </div>

        {/* Privacy Assurance Banner */}
        <div className="privacy-assurance-box">
          <strong>🛡️ Zero Raw Aadhaar Storage Guarantee:</strong> DigiIn never captures or stores 12-digit Aadhaar numbers or biometrics. All verifications use masked Virtual IDs (VID) and issue tamper-evident asymmetric cryptographic tokens (Ed25519).
        </div>

        {errorMessage && (
          <div className="error-alert" role="alert">
            ⚠️ {errorMessage}
          </div>
        )}

        {/* STEP 1: Enter Virtual ID */}
        {step === "ENTER_REF" && (
          <div className="ekyc-step-content">
            <p className="step-instruction">
              Authenticate your identity to elevate <strong>{documentTitle || "your document"}</strong> to <strong>Level 4: Government Verified</strong>.
            </p>

            <div className="form-group">
              <label htmlFor="aadhaar-ref-input">
                <strong>Enter Aadhaar Reference or 16-Digit Virtual ID (VID):</strong>
              </label>
              <input
                id="aadhaar-ref-input"
                type="text"
                className="input-field"
                placeholder="e.g. 9100-2026-9921"
                value={aadhaarRef}
                onChange={(e) => setAadhaarRef(e.target.value)}
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
                disabled={loading || !aadhaarRef}
              >
                {loading ? "Generating OTP..." : "📲 Generate Simulated OTP"}
              </button>
            </div>
          </div>
        )}

        {/* STEP 2: Enter 6-Digit OTP */}
        {step === "ENTER_OTP" && txnData && (
          <div className="ekyc-step-content">
            <div className="otp-sent-banner">
              <span>📩 Simulated 6-digit OTP sent to: <strong>{txnData.maskedMobile}</strong></span>
              <span className="otp-countdown">⏱️ Expires in {Math.floor(countdown / 60)}:{(countdown % 60).toString().padStart(2, "0")}</span>
            </div>

            <div className="form-group" style={{ textAlign: "center", margin: "1.5rem 0" }}>
              <label htmlFor="ekyc-otp-input" style={{ display: "block", marginBottom: "0.5rem" }}>
                <strong>Enter 6-Digit eKYC OTP:</strong>
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
              <span>💡 Demonstration Hint: Expected OTP is <code>{txnData.demoOtpHint}</code></span>
              <button
                type="button"
                className="btn btn-sm btn-outline"
                style={{ marginLeft: "0.75rem" }}
                onClick={() => setOtp(txnData.demoOtpHint)}
              >
                Auto-fill Demo OTP
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
                {loading ? "Verifying Demographics..." : "🔐 Verify & Match Identity"}
              </button>
            </div>
          </div>
        )}

        {/* STEP 3: Verified Demographics & Elevation Receipt */}
        {step === "VERIFIED_RECEIPT" && verifyResult && (
          <div className="ekyc-step-content verified-receipt-section">
            <div className="ekyc-success-banner">
              <div className="success-icon">✓</div>
              <div>
                <h4>eKYC Demographic Verification Successful</h4>
                <p>Identity established with official registry fixture. Document trust level elevated.</p>
              </div>
              <div className="match-score-badge">
                <span className="score-num">{verifyResult.matchResult.score}%</span>
                <span className="score-label">{verifyResult.matchResult.verdict}</span>
              </div>
            </div>

            {/* Elevation Notification */}
            {verifyResult.elevatedDocumentLevel && (
              <div className="elevation-alert-box">
                🛡️ <strong>Trust Level Elevated to Level 4 (Government Verified)</strong>
                <p style={{ margin: "0.25rem 0 0 0", fontSize: "0.85rem" }}>
                  The document has been bound to an authentic sovereign Aadhaar eKYC assertion signed with Ed25519.
                </p>
              </div>
            )}

            {/* Demographics Comparison Table */}
            <h4 style={{ margin: "1rem 0 0.5rem 0" }}>📋 Side-by-Side Demographic Verification</h4>
            <div className="demographics-diff-table">
              <div className="diff-header-row">
                <span>Attribute</span>
                <span>Claimed Document Value</span>
                <span>Official eKYC Registry Record</span>
                <span>Status</span>
              </div>
              <div className="diff-data-row">
                <span className="attr-name">Full Name</span>
                <span>{verifyResult.matchResult.claimedValues.name || "SAHIL KHUTEY"}</span>
                <span>{verifyResult.identitySnapshot.name}</span>
                <span className="badge-match">✓ {verifyResult.matchResult.nameMatch ? "MATCHED" : "MISMATCH"}</span>
              </div>
              <div className="diff-data-row">
                <span className="attr-name">Date of Birth</span>
                <span>{verifyResult.matchResult.claimedValues.dob || "2006-05-14"}</span>
                <span>{verifyResult.identitySnapshot.dob}</span>
                <span className="badge-match">✓ {verifyResult.matchResult.dobMatch ? "VERIFIED" : "DISCREPANCY"}</span>
              </div>
              <div className="diff-data-row">
                <span className="attr-name">Masked Aadhaar</span>
                <span>—</span>
                <span>{verifyResult.identitySnapshot.maskedAadhaar}</span>
                <span className="badge-match">🔒 SOVEREIGN</span>
              </div>
              <div className="diff-data-row">
                <span className="attr-name">Jurisdiction / State</span>
                <span>{verifyResult.matchResult.claimedValues.state || "Chhattisgarh"}</span>
                <span>{verifyResult.identitySnapshot.state}</span>
                <span className="badge-match">✓ RESIDENT</span>
              </div>
            </div>

            {/* Cryptographic Signature Assertion Details */}
            <div className="ekyc-crypto-token-box">
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.25rem" }}>
                <strong>Signed eKYC Assertion ({verifyResult.algorithm})</strong>
                <span className="key-id-tag">Key: {verifyResult.keyId}</span>
              </div>
              <code>{verifyResult.ekycProofToken}</code>
            </div>

            <div className="modal-actions" style={{ marginTop: "1.5rem" }}>
              <button className="btn btn-primary" onClick={onClose}>
                ✓ Done & Return to Wallet
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
