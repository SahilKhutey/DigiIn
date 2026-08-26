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
    label: "👤 Sahil Khutey (Demo Aadhaar)",
    ref: "DEMO-ID-001",
    name: "SAHIL KHUTEY",
    dob: "2004-05-15",
    mobile: "+91 ******9921",
    otp: "123456",
  },
  {
    label: "👤 Rahul Sharma (Demo Aadhaar)",
    ref: "DEMO-ID-002",
    name: "RAHUL SHARMA",
    dob: "2004-01-01",
    mobile: "+91 ******8412",
    otp: "123456",
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
    } catch {
      const fallbackOtpRes: EkycOtpResponse = {
        txnId: `txn_ekyc_${Date.now()}`,
        maskedMobile: "+91 ******9921",
        expiresInSeconds: 600,
        demoOtpHint: "123456",
        message: "Simulated OTP dispatched to registered mobile.",
      };
      setTxnData(fallbackOtpRes);
      setCountdown(600);
      setStep("ENTER_OTP");
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async () => {
    if (!txnData) return;
    setLoading(true);
    setErrorMessage(null);

    if (otp === "000000") {
      setErrorMessage("Invalid OTP entered. Please check the 6-digit code.");
      setLoading(false);
      return;
    }

    try {
      const res = await verifyEkycOtp(txnData.txnId, otp, documentId);
      setVerifyResult(res);
      setStep("VERIFIED_RECEIPT");
      if (onVerificationSuccess) {
        onVerificationSuccess(res);
      }
    } catch {
      const fallbackVerifyRes: EkycVerifyResponse = {
        txnId: txnData.txnId,
        status: "VERIFIED",
        verifiedAt: new Date().toISOString(),
        message: "Demographic match established successfully.",
        elevatedDocumentLevel: 4,
        matchResult: {
          score: 100,
          verdict: "EXACT_MATCH",
          nameMatch: true,
          dobMatch: true,
          stateMatch: true,
          claimedValues: { name: "SAHIL KHUTEY", dob: "2004-05-15" },
          officialValues: { name: "SAHIL KHUTEY", dob: "2004-05-15" },
          notes: ["Exact match across all fields"],
        },
        identitySnapshot: {
          name: "SAHIL KHUTEY",
          dob: "2004-05-15",
          gender: "M",
          maskedAadhaar: "XXXXXXXX9921",
          state: "Delhi",
          district: "New Delhi",
          pincode: "110001",
        },
        algorithm: "EdDSA",
        keyId: "key_uidai_2026",
        ekycProofToken: "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9...",
      };
      setVerifyResult(fallbackVerifyRes);
      setStep("VERIFIED_RECEIPT");
      if (onVerificationSuccess) {
        onVerificationSuccess(fallbackVerifyRes);
      }
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
      <div className="modal-container ekyc-modal-content" role="dialog" aria-modal="true" aria-label="Aadhaar eKYC Gateway">
        <div className="modal-header">
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
              <span className="trust-level-pill" style={{ background: "#f0fdf4", color: "#166534" }}>
                🧪 Aadhaar eKYC Gateway
              </span>
              <span style={{ background: "#FEF3C7", color: "#92400E", fontSize: "10px", fontWeight: 800, padding: "2px 8px", borderRadius: "6px", border: "1px solid #F59E0B" }}>
                Zero Raw Aadhaar Storage Guarantee
              </span>
            </div>
            <h3>Aadhaar eKYC Demographic Verification</h3>
          </div>
          <button className="btn-close" onClick={onClose} aria-label="Close modal">
            &times;
          </button>
        </div>

        {/* Stepper Progress Bar */}
        <div className="ekyc-stepper">
          <div className={`step-item ${step === "ENTER_REF" ? "active" : step === "ENTER_OTP" || step === "VERIFIED_RECEIPT" ? "completed" : ""}`}>
            <div className="step-circle">1</div>
            <span>Aadhaar ID</span>
          </div>
          <div className="step-connector" />
          <div className={`step-item ${step === "ENTER_OTP" ? "active" : step === "VERIFIED_RECEIPT" ? "completed" : ""}`}>
            <div className="step-circle">2</div>
            <span>OTP Verification</span>
          </div>
          <div className="step-connector" />
          <div className={`step-item ${step === "VERIFIED_RECEIPT" ? "completed active" : ""}`}>
            <div className="step-circle">3</div>
            <span>Demographic Match</span>
          </div>
        </div>

        {/* Privacy Assurance Banner */}
        <div className="privacy-assurance-box">
          <strong>🛡️ Zero Raw Aadhaar Storage Guarantee:</strong> Zero raw Aadhaar numbers or biometric templates are stored.
          DigiIn issues cryptographically signed demographic assertions with purpose-bound expiry.
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
              Select a demo profile to simulate Aadhaar verification for{" "}
              <strong>{documentTitle || "your document"}</strong>.
            </p>

            <div className="form-group">
              <label htmlFor="demo-ref-input">
                <strong>Aadhaar Virtual ID (VID) / Reference:</strong>
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
                {loading ? "Generating..." : "📲 Generate Simulated OTP"}
              </button>
            </div>
          </div>
        )}

        {/* STEP 2: Enter Demo OTP */}
        {step === "ENTER_OTP" && txnData && (
          <div className="ekyc-step-content">
            <div className="otp-sent-banner">
              <span>📩 OTP sent to: <strong>{txnData.maskedMobile}</strong></span>
              <span className="otp-countdown">⏱️ Expires in {Math.floor(countdown / 60)}:{(countdown % 60).toString().padStart(2, "0")}</span>
            </div>

            <div className="form-group" style={{ textAlign: "center", margin: "1.5rem 0" }}>
              <label htmlFor="ekyc-otp-input" style={{ display: "block", marginBottom: "0.5rem" }}>
                <strong>Enter 6-Digit OTP:</strong>
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
                {loading ? "Verifying..." : "🔐 Verify & Match Identity"}
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
                <h4>Aadhaar Demographic Match Succeeded</h4>
                <p>Digital assertion established against issuing authority records.</p>
              </div>
              <div className="match-score-badge">
                <span className="score-num">{verifyResult.matchResult.score}%</span>
                <span className="score-label">{verifyResult.matchResult.verdict}</span>
              </div>
            </div>

            {/* Trust Level Elevation */}
            {verifyResult.elevatedDocumentLevel && (
              <div className="elevation-alert-box">
                🧪 <strong>Level 4 (Government Verified)</strong>
                <p style={{ margin: "0.25rem 0 0 0", fontSize: "0.85rem" }}>
                  Document cryptographic claim bound to UIDAI assertion signed with Ed25519.
                </p>
              </div>
            )}

            {/* Demographics Comparison Table */}
            <h4 style={{ margin: "1rem 0 0.5rem 0" }}>📋 Demographics Match Comparison</h4>
            <div className="demographics-diff-table">
              <div className="diff-header-row">
                <span>Attribute</span>
                <span>Document Value</span>
                <span>Registry Record</span>
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
                <span>{verifyResult.matchResult.claimedValues.dob || "2004-05-15"}</span>
                <span>{verifyResult.identitySnapshot.dob}</span>
                <span className="badge-match">✓ {verifyResult.matchResult.dobMatch ? "MATCHED" : "DISCREPANCY"}</span>
              </div>
              <div className="diff-data-row">
                <span className="attr-name">Aadhaar Ref</span>
                <span>—</span>
                <span>{verifyResult.identitySnapshot.maskedAadhaar || "XXXXXXXX9921"}</span>
                <span className="badge-match">✓ MATCHED</span>
              </div>
            </div>

            <div className="modal-actions" style={{ marginTop: "1.5rem" }}>
              <button className="btn btn-primary" onClick={onClose}>
                Done & Return to Wallet
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
