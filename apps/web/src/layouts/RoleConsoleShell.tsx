import React from "react";
import { AppView } from "./GovHeader";
import { useLanguage } from "../context/LanguageContext";

interface RoleConsoleShellProps {
  role: "ISSUER" | "VERIFIER" | "ADMIN";
  currentView: AppView;
  onViewChange: (view: AppView) => void;
  children: React.ReactNode;
}

export const RoleConsoleShell: React.FC<RoleConsoleShellProps> = ({
  role,
  currentView,
  onViewChange,
  children,
}) => {
  const { locale, setLocale } = useLanguage();

  const roleConfig = {
    ISSUER: {
      badge: "Government Issuer Console",
      subtext: "Authoritative Registry Verification & Discrepancy Queue (CBSE / UIDAI / MoRTH)",
      icon: "🏛️",
      color: "from-[#092F4F] to-[#1A3B5C]",
      border: "border-sky-700",
    },
    VERIFIER: {
      badge: "Verifier / Requester Portal",
      subtext: "Scoped Verification Request Dispatch & Instant Verifiable Proof Intake",
      icon: "🔍",
      color: "from-[#0F172A] to-[#1E293B]",
      border: "border-indigo-700",
    },
    ADMIN: {
      badge: "Platform Administration & System Governance",
      subtext: "HSM Trust Anchors, Registered Issuer Topology, Live Verification Lab",
      icon: "⚙️",
      color: "from-[#1E1B4B] to-[#312E81]",
      border: "border-purple-700",
    },
  }[role];

  return (
    <div className="min-h-screen flex flex-col bg-[#F3F7FA] text-[#092F4F] font-sans antialiased">
      {/* 1. Official Government Top Strip with Role Badge */}
      <div className={`bg-gradient-to-r ${roleConfig.color} text-white text-xs py-2 px-4 md:px-8 flex items-center justify-between border-b ${roleConfig.border}`}>
        <div className="flex items-center gap-3">
          <span className="text-base">{roleConfig.icon}</span>
          <div>
            <div className="font-extrabold uppercase tracking-wide text-xs">
              {roleConfig.badge}
            </div>
            <p className="text-[11px] text-slate-300 m-0 hidden sm:block">
              {roleConfig.subtext}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Role Surface Switcher */}
          <div className="flex items-center gap-1 bg-black/30 px-2.5 py-1 rounded-lg border border-white/20 text-xs">
            <span className="text-slate-300 hidden sm:inline">Surface:</span>
            <select
              value={role}
              onChange={(e) => {
                const val = e.target.value;
                if (val === "PUBLIC") onViewChange("LANDING");
                else if (val === "CITIZEN") onViewChange("DASHBOARD");
                else if (val === "ISSUER") onViewChange("ISSUER_CONSOLE");
                else if (val === "VERIFIER") onViewChange("VERIFIER_CONSOLE");
                else if (val === "ADMIN") onViewChange("ADMIN_CONSOLE");
              }}
              className="bg-transparent text-white font-bold border-none cursor-pointer focus:outline-none text-xs"
            >
              <option value="ISSUER" className="bg-slate-900 text-white">🏛️ Issuer Console</option>
              <option value="VERIFIER" className="bg-slate-900 text-white">🔍 Verifier Portal</option>
              <option value="ADMIN" className="bg-slate-900 text-white">⚙️ Admin / Operations</option>
              <option value="CITIZEN" className="bg-slate-900 text-white">👤 Citizen App</option>
              <option value="PUBLIC" className="bg-slate-900 text-white">🌐 Public Portal</option>
            </select>
          </div>

          <button
            type="button"
            onClick={() => onViewChange("DASHBOARD")}
            className="px-3 py-1 rounded-lg text-xs font-bold bg-white text-[#092F4F] hover:bg-slate-100 transition-all cursor-pointer shrink-0"
          >
            ← Citizen Portal
          </button>
        </div>
      </div>

      {/* 2. Top System Health Sub-Bar */}
      <div className="bg-white border-b border-[#CBD5E1] py-2 px-4 md:px-8 text-xs flex items-center justify-between gap-4">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-1.5 font-bold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-300">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>HSM Trust Anchor: ACTIVE</span>
          </div>

          <div className="text-slate-600 hidden md:inline">
            <span className="font-semibold">Issuers Connected:</span> 42 Authorities (CBSE, UIDAI, MoRTH)
          </div>

          <div className="text-slate-600 hidden lg:inline">
            <span className="font-semibold">Throughput:</span> 450 Verifications/sec
          </div>
        </div>

        <div className="flex items-center gap-2">
          {role === "ADMIN" && (
            <button
              type="button"
              onClick={() => onViewChange("DEMO_LAB")}
              className={`px-2.5 py-1 rounded-md text-xs font-bold transition-colors cursor-pointer ${
                currentView === "DEMO_LAB"
                  ? "bg-purple-700 text-white"
                  : "bg-purple-50 text-purple-800 border border-purple-200 hover:bg-purple-100"
              }`}
            >
              ⚗️ Open Verification Lab
            </button>
          )}

          <button
            type="button"
            onClick={() => setLocale(locale === "en" ? "hi" : "en")}
            className="px-2 py-0.5 rounded text-xs font-bold text-slate-600 hover:text-[#092F4F] border border-slate-300 cursor-pointer"
          >
            {locale === "en" ? "हिन्दी" : "EN"}
          </button>
        </div>
      </div>

      {/* 3. Main Operational Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 md:px-8 py-6">
        {children}
      </main>
    </div>
  );
};
