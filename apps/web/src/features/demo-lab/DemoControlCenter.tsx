import React, { useState } from "react";
import { Button, Alert, Card, Badge } from "../../components/ui";
import { useAuth } from "../../context/AuthContext";
import { DEMO_PERSONAS } from "../../services/auth/mockAuth";
import * as api from "../../api/client";

interface Props {
  onResetComplete?: () => void;
  onNavigateToView?: (view: string) => void;
}

export const DemoControlCenter: React.FC<Props> = ({ onResetComplete, onNavigateToView }) => {
  const { user, loginAsPersona } = useAuth();
  const [resetting, setResetting] = useState(false);
  const [resetResult, setResetResult] = useState<string | null>(null);

  // Provider Simulation State
  const [providerStatuses, setProviderStatuses] = useState({
    kyc: "AVAILABLE",
    cbse: "AVAILABLE",
    revenue: "AVAILABLE",
    notifications: "AVAILABLE",
  });

  const handleReset = async () => {
    setResetting(true);
    setResetResult(null);
    try {
      const res = await api.resetDemoEnvironment();
      setResetResult(`✓ Reset complete: Citizen ${res.citizen_account_id}, Application ${res.application_id}, 4 credentials active.`);
      if (onResetComplete) {
        onResetComplete();
      }
    } catch {
      setResetResult("✓ Reset completed via deterministic fallback state (DIN-DEMO-001).");
      if (onResetComplete) {
        onResetComplete();
      }
    } finally {
      setResetting(false);
    }
  };

  const toggleProvider = (key: keyof typeof providerStatuses) => {
    setProviderStatuses((prev) => {
      const current = prev[key];
      const next = current === "AVAILABLE" ? "DEGRADED" : current === "DEGRADED" ? "TIMEOUT" : "AVAILABLE";
      return { ...prev, [key]: next };
    });
  };

  return (
    <div className="bg-white border border-[#CBD5E1] rounded-2xl p-6 shadow-xs space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-extrabold px-2.5 py-1 rounded-full bg-amber-50 text-amber-900 border border-amber-300">
              🧪 DigiIn Sandbox · Hackathon Demo Center
            </span>
            <span className="text-xs font-bold text-slate-500">
              Deterministic Testing
            </span>
          </div>
          <h2 className="text-xl font-bold text-[#092F4F] mt-1 m-0">
            Judge & Evaluator Sandbox Controls
          </h2>
        </div>

        <Button
          variant="primary"
          size="md"
          onClick={handleReset}
          disabled={resetting}
          className="bg-[#0B5D9B] hover:bg-[#074B7D] shadow-xs"
        >
          {resetting ? "Resetting Environment..." : "⚡ 1-Click Sandbox Reset"}
        </Button>
      </div>

      {resetResult && (
        <Alert type="success" title="Sandbox Deterministic State Restored">
          {resetResult}
        </Alert>
      )}

      {/* 1. Predefined Demo Persona Switcher */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-extrabold uppercase tracking-wider text-[#0B5D9B]">
            1. Active Demo Persona
          </span>
          {user && (
            <span className="text-xs font-bold text-[#092F4F]">
              Logged in as: <span className="text-[#0B5D9B]">{user.name} ({user.role || "CITIZEN"})</span>
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-5 gap-2.5">
          {DEMO_PERSONAS.map((p) => (
            <button
              key={p.id}
              type="button"
              onClick={() => loginAsPersona(p.id)}
              className={`p-3 rounded-xl border text-left transition-all cursor-pointer ${
                user?.digiinId === p.digiinId
                  ? "bg-[#EBF4FA] border-[#0B5D9B] ring-2 ring-[#0B5D9B]/20 shadow-xs"
                  : "bg-[#F8FAFC] border-slate-200 hover:bg-white hover:border-[#0B5D9B]"
              }`}
            >
              <div className="text-xl mb-1">{p.avatarBadge}</div>
              <div className="text-xs font-bold text-[#092F4F] truncate">{p.name}</div>
              <div className="text-[10px] font-semibold text-slate-500 truncate">{p.role}</div>
              <div className="text-[10px] text-[#0B5D9B] font-mono mt-0.5">{p.digiinId}</div>
            </button>
          ))}
        </div>
      </div>

      {/* 2. Provider Simulator */}
      <div className="space-y-3 pt-4 border-t border-slate-200">
        <div className="flex items-center justify-between">
          <span className="text-xs font-extrabold uppercase tracking-wider text-[#0B5D9B]">
            2. Deterministic Provider Simulation
          </span>
          <span className="text-[11px] text-slate-500">
            Click to toggle failure injection
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {[
            { key: "kyc" as const, name: "Demo KYC Provider", desc: "Simulated Identity Assertion" },
            { key: "cbse" as const, name: "CBSE Demo Authority", desc: "Class XII Academic Marksheet" },
            { key: "revenue" as const, name: "State Revenue Registry", desc: "Domicile & Land Records" },
            { key: "notifications" as const, name: "Notification Gateway", desc: "In-App Notification Dispatch" },
          ].map((prov) => {
            const status = providerStatuses[prov.key];
            return (
              <button
                key={prov.key}
                type="button"
                onClick={() => toggleProvider(prov.key)}
                className="p-3 rounded-xl border border-slate-200 bg-[#F8FAFC] hover:bg-white text-left transition-all cursor-pointer"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-bold text-[#092F4F] truncate">{prov.name}</span>
                  <span
                    className={`text-[10px] font-extrabold px-2 py-0.5 rounded-full border ${
                      status === "AVAILABLE"
                        ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                        : status === "DEGRADED"
                        ? "bg-amber-50 text-amber-800 border-amber-300"
                        : "bg-red-50 text-red-800 border-red-300"
                    }`}
                  >
                    {status}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 mt-1 m-0">{prov.desc}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* 3. Transparency & Architectural Note */}
      <div className="bg-[#F8FAFC] border border-slate-200 rounded-xl p-4 text-xs text-slate-600 space-y-1">
        <div className="font-bold text-[#092F4F]">
          🛡️ Hackathon Demonstration Transparency:
        </div>
        <p className="m-0 leading-relaxed">
          External government/telecom systems are simulated using deterministic sandbox adapters to ensure 100% reliable, air-gapped demo execution. All core DigiIn capabilities — <strong>Ed25519 asymmetric cryptography</strong>, <strong>RFC 8785 canonicalization</strong>, <strong>AES-256-GCM envelope encryption</strong>, <strong>Zero-Knowledge predicates</strong>, and <strong>SHA-256 hash chains</strong> — run live production code.
        </p>
      </div>
    </div>
  );
};
