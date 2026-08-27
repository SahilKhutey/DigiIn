import React, { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { Button, Card, Badge } from "../../components/ui";

interface Institution {
  code: string;
  name: string;
  category: string;
  description: string;
  allowedScopes: string[];
  totalApps: number;
  awaitingVerify: number;
  verified: number;
  rejected: number;
}

const SANDBOX_INSTITUTIONS: Institution[] = [
  {
    code: "EDU-DEMO-001",
    name: "Education Scholarship Service",
    category: "Higher Education",
    description: "Simulated national scholarship portal verifying academic merit, household income, and state domicile.",
    allowedScopes: ["education_qualification", "income_status", "domicile_status"],
    totalApps: 42,
    awaitingVerify: 8,
    verified: 29,
    rejected: 5,
  },
  {
    code: "REV-DEMO-002",
    name: "Revenue Certificate Service",
    category: "Revenue & Social Welfare",
    description: "Simulated state revenue portal processing income attestation, community certificates, and domicile.",
    allowedScopes: ["identity_assertion", "income_status", "domicile_status"],
    totalApps: 38,
    awaitingVerify: 4,
    verified: 31,
    rejected: 3,
  },
  {
    code: "ADM-DEMO-003",
    name: "Citizen Services Portal",
    category: "Local Administration",
    description: "Simulated municipal administration portal verifying resident identity and address proof.",
    allowedScopes: ["identity_assertion", "domicile_status"],
    totalApps: 19,
    awaitingVerify: 2,
    verified: 16,
    rejected: 1,
  },
];

interface Props {
  onSwitchToCitizenApp?: () => void;
}

export const MockInstitutionPortalView: React.FC<Props> = ({ onSwitchToCitizenApp }) => {
  const { user } = useAuth();
  const defaultAccountId = user?.digiinId || "DI-7K4M-9Q2X-8P6R";

  const [selectedInstitutionCode, setSelectedInstitutionCode] = useState<string>("EDU-DEMO-001");
  const [targetAccountId, setTargetAccountId] = useState<string>(defaultAccountId);
  const [purpose, setPurpose] = useState<string>("Scholarship Eligibility & Academic Merit");
  const [selectedScopes, setSelectedScopes] = useState<string[]>([
    "education_qualification",
    "income_status",
    "domicile_status",
  ]);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeRequest, setActiveRequest] = useState<any | null>(null);
  const [verifiedResult, setVerifiedResult] = useState<any | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const currentInstitution =
    SANDBOX_INSTITUTIONS.find((inst) => inst.code === selectedInstitutionCode) ||
    SANDBOX_INSTITUTIONS[0];

  const handleScopeToggle = (scope: string) => {
    setSelectedScopes((prev) =>
      prev.includes(scope) ? prev.filter((s) => s !== scope) : [...prev, scope]
    );
  };

  const handleInstitutionChange = (code: string) => {
    setSelectedInstitutionCode(code);
    const inst = SANDBOX_INSTITUTIONS.find((i) => i.code === code);
    if (inst) {
      setSelectedScopes([...inst.allowedScopes]);
      if (code === "EDU-DEMO-001") setPurpose("Scholarship Eligibility & Academic Merit");
      else if (code === "REV-DEMO-002") setPurpose("EWS Scheme & Domicile Attestation");
      else if (code === "ADM-DEMO-003") setPurpose("Municipal Property Record Title Verification");
    }
    setActiveRequest(null);
    setVerifiedResult(null);
  };

  const handleSendVerificationRequest = () => {
    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      const reqRef = `VR-${Math.floor(100000 + Math.random() * 900000)}`;
      setActiveRequest({
        requestReference: reqRef,
        institutionCode: currentInstitution.code,
        institutionName: currentInstitution.name,
        accountId: targetAccountId,
        purpose,
        scopes: selectedScopes,
        status: "PENDING_CITIZEN_CONSENT",
        timestamp: new Date().toLocaleTimeString(),
        expiresIn: "14:59",
      });
      setToastMessage(`✓ Verification request ${reqRef} dispatched to DigiIn Gateway.`);
      setTimeout(() => setToastMessage(null), 4000);
    }, 600);
  };

  const handleSimulateCitizenApproval = () => {
    if (!activeRequest) return;
    setVerifiedResult({
      status: "VERIFIED",
      requestReference: activeRequest.requestReference,
      assertionId: `VA-${Math.random().toString(16).slice(2, 10).toUpperCase()}`,
      accountId: targetAccountId,
      purpose,
      verifiedScopes: activeRequest.scopes,
      rawFilesTransferredBytes: 0,
      claims: {
        education_qualification: "CBSE Class XII 94.2% (Passed)",
        income_status: "Annual Household Income < 2.5L (Eligible)",
        domicile_status: "Verified Permanent Resident (NCT Delhi)",
        identity_assertion: "Sovereign Identity Matched (UIDAI Level 4)",
      },
      signatureValid: true,
      issuedAt: new Date().toISOString(),
      expiresAt: new Date(Date.now() + 600000).toISOString(),
    });
    setActiveRequest(null);
    setToastMessage("✓ Citizen approved request! Signed Ed25519 assertion received.");
    setTimeout(() => setToastMessage(null), 4000);
  };

  const handleResetDemo = () => {
    setActiveRequest(null);
    setVerifiedResult(null);
    setTargetAccountId("DI-7K4M-9Q2X-8P6R");
    setToastMessage("🔄 Sandbox demo state reset to baseline.");
    setTimeout(() => setToastMessage(null), 3000);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 py-4">
      {/* 1. Transparent Sandbox Disclaimer Banner */}
      <div className="bg-amber-500/10 border-2 border-amber-500/30 rounded-2xl p-4 sm:p-5 text-amber-950 shadow-xs space-y-1">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="text-xl">🧪</span>
            <span className="font-extrabold text-sm uppercase tracking-wide text-amber-900">
              HACKATHON SANDBOX: Simulated Institution Integration
            </span>
          </div>
          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-900 border border-amber-300">
            DigiIn Sandbox Environment
          </span>
        </div>
        <p className="text-xs text-amber-900/80 m-0">
          This portal simulates relying government departments (Education, Revenue, Municipal Administration) connecting to the DigiIn Verification Gateway using the citizen&apos;s DigiIn Account ID. It demonstrates the live protocol without claiming official government affiliation.
        </p>
      </div>

      {/* 2. Top Header & Institution Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white border border-slate-200 rounded-2xl p-5 shadow-xs">
        <div className="space-y-1">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wide">
            Select Relying Sandbox Service:
          </div>
          <select
            value={selectedInstitutionCode}
            onChange={(e) => handleInstitutionChange(e.target.value)}
            className="text-base sm:text-lg font-extrabold text-[#092F4F] bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 cursor-pointer focus:outline-none focus:ring-2 focus:ring-[#0B5D9B]"
          >
            {SANDBOX_INSTITUTIONS.map((inst) => (
              <option key={inst.code} value={inst.code}>
                🏛️ {inst.name} ({inst.code})
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleResetDemo}
            className="text-xs font-bold border-slate-300 hover:bg-slate-50"
          >
            🔄 Reset Demo
          </Button>

          {onSwitchToCitizenApp && (
            <Button
              variant="secondary"
              size="sm"
              onClick={onSwitchToCitizenApp}
              className="text-xs font-bold bg-[#092F4F] text-white hover:bg-[#071F34]"
            >
              👤 Switch to Citizen View
            </Button>
          )}
        </div>
      </div>

      {/* Global Toast Alert */}
      {toastMessage && (
        <div
          className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-300 text-xs font-bold text-emerald-900 flex items-center justify-between shadow-xs animate-fadeIn"
          role="status"
        >
          <span>{toastMessage}</span>
          <button
            type="button"
            onClick={() => setToastMessage(null)}
            className="text-emerald-700 hover:text-emerald-950 font-bold ml-2"
          >
            ✕
          </button>
        </div>
      )}

      {/* 3. Department Statistics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-1">
          <span className="text-[11px] font-semibold text-slate-500">Total Applications</span>
          <div className="text-xl sm:text-2xl font-extrabold text-slate-900">
            {currentInstitution.totalApps}
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-1">
          <span className="text-[11px] font-semibold text-slate-500">Awaiting Verify</span>
          <div className="text-xl sm:text-2xl font-extrabold text-amber-700">
            {currentInstitution.awaitingVerify + (activeRequest ? 1 : 0)}
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-1">
          <span className="text-[11px] font-semibold text-slate-500">Verified via DigiIn</span>
          <div className="text-xl sm:text-2xl font-extrabold text-emerald-700">
            {currentInstitution.verified + (verifiedResult ? 1 : 0)}
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-1">
          <span className="text-[11px] font-semibold text-slate-500">Rejected / Denied</span>
          <div className="text-xl sm:text-2xl font-extrabold text-red-600">
            {currentInstitution.rejected}
          </div>
        </div>
      </div>

      {/* 4. Main Two-Column Workflow Area */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Verification Request Dispatcher */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-5">
          <div className="border-b border-slate-100 pb-3">
            <h2 className="text-base font-bold text-[#092F4F] m-0 flex items-center gap-2">
              <span>📤</span> Initiate DigiIn Verification Request
            </h2>
            <p className="text-xs text-slate-500 mt-1 m-0">
              Department enters citizen&apos;s DigiIn Account ID and requests exact required claims.
            </p>
          </div>

          <div className="space-y-4 text-xs">
            {/* Target Account ID */}
            <div className="space-y-1.5">
              <label className="font-bold text-slate-800">Citizen DigiIn Account ID:</label>
              <input
                type="text"
                value={targetAccountId}
                onChange={(e) => setTargetAccountId(e.target.value)}
                placeholder="e.g. DI-7K4M-9Q2X-8P6R"
                className="w-full font-mono font-bold text-sm bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-slate-900 focus:outline-none focus:ring-2 focus:ring-[#0B5D9B]"
              />
            </div>

            {/* Purpose */}
            <div className="space-y-1.5">
              <label className="font-bold text-slate-800">Transaction Purpose:</label>
              <input
                type="text"
                value={purpose}
                onChange={(e) => setPurpose(e.target.value)}
                className="w-full text-xs font-semibold bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-slate-900 focus:outline-none focus:ring-2 focus:ring-[#0B5D9B]"
              />
            </div>

            {/* Accredited Scopes Selection */}
            <div className="space-y-2">
              <label className="font-bold text-slate-800">
                Required Verification Scopes (Accredited for {currentInstitution.code}):
              </label>
              <div className="space-y-2">
                {currentInstitution.allowedScopes.map((scope) => {
                  const isChecked = selectedScopes.includes(scope);
                  return (
                    <label
                      key={scope}
                      className={`flex items-center gap-2.5 p-3 rounded-xl border transition-all cursor-pointer ${
                        isChecked
                          ? "bg-blue-50/60 border-[#0B5D9B] text-slate-900"
                          : "bg-slate-50 border-slate-200 text-slate-600"
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => handleScopeToggle(scope)}
                        className="rounded text-[#0B5D9B] focus:ring-[#0B5D9B]"
                      />
                      <span className="font-bold">{scope}</span>
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Request TTL */}
            <div className="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-xl">
              <span className="text-slate-600">Verification Request Validity:</span>
              <span className="font-bold font-mono text-slate-900">15 Minutes (900s TTL)</span>
            </div>

            {/* Dispatch Button */}
            <Button
              variant="primary"
              onClick={handleSendVerificationRequest}
              disabled={isSubmitting || selectedScopes.length === 0}
              className="w-full font-bold bg-[#092F4F] hover:bg-[#071F34] py-2.5 text-xs shadow-xs"
            >
              {isSubmitting ? "Dispatching to Gateway..." : "🚀 Dispatch Verification Request to Citizen"}
            </Button>
          </div>
        </div>

        {/* Right Column: Live Status & Received Assertion */}
        <div className="space-y-6">
          {/* Active Pending Request Card */}
          {activeRequest && (
            <div className="bg-amber-50 border-2 border-amber-300 rounded-2xl p-5 shadow-xs space-y-4 animate-fadeIn">
              <div className="flex items-center justify-between border-b border-amber-200 pb-2.5">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-500 animate-ping" />
                  <strong className="text-xs uppercase tracking-wide text-amber-900">
                    Awaiting Citizen Consent ({activeRequest.requestReference})
                  </strong>
                </div>
                <span className="font-mono text-xs font-bold text-amber-800">
                  TTL: {activeRequest.expiresIn}
                </span>
              </div>

              <div className="text-xs text-amber-950 space-y-1">
                <div>Target ID: <strong className="font-mono">{activeRequest.accountId}</strong></div>
                <div>Purpose: <strong>{activeRequest.purpose}</strong></div>
                <div className="flex flex-wrap gap-1 pt-1">
                  {activeRequest.scopes.map((s: string) => (
                    <span
                      key={s}
                      className="px-2 py-0.5 bg-white text-slate-800 rounded border border-amber-300 text-[10px] font-bold"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              <div className="p-3 bg-white border border-amber-300 rounded-xl text-xs space-y-2">
                <span className="text-slate-600 block">
                  Simulate live citizen action on their mobile device / DigiIn app:
                </span>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleSimulateCitizenApproval}
                  className="w-full text-xs font-bold bg-emerald-700 hover:bg-emerald-800"
                >
                  ✓ Simulate Citizen &quot;Approve&quot; in DigiIn App
                </Button>
              </div>
            </div>
          )}

          {/* Received Verified Assertion Card */}
          {verifiedResult ? (
            <div className="bg-white border-2 border-emerald-400 rounded-2xl p-6 shadow-xs space-y-4 animate-fadeIn">
              <div className="flex items-center justify-between border-b border-emerald-100 pb-3">
                <div className="flex items-center gap-2">
                  <span className="text-lg">🛡️</span>
                  <strong className="text-sm font-bold text-[#092F4F]">
                    DigiIn Verification Assertion Verified
                  </strong>
                </div>
                <span className="text-xs font-extrabold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-900 border border-emerald-300">
                  ✓ VERIFIED
                </span>
              </div>

              <div className="space-y-3 text-xs">
                <div className="grid grid-cols-2 gap-2 text-slate-600">
                  <div>Assertion ID: <strong className="font-mono text-slate-900">{verifiedResult.assertionId}</strong></div>
                  <div>Account ID: <strong className="font-mono text-slate-900">{verifiedResult.accountId}</strong></div>
                  <div>Algorithm: <strong className="text-slate-900">Ed25519 (RFC 8032)</strong></div>
                  <div>Raw File Bytes: <strong className="text-emerald-800">0 Bytes (Zero Exposure)</strong></div>
                </div>

                <div className="space-y-2 pt-2 border-t border-slate-100">
                  <span className="font-bold text-slate-800 block">Verified Claims Payload:</span>
                  <div className="space-y-1.5 bg-slate-50 border border-slate-200 rounded-xl p-3 text-slate-800">
                    {verifiedResult.verifiedScopes.map((scope: string) => (
                      <div key={scope} className="flex items-center justify-between text-[11px]">
                        <span className="font-semibold">{scope}:</span>
                        <span className="font-bold text-emerald-800">
                          ✓ {verifiedResult.claims[scope] || "VERIFIED"}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl text-[11px] text-blue-900">
                  <strong>Service Invariant Proven:</strong> The department received cryptographically sealed eligibility assertions directly through the citizen&apos;s DigiIn Account ID without requiring any uploaded PDF documents.
                </div>
              </div>
            </div>
          ) : (
            !activeRequest && (
              <div className="bg-slate-50 border-2 border-dashed border-slate-200 rounded-2xl p-8 text-center text-slate-400 space-y-2">
                <span className="text-3xl block">📋</span>
                <strong className="text-sm font-bold text-slate-600 block">
                  No Active Verification Transaction
                </strong>
                <p className="text-xs text-slate-500 max-w-sm mx-auto m-0">
                  Select a sandbox institution on the left, enter a DigiIn Account ID, and dispatch a verification request to see the live cryptographic response.
                </p>
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
};
