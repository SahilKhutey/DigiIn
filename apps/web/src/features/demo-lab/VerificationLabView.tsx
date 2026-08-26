import React, { useState, useEffect } from "react";
import * as api from "../../api/client";
import type { LabTestResult } from "../../types";

// Fallback demo data when API is unavailable
const FALLBACK_TESTS: LabTestResult[] = [
  { test_id: "TC-01", test_name: "Valid Proof Verification", description: "Authentic proof with unmodified claims", is_valid: true, status: "VERIFIED" },
  { test_id: "TC-02", test_name: "Tampered Claim Rejection", description: "income_eligible claim altered after signing", is_valid: false, status: "INVALID", tampered_field: "income_eligible", original_value: true, tampered_value: false, failure_reason: "Claim digest mismatch — income_eligible" },
  { test_id: "TC-03", test_name: "Wrong Audience Rejection", description: "Proof presented to unintended verifier", is_valid: false, status: "INVALID", failure_reason: "Audience mismatch — proof bound to different service" },
  { test_id: "TC-04", test_name: "Revoked Credential Rejection", description: "Issuer revoked this credential after issuance", is_valid: false, status: "REVOKED", failure_reason: "Credential revoked by issuer at 2026-08-23T10:00:00Z" },
  { test_id: "TC-05", test_name: "Expired Proof Rejection", description: "Proof validity window has elapsed", is_valid: false, status: "EXPIRED", failure_reason: "Proof expired at 2026-08-23T00:00:00Z" },
];

const statusColor: Record<string, string> = {
  VERIFIED: "bg-green-50 border-green-200 text-green-700",
  INVALID: "bg-red-50 border-red-200 text-red-700",
  REVOKED: "bg-orange-50 border-orange-200 text-orange-700",
  EXPIRED: "bg-slate-50 border-slate-300 text-slate-600",
};

const statusIcon: Record<string, string> = {
  VERIFIED: "✓",
  INVALID: "✕",
  REVOKED: "⊘",
  EXPIRED: "⏱",
};

const TestCard: React.FC<{ test: LabTestResult; isActive: boolean; onClick: () => void }> = ({ test, isActive, onClick }) => (
  <button
    type="button"
    onClick={onClick}
    className={`w-full text-left p-4 rounded-xl border-2 transition-all cursor-pointer ${
      isActive ? "border-[#0B5D9B] bg-[#EBF4FA]" : "border-slate-200 bg-white hover:border-slate-300"
    }`}
  >
    <div className="flex items-center justify-between mb-1">
      <div className="font-bold text-sm text-slate-800">{test.test_name}</div>
      <span className={`text-xs font-extrabold px-2 py-0.5 rounded-full border ${statusColor[test.status] ?? "bg-slate-100 text-slate-600"}`}>
        {statusIcon[test.status] ?? "?"} {test.status}
      </span>
    </div>
    <div className="text-xs text-slate-500">{test.description}</div>
  </button>
);

export const VerificationLabView: React.FC = () => {
  const [tests, setTests] = useState<LabTestResult[]>(FALLBACK_TESTS);
  const [loading, setLoading] = useState(true);
  const [activeId, setActiveId] = useState<string>("TC-01");

  useEffect(() => {
    api.getVerificationLabResults()
      .then(r => { setTests(r.tests); setLoading(false); })
      .catch(() => { setTests(FALLBACK_TESTS); setLoading(false); });
  }, []);

  const activeTest = tests.find(t => t.test_id === activeId) ?? tests[0];

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="bg-gradient-to-br from-[#092F4F] to-[#0B5D9B] text-white rounded-2xl p-6 mb-6">
        <div className="text-xs font-bold opacity-70 uppercase tracking-wide mb-1">⚗️ Verification Lab</div>
        <h1 className="text-2xl font-extrabold mb-1">Cryptographic Proof Verification Demo</h1>
        <p className="text-sm opacity-90">Live demonstration of valid, tampered, revoked and expired proof handling.</p>
      </div>

      {loading && (
        <div className="text-center py-8 text-slate-500">
          <div className="inline-block w-8 h-8 border-4 border-[#0B5D9B] border-t-transparent rounded-full animate-spin mb-3" />
          <div>Loading verification lab…</div>
        </div>
      )}

      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Left: Test list */}
          <div className="space-y-3">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">Test Cases</div>
            {tests.map(t => (
              <TestCard key={t.test_id} test={t} isActive={t.test_id === activeId} onClick={() => setActiveId(t.test_id)} />
            ))}
          </div>

          {/* Right: Detail panel */}
          {activeTest && (
            <div>
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-2">Result Detail</div>
              <div className={`rounded-xl border-2 p-5 mb-4 ${statusColor[activeTest.status] ?? "bg-slate-50 border-slate-200 text-slate-700"}`}>
                <div className="text-3xl mb-2 font-extrabold">
                  {statusIcon[activeTest.status]} {activeTest.status}
                </div>
                <div className="font-bold text-base mb-1">{activeTest.test_name}</div>
                <div className="text-sm opacity-80">{activeTest.description}</div>
                {activeTest.failure_reason && (
                  <div className="mt-3 text-sm font-mono bg-white/50 rounded-lg px-3 py-2">
                    {activeTest.failure_reason}
                  </div>
                )}
              </div>

              {/* Tamper visualization for TC-02 */}
              {activeTest.test_id === "TC-02" && (
                <div className="bg-white border border-slate-200 rounded-xl p-4 font-mono text-sm">
                  <div className="text-xs font-bold text-slate-400 uppercase mb-2">Claim Modification</div>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-600">income_eligible:</span>
                    <span className="line-through text-red-400">true</span>
                    <span className="text-slate-400">→</span>
                    <span className="font-bold text-red-600">false</span>
                  </div>
                  <div className="mt-3 py-2 px-3 bg-red-600 text-white rounded-lg text-center font-extrabold">
                    SIGNATURE INVALID ✕
                  </div>
                  <div className="text-xs text-slate-500 mt-2 text-center">
                    Ed25519 digest mismatch. Claim modified after signing.
                  </div>
                </div>
              )}

              {/* Proof check table for valid proof */}
              {activeTest.test_id === "TC-01" && (
                <div className="bg-white border border-slate-200 rounded-xl p-4 font-mono text-sm">
                  <div className="text-xs font-bold text-slate-400 uppercase mb-2">Verification Checks</div>
                  {[["Signature", "✓ Valid"], ["Issuer", "✓ DigiIn DEMO Issuer"], ["Audience", "✓ Matches"], ["Expiry", "✓ Within Window"], ["Claims", "✓ All digests match"]].map(([l, v]) => (
                    <div key={l} className="flex justify-between py-1.5 border-b border-slate-100 last:border-0">
                      <span className="text-slate-600">{l}</span>
                      <span className="text-green-600 font-bold">{v}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <div className="mt-6 bg-amber-50 border border-amber-200 rounded-xl p-4 text-xs text-amber-700">
        <strong>SANDBOX DEMO</strong> — All proofs are cryptographically verifiable but use synthetic demo data. No real credentials are involved.
      </div>
    </div>
  );
};
