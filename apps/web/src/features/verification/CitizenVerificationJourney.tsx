import React, { useState, useEffect } from "react";
import { Button, Card, Badge, Alert, ProgressIndicator, OtpInput, ProgressStep } from "../../components/ui";
import { useLanguage } from "../../context/LanguageContext";

type JourneyStep =
  | "INGRESS"
  | "SCOPE"
  | "AUTH"
  | "CONSENT"
  | "PIPELINE"
  | "RESULT"
  | "RECEIPT"
  | "RECOVERY";

export const CitizenVerificationJourney: React.FC = () => {
  const { t } = useLanguage();
  const [currentStep, setCurrentStep] = useState<JourneyStep>("INGRESS");
  const [otpValue, setOtpValue] = useState<string>("992144");
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [zkpMode, setZkpMode] = useState(true);
  const [consentGranted, setConsentGranted] = useState(false);
  const [pipelineProgress, setPipelineProgress] = useState(0);
  const [failureScenario, setFailureScenario] = useState<"none" | "mismatch" | "unavailable">("none");
  const [receiptCopied, setReceiptCopied] = useState(false);

  // Progressive Pipeline Steps
  const progressSteps: ProgressStep[] = [
    {
      id: "step-auth",
      title: "DigiLocker Account Session",
      description: "Secure gateway token established with UIDAI identity binding. (Sandbox)",
      status: pipelineProgress >= 1 ? "completed" : "in_progress",
    },
    {
      id: "step-fetch",
      title: "Fetch Official Issuer Records",
      description: "Retrieving verified records directly from CBSE and UIDAI repositories. (Sandbox — synthetic data only)",
      status: pipelineProgress >= 2 ? "completed" : pipelineProgress === 1 ? "in_progress" : "pending",
    },
    {
      id: "step-rules",
      title: "Demographics & Rule Engine",
      description: "Matching candidate name, date of birth, and cutoff eligibility criteria.",
      status:
        failureScenario === "mismatch" && pipelineProgress >= 2
          ? "failed"
          : pipelineProgress >= 3
          ? "completed"
          : pipelineProgress === 2
          ? "in_progress"
          : "pending",
    },
    {
      id: "step-proof",
      title: "Generate Ed25519 Proof Receipt",
      description: "Signing verifiable claim receipt with RFC 7515/7519 compliance.",
      status: pipelineProgress >= 4 ? "completed" : pipelineProgress === 3 ? "in_progress" : "pending",
    },
  ];

  // Pipeline simulation timer
  useEffect(() => {
    if (currentStep === "PIPELINE") {
      setPipelineProgress(0);
      const t1 = setTimeout(() => setPipelineProgress(1), 700);
      const t2 = setTimeout(() => setPipelineProgress(2), 1600);
      const t3 = setTimeout(() => {
        if (failureScenario === "mismatch") {
          setCurrentStep("RECOVERY");
        } else {
          setPipelineProgress(3);
        }
      }, 2600);
      const t4 = setTimeout(() => {
        if (failureScenario !== "mismatch") {
          setPipelineProgress(4);
          setCurrentStep("RESULT");
        }
      }, 3600);

      return () => {
        clearTimeout(t1);
        clearTimeout(t2);
        clearTimeout(t3);
        clearTimeout(t4);
      };
    }
  }, [currentStep, failureScenario]);

  const handleStartAuth = () => {
    setIsAuthenticating(true);
    setTimeout(() => {
      setIsAuthenticating(false);
      setCurrentStep("CONSENT");
    }, 600);
  };

  const handleCopyReceipt = () => {
    navigator.clipboard.writeText("DLV-8F72-A92C");
    setReceiptCopied(true);
    setTimeout(() => setReceiptCopied(false), 2500);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Journey Stepper Breadcrumb Header */}
      <div className="bg-white border border-[#CBD5E1] rounded-xl p-4 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#0B5D9B] animate-pulse" />
            <span className="text-xs font-extrabold uppercase tracking-wider text-[#0B5D9B]">
              Citizen Verification Journey
            </span>
            <span className="text-slate-300">/</span>
            <span className="text-xs font-bold text-[#092F4F]">
              {currentStep === "INGRESS" && "1. Request Received"}
              {currentStep === "SCOPE" && "2. Scope of Sharing"}
              {currentStep === "AUTH" && "3. DigiLocker Authentication"}
              {currentStep === "CONSENT" && "4. Purpose & Consent"}
              {currentStep === "PIPELINE" && "5. Verifying Documents..."}
              {currentStep === "RESULT" && "6. Verification Result"}
              {currentStep === "RECEIPT" && "7. Cryptographic Receipt"}
              {currentStep === "RECOVERY" && "8. Explainable Recovery"}
            </span>
          </div>

          {/* Test Failure Trigger */}
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-slate-500 font-semibold">Test Scenario:</span>
            <select
              value={failureScenario}
              onChange={(e) => setFailureScenario(e.target.value as any)}
              className="text-xs bg-slate-50 border border-slate-300 rounded px-2 py-1 font-semibold text-slate-700 focus:outline-none focus:border-[#0B5D9B]"
              aria-label="Select test simulation scenario"
            >
              <option value="none">✓ Happy Path (Full Match)</option>
              <option value="mismatch">⚠ Demographic Mismatch</option>
            </select>
          </div>
        </div>
      </div>

      {/* =========================================================================
          STEP 1: INGRESS (Organization Verification Request)
          ========================================================================= */}
      {currentStep === "INGRESS" && (
        <Card variant="elevated" className="space-y-6">
          <div className="flex items-start justify-between gap-4 border-b border-slate-200 pb-4">
            <div className="space-y-1">
              <Badge variant="primary" size="sm">Verification Request</Badge>
              <h2 className="text-2xl font-bold text-[#092F4F] m-0">
                ABC University — Undergraduate Admissions 2026
              </h2>
              <p className="text-xs text-slate-500">
                Official Request Reference: <code>REQ-ABC-2026-UG991</code>
              </p>
            </div>
            <div className="w-12 h-12 rounded-lg bg-[#EBF4FA] border border-[#BAE6FD] flex items-center justify-center text-xl font-bold text-[#0B5D9B] shrink-0">
              🏛️
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-base font-bold text-[#092F4F] m-0">
              Verify your documents
            </h3>
            <p className="text-sm text-[#475569] leading-relaxed">
              Securely share your verified DigiLocker documents with <strong>ABC University</strong> to validate your eligibility for course admission without physically submitting paper marksheet copies.
            </p>

            <div className="bg-[#F8FAFC] border border-[#CBD5E1] rounded-xl p-4 space-y-3">
              <h4 className="text-xs font-extrabold uppercase tracking-wider text-slate-500 m-0">
                Requested Credentials (3)
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="bg-white p-3 rounded-lg border border-slate-200 space-y-1">
                  <span className="text-xs font-bold text-[#092F4F] block">Class 10 Certificate</span>
                  <span className="text-[11px] text-slate-500 block">CBSE • Age & Matriculation</span>
                </div>
                <div className="bg-white p-3 rounded-lg border border-slate-200 space-y-1">
                  <span className="text-xs font-bold text-[#092F4F] block">Class 12 Marksheet</span>
                  <span className="text-[11px] text-slate-500 block">CBSE • Cut-off Aggregate</span>
                </div>
                <div className="bg-white p-3 rounded-lg border border-slate-200 space-y-1">
                  <span className="text-xs font-bold text-[#092F4F] block">Aadhaar eKYC</span>
                  <span className="text-[11px] text-slate-500 block">UIDAI • Identity Match</span>
                </div>
              </div>
            </div>

            <Alert type="info">
              No physical document copies will be permanently stored by ABC University. Only cryptographically signed assertions will be exchanged.
            </Alert>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-slate-200">
            <span className="text-xs text-slate-500">
              Powered by DigiLocker X & UX4G
            </span>
            <div className="flex items-center gap-3">
              <Button
                variant="primary"
                size="lg"
                onClick={() => setCurrentStep("SCOPE")}
              >
                Continue with DigiLocker →
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* =========================================================================
          STEP 2: SCOPE (What Will Be Shared)
          ========================================================================= */}
      {currentStep === "SCOPE" && (
        <Card variant="elevated" className="space-y-6">
          <div className="space-y-1 border-b border-slate-200 pb-4">
            <span className="text-xs font-bold uppercase tracking-wider text-[#0B5D9B]">
              Step 2 of 6
            </span>
            <h2 className="text-2xl font-bold text-[#092F4F] m-0">
              Review What Will Be Shared
            </h2>
            <p className="text-sm text-[#475569]">
              ABC University is requesting the following specific details for the stated purpose:
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border border-slate-200 rounded-lg overflow-hidden">
              <thead className="bg-[#F1F5F9] text-[#092F4F] font-bold uppercase tracking-wider">
                <tr>
                  <th className="p-3 border-b border-slate-200">Document</th>
                  <th className="p-3 border-b border-slate-200">Attributes Shared</th>
                  <th className="p-3 border-b border-slate-200">Specific Purpose</th>
                  <th className="p-3 border-b border-slate-200">Issuing Authority</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 text-slate-700">
                <tr className="bg-white">
                  <td className="p-3 font-bold text-[#092F4F]">Class 10 Certificate</td>
                  <td className="p-3">Roll Number, Passing Year (2024), Date of Birth</td>
                  <td className="p-3">Matriculation & Age Proof</td>
                  <td className="p-3"><Badge variant="info" size="sm">CBSE</Badge></td>
                </tr>
                <tr className="bg-white">
                  <td className="p-3 font-bold text-[#092F4F]">Class 12 Marksheet</td>
                  <td className="p-3">Roll Number, Total Aggregate (88.4%), Status: Pass</td>
                  <td className="p-3">Admission Merit Cut-off</td>
                  <td className="p-3"><Badge variant="info" size="sm">CBSE</Badge></td>
                </tr>
                <tr className="bg-white">
                  <td className="p-3 font-bold text-[#092F4F]">Aadhaar Identity</td>
                  <td className="p-3">Demographic Match Assertion (Name & DOB Match)</td>
                  <td className="p-3">Identity Validation</td>
                  <td className="p-3"><Badge variant="info" size="sm">UIDAI</Badge></td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="bg-[#EBF4FA] p-4 rounded-xl border border-[#BAE6FD] text-xs text-[#0A6990] space-y-1">
            <strong className="block font-bold text-sm">
              🛡️ Zero-Knowledge Proof Protection Active
            </strong>
            <p className="m-0 leading-relaxed">
              Only the mathematical validity of your aggregate score and demographic match will be verified. Unrelated sensitive personal data (like address, religion, or subject breakdown) is not shared.
            </p>
          </div>

          <div className="flex items-center justify-between gap-4 pt-4 border-t border-slate-200">
            <Button variant="secondary" onClick={() => setCurrentStep("INGRESS")}>
              ← Back
            </Button>
            <Button variant="primary" size="lg" onClick={() => setCurrentStep("AUTH")}>
              Proceed to Sign In →
            </Button>
          </div>
        </Card>
      )}

      {/* =========================================================================
          STEP 3: AUTH (Passwordless DigiLocker OTP)
          ========================================================================= */}
      {currentStep === "AUTH" && (
        <Card variant="elevated" className="max-w-md mx-auto space-y-6">
          <div className="text-center space-y-2 border-b border-slate-200 pb-4">
            <div className="w-12 h-12 rounded-full bg-[#EBF4FA] text-[#0B5D9B] font-bold text-xl flex items-center justify-center mx-auto border border-[#BAE6FD]">
              🔒
            </div>
            <h2 className="text-xl font-bold text-[#092F4F] m-0">
              Sign In with DigiLocker
            </h2>
            <p className="text-xs text-slate-500">
              Passwordless authentication via Aadhaar-linked OTP challenge
            </p>
          </div>

          <div className="space-y-4">
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs">
              <span className="text-slate-500 block">Registered Mobile Number:</span>
              <strong className="text-sm text-[#092F4F]">+91 98765 43210</strong>
            </div>

            <OtpInput
              value={otpValue}
              onChange={setOtpValue}
              label="Enter 6-Digit OTP"
              helperText="Auto-filled for demonstration (992144)"
            />

            <Button
              variant="primary"
              size="lg"
              fullWidth
              loading={isAuthenticating}
              onClick={handleStartAuth}
            >
              Verify & Proceed →
            </Button>

            <div className="text-center">
              <button
                type="button"
                className="text-xs font-bold text-[#0B5D9B] hover:underline cursor-pointer"
                onClick={() => setOtpValue("992144")}
              >
                Resend OTP (30s)
              </button>
            </div>
          </div>
        </Card>
      )}

      {/* =========================================================================
          STEP 4: CONSENT (Granular & Purpose-Bound)
          ========================================================================= */}
      {currentStep === "CONSENT" && (
        <Card variant="elevated" className="space-y-6">
          <div className="space-y-1 border-b border-slate-200 pb-4">
            <Badge variant="warning" size="sm">Citizen Consent Required</Badge>
            <h2 className="text-2xl font-bold text-[#092F4F] m-0">
              Authorize Document Sharing
            </h2>
            <p className="text-sm text-[#475569]">
              Grant explicit, revocable permission to share verification proofs with ABC University.
            </p>
          </div>

          <div className="space-y-4">
            {/* Consent Details Box */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-3 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-bold text-[#092F4F]">Requesting Entity:</span>
                <span className="font-semibold text-slate-700">ABC University (Accredited Institution)</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-bold text-[#092F4F]">Purpose of Sharing:</span>
                <span className="font-semibold text-slate-700">Undergraduate Admissions Eligibility</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-bold text-[#092F4F]">Access Duration:</span>
                <span className="font-semibold text-slate-700">7 Days (Expires 29 Aug 2026)</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-bold text-[#092F4F]">Revocation Rights:</span>
                <span className="font-semibold text-emerald-700">✓ Instant 1-Click Revocation in Citizen Vault</span>
              </div>
            </div>

            {/* Zero-Knowledge Toggle */}
            <div className="border border-[#CBD5E1] rounded-xl p-4 flex items-center justify-between gap-4 bg-white">
              <div className="space-y-0.5">
                <span className="text-sm font-bold text-[#092F4F] block">
                  Zero-Knowledge Proof (ZKP) Mode
                </span>
                <span className="text-xs text-slate-500 block">
                  Share only true/false verification assertions instead of raw certificates.
                </span>
              </div>
              <input
                type="checkbox"
                checked={zkpMode}
                onChange={(e) => setZkpMode(e.target.checked)}
                className="w-5 h-5 accent-[#0B5D9B] cursor-pointer"
                aria-label="Toggle Zero-Knowledge Proof Mode"
              />
            </div>

            {/* Explicit Consent Checkbox */}
            <label className="flex items-start gap-3 p-4 rounded-xl bg-[#EBF4FA] border border-[#BAE6FD] cursor-pointer select-none">
              <input
                type="checkbox"
                checked={consentGranted}
                onChange={(e) => setConsentGranted(e.target.checked)}
                className="w-5 h-5 accent-[#0B5D9B] mt-0.5 cursor-pointer"
              />
              <span className="text-xs text-[#0A6990] leading-relaxed">
                <strong>I hereby give informed consent</strong> for DigiIn to fetch my Class 10, Class 12, and Aadhaar identity records from official issuers and share cryptographically signed verification assertions with ABC University.
              </span>
            </label>
          </div>

          <div className="flex items-center justify-between gap-4 pt-4 border-t border-slate-200">
            <Button variant="secondary" onClick={() => setCurrentStep("AUTH")}>
              ← Back
            </Button>
            <Button
              variant="primary"
              size="lg"
              disabled={!consentGranted}
              onClick={() => setCurrentStep("PIPELINE")}
            >
              Continue & Give Consent →
            </Button>
          </div>
        </Card>
      )}

      {/* =========================================================================
          STEP 5: PIPELINE (Transparent Async Step Tracker)
          ========================================================================= */}
      {currentStep === "PIPELINE" && (
        <Card variant="elevated" className="space-y-6">
          <div className="text-center space-y-2 border-b border-slate-200 pb-4">
            <div className="w-10 h-10 rounded-full border-4 border-[#0B5D9B] border-t-transparent animate-spin mx-auto" />
            <h2 className="text-xl font-bold text-[#092F4F] m-0">
              Verifying your documents...
            </h2>
            <p className="text-xs text-slate-500">
              Executing real-time issuer queries and demographic validation
            </p>
          </div>

          <ProgressIndicator steps={progressSteps} />

          <Alert type="info">
            Please do not refresh or close this window while the asymmetric cryptographic proof is being minted.
          </Alert>
        </Card>
      )}

      {/* =========================================================================
          STEP 6: RESULT (3-Second Comprehension Hero Screen)
          ========================================================================= */}
      {currentStep === "RESULT" && (
        <Card variant="bordered" className="space-y-6 border-emerald-600 bg-white">
          {/* Hero Outcome Header */}
          <div className="bg-[#DFF6E8] border border-[#86EFAC] rounded-xl p-6 text-center space-y-2">
            <div className="w-14 h-14 rounded-full bg-[#14743F] text-white text-3xl font-extrabold flex items-center justify-center mx-auto shadow-md">
              ✓
            </div>
            <h2 className="text-2xl md:text-3xl font-extrabold text-[#092F4F] m-0">
              Verification Complete
            </h2>
            <p className="text-sm text-[#14743F] font-bold">
              3 of 3 Documents were successfully verified with official issuing authorities.
            </p>
          </div>

          {/* Verified Credentials Breakdown */}
          <div className="space-y-3">
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-500 m-0">
              Verified Items (3)
            </h3>

            <div className="space-y-2">
              <div className="flex items-center justify-between p-3 rounded-lg border border-slate-200 bg-[#F8FAFC]">
                <div className="flex items-center gap-3">
                  <span className="text-emerald-600 font-bold text-lg">✓</span>
                  <div>
                    <span className="text-xs font-bold text-[#092F4F] block">Class 10 Certificate</span>
                    <span className="text-[11px] text-slate-500">CBSE • Passing Year: 2024 • Verified at Source</span>
                  </div>
                </div>
                <Badge variant="success" size="sm">Source Verified</Badge>
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg border border-slate-200 bg-[#F8FAFC]">
                <div className="flex items-center gap-3">
                  <span className="text-emerald-600 font-bold text-lg">✓</span>
                  <div>
                    <span className="text-xs font-bold text-[#092F4F] block">Class 12 Marksheet</span>
                    <span className="text-[11px] text-slate-500">CBSE • Aggregate: 88.4% • Status: Pass</span>
                  </div>
                </div>
                <Badge variant="success" size="sm">Source Verified</Badge>
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg border border-slate-200 bg-[#F8FAFC]">
                <div className="flex items-center gap-3">
                  <span className="text-emerald-600 font-bold text-lg">✓</span>
                  <div>
                    <span className="text-xs font-bold text-[#092F4F] block">Aadhaar Identity Assertion</span>
                    <span className="text-[11px] text-slate-500">UIDAI • Demographic Match Score: 100%</span>
                  </div>
                </div>
                <Badge variant="success" size="sm">eKYC Matched</Badge>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-slate-200">
            <Button variant="secondary" onClick={() => setCurrentStep("RECEIPT")}>
              View Proof Receipt Details →
            </Button>

            <Button variant="primary" size="lg" onClick={() => setCurrentStep("RECEIPT")}>
              Share Verification with ABC University →
            </Button>
          </div>
        </Card>
      )}

      {/* =========================================================================
          STEP 7: RECEIPT (Cryptographic Verification Receipt)
          ========================================================================= */}
      {currentStep === "RECEIPT" && (
        <Card variant="elevated" className="space-y-6">
          <div className="flex items-start justify-between gap-4 border-b border-slate-200 pb-4">
            <div>
              <Badge variant="success" size="sm">Official Proof Receipt</Badge>
              <h2 className="text-2xl font-bold text-[#092F4F] mt-1 mb-0">
                Cryptographic Verification Reference
              </h2>
              <p className="text-xs text-slate-500 mt-1 mb-0">
                This receipt allows ABC University to verify your credentials offline without storing raw documents.
              </p>
            </div>
            <div className="text-right">
              <span className="text-[10px] uppercase font-bold text-slate-400 block">RFC 7515 / 7519</span>
              <span className="text-xs font-mono font-bold text-[#0B5D9B]">Ed25519 Signed</span>
            </div>
          </div>

          {/* Receipt Data Table */}
          <div className="bg-[#F8FAFC] border border-[#CBD5E1] rounded-xl p-5 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div>
                <span className="text-slate-500 block">Verification ID (Token):</span>
                <div className="flex items-center gap-2 mt-1">
                  <code className="text-sm font-bold text-[#092F4F] bg-white px-2 py-1 rounded border border-slate-300">
                    DLV-8F72-A92C
                  </code>
                  <button
                    type="button"
                    onClick={handleCopyReceipt}
                    className="text-xs font-bold text-[#0B5D9B] hover:underline cursor-pointer"
                  >
                    {receiptCopied ? "✓ Copied" : "Copy"}
                  </button>
                </div>
              </div>

              <div>
                <span className="text-slate-500 block">Status:</span>
                <span className="text-sm font-bold text-emerald-700 mt-1 inline-flex items-center gap-1">
                  ✓ Verified at Source (Level 4)
                </span>
              </div>

              <div>
                <span className="text-slate-500 block">Verified For:</span>
                <strong className="text-sm text-[#092F4F]">ABC University Admissions</strong>
              </div>

              <div>
                <span className="text-slate-500 block">Timestamp:</span>
                <strong className="text-sm text-[#092F4F]">23 Aug 2026, 10:30 IST</strong>
              </div>
            </div>

            {/* JWS Claims Payload */}
            <div className="bg-[#092F4F] text-slate-200 p-4 rounded-lg font-mono text-xs space-y-1 overflow-x-auto">
              <span className="text-cyan-400 font-bold block text-[11px]">
                {"// Cryptographic Proof Payload Claims"}
              </span>
              <pre className="m-0 text-[11px] leading-relaxed text-slate-300">
{JSON.stringify(
  {
    iss: "https://digiin.gov.in/issuer/cbse",
    sub: "din:account:992144",
    aud: "https://abc.edu.in",
    exp: 1787498400,
    claims: {
      class10_pass: true,
      class12_aggregate_percentage: 88.4,
      identity_match_score: 1.0,
    },
    jws_sig: "3b08e5c8e268a287a2a7b8e1f0e2d3c4...",
  },
  null,
  2
)}
              </pre>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-slate-200">
            <Button
              variant="secondary"
              onClick={() => setCurrentStep("INGRESS")}
            >
              Start Another Verification
            </Button>

            <div className="flex items-center gap-3">
              <Button
                variant="primary"
                onClick={() => alert("Verification Proof shared with ABC University admissions portal via webhook callback.")}
              >
                Send Proof to ABC University ✓
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* =========================================================================
          STEP 8: RECOVERY (Explainable Failure Path)
          ========================================================================= */}
      {currentStep === "RECOVERY" && (
        <Card variant="elevated" className="space-y-6 border-amber-400 bg-white">
          <div className="space-y-1 border-b border-slate-200 pb-4">
            <Badge variant="danger" size="sm">Verification Attention Needed</Badge>
            <h2 className="text-2xl font-bold text-[#092F4F] mt-1 mb-0">
              Document Details Do Not Match
            </h2>
            <p className="text-sm text-[#475569]">
              The candidate information on your Aadhaar record differs from the CBSE Class 12 registry.
            </p>
          </div>

          {/* Discrepancy Comparison Box */}
          <div className="bg-[#FFF0CC] border border-[#FDE68A] rounded-xl p-4 space-y-3">
            <h4 className="text-xs font-extrabold uppercase tracking-wider text-[#744B00] m-0">
              Identified Field Discrepancy
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div className="bg-white p-3 rounded-lg border border-amber-200">
                <span className="text-slate-500 block">Name on Aadhaar (UIDAI):</span>
                <strong className="text-sm text-[#092F4F]">Rahul S. Sharma</strong>
              </div>
              <div className="bg-white p-3 rounded-lg border border-amber-200">
                <span className="text-slate-500 block">Name on Class 12 Certificate (CBSE):</span>
                <strong className="text-sm text-[#092F4F]">Rahul Sharma</strong>
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <h4 className="text-xs font-extrabold uppercase tracking-wider text-slate-500 m-0">
              Recommended Recovery Action
            </h4>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              You can submit this discrepancy to the <strong>Government Officer Adjudication Queue</strong>. An authorized CBSE education officer will review your supporting birth certificate and issue a Level 4 verified credential.
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-slate-200">
            <Button
              variant="secondary"
              onClick={() => {
                setFailureScenario("none");
                setCurrentStep("INGRESS");
              }}
            >
              ← Retry with Exact Details
            </Button>

            <Button
              variant="primary"
              onClick={() => {
                alert("Case submitted to Government Review Queue! Officer case reference #GOV-REV-2026.");
                setFailureScenario("none");
                setCurrentStep("RESULT");
              }}
            >
              Submit for Officer Review →
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
};
