import React, { useState, useEffect } from "react";
import { Button } from "../../components/ui";
import { AppView } from "../../layouts/GovHeader";

interface LandingViewProps {
  onStartJourney: () => void;
  onOpenWallet: () => void;
  onOpenVerifier: () => void;
  onNavigate?: (view: AppView) => void;
}

export const LandingView: React.FC<LandingViewProps> = ({
  onStartJourney,
  onOpenWallet,
  onOpenVerifier,
  onNavigate,
}) => {
  const [scanState, setScanState] = useState<"scanning" | "verified">("scanning");

  useEffect(() => {
    const timer = setTimeout(() => {
      setScanState("verified");
    }, 1200);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="page-enter space-y-16 md:space-y-24 py-4 max-w-[1200px] mx-auto">
      {/* 1. HERO BLOCK */}
      <section className="relative overflow-hidden rounded-3xl border border-slate-200 bg-white p-8 md:p-14 shadow-2xs">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          {/* Left Column: Headline & Action */}
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2">
              <span className="text-[11px] font-extrabold uppercase tracking-widest text-[#0B5D9B] bg-[#EBF4FA] px-3 py-1 rounded-full border border-[#BAE6FD]">
                DIGITAL TRUST
              </span>
              <span className="text-xs text-slate-400 font-semibold hidden sm:inline">
                National Public Infrastructure
              </span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-[54px] font-extrabold text-[#092F4F] tracking-tight leading-[1.08] m-0">
              Verify once.<br />
              Use anywhere.
            </h1>

            <p className="text-base sm:text-lg text-slate-600 leading-relaxed max-w-xl m-0">
              Keep verified documents and share only the information a service needs.
            </p>

            {/* Primary Actions */}
            <div className="flex flex-wrap items-center gap-3.5 pt-2">
              <Button
                variant="primary"
                size="lg"
                onClick={onStartJourney}
                className="shadow-sm font-bold text-base px-7 cursor-pointer"
              >
                Get started →
              </Button>

              <button
                type="button"
                onClick={() => onNavigate?.("HOW_IT_WORKS")}
                className="px-5 py-3 rounded-xl text-sm font-bold text-slate-700 hover:text-[#0B5D9B] hover:bg-slate-50 transition-all cursor-pointer inline-flex items-center gap-1.5"
              >
                How it works <span aria-hidden="true">&rarr;</span>
              </button>

              <button
                type="button"
                onClick={onOpenWallet}
                className="px-4 py-3 rounded-xl text-xs font-semibold text-slate-500 hover:text-slate-800 transition-all cursor-pointer"
              >
                🗂️ Open Document Vault
              </button>
            </div>
          </div>

          {/* Right Column: Purposeful Verification Simulation Animation */}
          <div className="lg:col-span-5 flex justify-center">
            <div
              className="w-full max-w-sm rounded-2xl border border-slate-200 bg-slate-50 p-6 shadow-md relative overflow-hidden transition-all"
              aria-label="Digital Credential Verification Preview"
            >
              {/* Scan Bar Effect */}
              {scanState === "scanning" && (
                <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-cyan-400 to-blue-600 animate-pulse" />
              )}

              <div className="flex items-center justify-between border-b border-slate-200 pb-3 mb-4">
                <div className="flex items-center gap-2">
                  <div className="h-7 w-7 rounded-lg bg-[#0B5D9B] text-white flex items-center justify-center text-xs font-extrabold">
                    D
                  </div>
                  <div>
                    <div className="text-xs font-bold text-[#092F4F]">Digital Credential</div>
                    <div className="text-[10px] text-slate-400">RFC 7515 / 8032 JWS</div>
                  </div>
                </div>
                <span
                  className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border transition-all ${
                    scanState === "verified"
                      ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                      : "bg-blue-50 text-blue-800 border-blue-200 animate-pulse"
                  }`}
                >
                  {scanState === "verified" ? "✓ VERIFIED" : "Scanning..."}
                </span>
              </div>

              <div className="space-y-2 mb-4 bg-white p-3.5 rounded-xl border border-slate-200/80 text-xs">
                <div className="font-bold text-slate-800 text-sm">Class XII Senior Certificate</div>
                <div className="text-slate-500 flex justify-between">
                  <span>Issuer:</span>
                  <strong className="text-slate-700">CBSE Central Registry</strong>
                </div>
                <div className="text-slate-500 flex justify-between">
                  <span>Status:</span>
                  <strong className="text-emerald-700">Proof Ready</strong>
                </div>
              </div>

              <div className="p-2.5 bg-slate-900 rounded-xl text-[11px] font-mono text-emerald-400 flex items-center justify-between">
                <span>🛡️ Secure Proof</span>
                <code className="text-[10px] text-cyan-300">TOKEN: 8f9a••2026</code>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. TRUST STRIP (One Clean Line) */}
      <section className="bg-slate-50 border border-slate-200 rounded-2xl py-4 px-6 text-xs text-slate-700 shadow-2xs">
        <div className="flex flex-wrap items-center justify-between gap-4 font-semibold">
          <div className="flex items-center gap-2 text-[#092F4F] font-bold">
            <span>🔒</span>
            <span className="uppercase tracking-wider text-[11px]">Secure by design:</span>
          </div>
          <div className="flex flex-wrap items-center gap-4 sm:gap-6 text-xs">
            <span className="flex items-center gap-1.5 text-emerald-800">
              ✓ Explicit consent
            </span>
            <span className="flex items-center gap-1.5 text-blue-800">
              ✓ Verified issuers
            </span>
            <span className="flex items-center gap-1.5 text-indigo-800">
              ✓ Minimum disclosure
            </span>
            <span className="flex items-center gap-1.5 text-slate-800">
              ✓ Secure proofs
            </span>
          </div>
        </div>
      </section>

      {/* 3. SERVICES (4 Unified Template Cards in 2x2 Grid) */}
      <section className="space-y-8">
        <div className="space-y-2 text-center max-w-xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-extrabold text-[#092F4F] m-0">
            Services
          </h2>
          <p className="text-sm text-slate-600 m-0">
            Everything you need to verify and share documents securely.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Card 1: Documents */}
          <article className="interactive-card flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-7 shadow-xs min-h-[220px]">
            <div>
              <div className="h-10 w-10 rounded-xl bg-blue-50 text-[#0B5D9B] text-xl flex items-center justify-center font-bold mb-4">
                🗂️
              </div>
              <h3 className="text-lg font-bold text-[#092F4F] mb-1.5">
                Documents
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Keep your verified documents in one place.
              </p>
            </div>
            <button
              type="button"
              onClick={onOpenWallet}
              className="inline-flex items-center gap-1.5 text-sm font-bold text-[#0B5D9B] card-arrow pt-4 cursor-pointer text-left"
            >
              View documents <span aria-hidden="true">&rarr;</span>
            </button>
          </article>

          {/* Card 2: Verification */}
          <article className="interactive-card flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-7 shadow-xs min-h-[220px]">
            <div>
              <div className="h-10 w-10 rounded-xl bg-emerald-50 text-emerald-700 text-xl flex items-center justify-center font-bold mb-4">
                🛡️
              </div>
              <h3 className="text-lg font-bold text-[#092F4F] mb-1.5">
                Verification
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Prove a document or credential without sharing the original.
              </p>
            </div>
            <button
              type="button"
              onClick={onStartJourney}
              className="inline-flex items-center gap-1.5 text-sm font-bold text-[#0B5D9B] card-arrow pt-4 cursor-pointer text-left"
            >
              Start verification <span aria-hidden="true">&rarr;</span>
            </button>
          </article>

          {/* Card 3: Credentials */}
          <article className="interactive-card flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-7 shadow-xs min-h-[220px]">
            <div>
              <div className="h-10 w-10 rounded-xl bg-indigo-50 text-indigo-700 text-xl flex items-center justify-center font-bold mb-4">
                📜
              </div>
              <h3 className="text-lg font-bold text-[#092F4F] mb-1.5">
                Credentials
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Access verified digital credentials issued from trusted sources.
              </p>
            </div>
            <button
              type="button"
              onClick={() => onNavigate?.("CREDENTIALS")}
              className="inline-flex items-center gap-1.5 text-sm font-bold text-[#0B5D9B] card-arrow pt-4 cursor-pointer text-left"
            >
              View credentials <span aria-hidden="true">&rarr;</span>
            </button>
          </article>

          {/* Card 4: Sharing */}
          <article className="interactive-card flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-7 shadow-xs min-h-[220px]">
            <div>
              <div className="h-10 w-10 rounded-xl bg-amber-50 text-amber-700 text-xl flex items-center justify-center font-bold mb-4">
                🔐
              </div>
              <h3 className="text-lg font-bold text-[#092F4F] mb-1.5">
                Sharing
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Control who can access your verified information.
              </p>
            </div>
            <button
              type="button"
              onClick={() => onNavigate?.("CONSENT")}
              className="inline-flex items-center gap-1.5 text-sm font-bold text-[#0B5D9B] card-arrow pt-4 cursor-pointer text-left"
            >
              Manage sharing <span aria-hidden="true">&rarr;</span>
            </button>
          </article>
        </div>
      </section>

      {/* 4. HOW IT WORKS (3 Simple Sequential Steps) */}
      <section className="space-y-10">
        <div className="space-y-2 text-center max-w-xl mx-auto">
          <span className="text-xs uppercase font-extrabold tracking-wider text-[#0B5D9B]">
            Process
          </span>
          <h2 className="text-3xl md:text-4xl font-extrabold text-[#092F4F] m-0">
            How DigiIn Works
          </h2>
          <p className="text-sm text-slate-600 m-0">
            Three simple steps to tamper-proof verification.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
          {/* Step 1 */}
          <div className="bg-white border border-slate-200 rounded-2xl p-7 shadow-xs space-y-3 relative">
            <span className="inline-block text-xs font-extrabold px-3 py-1 rounded-full bg-blue-50 text-[#0B5D9B] border border-blue-200 font-mono">
              01 Add
            </span>
            <h3 className="text-lg font-bold text-[#092F4F]">Add Record</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Add your document or credential into your sovereign DigiIn vault.
            </p>
          </div>

          {/* Step 2 */}
          <div className="bg-white border border-slate-200 rounded-2xl p-7 shadow-xs space-y-3 relative">
            <span className="inline-block text-xs font-extrabold px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 font-mono">
              02 Verify
            </span>
            <h3 className="text-lg font-bold text-[#092F4F]">Verify Authority</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Verify through an authorised official registry such as CBSE, UIDAI, or MoRTH.
            </p>
          </div>

          {/* Step 3 */}
          <div className="bg-white border border-slate-200 rounded-2xl p-7 shadow-xs space-y-3 relative">
            <span className="inline-block text-xs font-extrabold px-3 py-1 rounded-full bg-indigo-50 text-indigo-800 border border-indigo-200 font-mono">
              03 Share
            </span>
            <h3 className="text-lg font-bold text-[#092F4F]">Share Proof</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Share a secure, minimum-disclosure cryptographic proof without original files.
            </p>
          </div>
        </div>
      </section>

      {/* 5. TRUST & SECURITY SECTION */}
      <section className="bg-gradient-to-r from-[#092F4F] to-[#0B5D9B] text-white rounded-3xl p-8 md:p-12 shadow-md">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          <div className="lg:col-span-7 space-y-4">
            <span className="text-xs font-bold uppercase tracking-widest text-cyan-300">
              SOVEREIGN PRIVACY
            </span>
            <h2 className="text-2xl md:text-4xl font-extrabold text-white m-0 leading-tight">
              Your documents stay yours.
            </h2>
            <p className="text-sm md:text-base text-slate-200 leading-relaxed m-0">
              DigiIn is designed around <strong>explicit consent</strong>, <strong>minimum disclosure</strong>, <strong>verified issuers</strong>, and <strong>secure cryptographic proofs</strong>.
            </p>
            <div className="pt-2">
              <button
                type="button"
                onClick={() => onNavigate?.("SECURITY")}
                className="inline-flex items-center gap-1.5 text-xs font-bold text-cyan-300 hover:text-white transition-colors cursor-pointer"
              >
                Learn about security &rarr;
              </button>
            </div>
          </div>

          {/* Diagram Flow */}
          <div className="lg:col-span-5 bg-black/30 p-5 rounded-2xl border border-white/10 text-xs font-mono space-y-2">
            <div className="flex items-center justify-between text-slate-300">
              <span>📁 Document</span>
              <span className="text-cyan-400">&rarr;</span>
              <span>🏛️ Registry</span>
            </div>
            <div className="flex items-center justify-center text-cyan-400 text-sm font-bold">
              &darr;
            </div>
            <div className="flex items-center justify-between text-slate-300">
              <span>🏢 Requester</span>
              <span className="text-cyan-400">&larr;</span>
              <span>🛡️ Proof</span>
            </div>
          </div>
        </div>
      </section>

      {/* 6. FINAL CTA BLOCK */}
      <section className="text-center py-10 px-6 rounded-3xl border border-slate-200 bg-white shadow-2xs space-y-4">
        <h2 className="text-2xl md:text-3xl font-extrabold text-[#092F4F] m-0">
          Ready to verify securely?
        </h2>
        <p className="text-xs md:text-sm text-slate-500 max-w-md mx-auto m-0">
          Join citizens verifying academic and identity claims with instant mathematical proofs.
        </p>
        <div className="pt-2">
          <Button
            variant="primary"
            size="lg"
            onClick={onStartJourney}
            className="shadow-sm font-bold text-base px-8 cursor-pointer"
          >
            Get Started →
          </Button>
        </div>
      </section>
    </div>
  );
};
