import React from "react";
import { Button, Card, Badge, Alert } from "../../components/ui";
import { useLanguage } from "../../context/LanguageContext";
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
  const { t } = useLanguage();

  return (
    <div className="space-y-12">
      {/* 1. Hero Section: Goal-Driven & Citizen-Focused */}
      <section className="bg-white border border-[#CBD5E1] rounded-2xl p-6 md:p-12 shadow-sm relative overflow-hidden">
        <div className="max-w-3xl space-y-6">
          <div className="inline-flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-widest text-[#0B5D9B] bg-[#EBF4FA] px-3 py-1 rounded-full border border-[#BAE6FD]">
              Digital Public Infrastructure
            </span>
            <span className="text-xs text-slate-500 font-semibold">
              UX4G 3.0 Standard
            </span>
          </div>

          <h1 className="text-3xl md:text-5xl font-extrabold text-[#092F4F] tracking-tight leading-tight m-0">
            Verify once. Share securely anywhere.
          </h1>

          <p className="text-base md:text-lg text-[#475569] leading-relaxed max-w-2xl m-0">
            DigiIn helps citizens use verified digital documents across government, universities, and employers without repeatedly uploading raw unredacted document copies.
          </p>

          {/* Primary & Secondary CTAs */}
          <div className="flex flex-wrap items-center gap-4 pt-2">
            <Button
              variant="primary"
              size="lg"
              onClick={onStartJourney}
              className="shadow-md"
            >
              Start Verification Journey →
            </Button>

            <Button
              variant="secondary"
              size="lg"
              onClick={onOpenWallet}
            >
              Open Document Vault
            </Button>

            <Button
              variant="outline"
              size="lg"
              onClick={() => onNavigate?.("HOW_IT_WORKS")}
            >
              See How It Works
            </Button>
          </div>

          {/* Trust Row */}
          <div className="flex flex-wrap items-center gap-4 pt-2 text-xs font-bold text-slate-600">
            <span className="flex items-center gap-1.5 bg-[#DFF6E8] text-[#14743F] px-3 py-1 rounded-full border border-emerald-300">
              ✓ Consent-led by Design
            </span>
            <span className="flex items-center gap-1.5 bg-[#EBF4FA] text-[#0B5D9B] px-3 py-1 rounded-full border border-[#BAE6FD]">
              ✓ WCAG 2.1 AA Accessible
            </span>
            <span className="flex items-center gap-1.5 bg-[#F8FAFC] text-slate-700 px-3 py-1 rounded-full border border-slate-300">
              ✓ DPDP Act 2023 Compliant
            </span>
          </div>
        </div>
      </section>

      {/* 2. Why DigiIn Section */}
      <section className="space-y-6">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <span className="text-xs uppercase font-extrabold tracking-wider text-[#0B5D9B]">
            Why DigiIn
          </span>
          <h2 className="text-2xl md:text-3xl font-bold text-[#092F4F] m-0">
            Less Paperwork. More Trust.
          </h2>
          <p className="text-sm text-[#475569] m-0">
            A reusable verification layer for all citizen-facing services.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card variant="elevated" className="space-y-3">
            <div className="w-10 h-10 rounded-xl bg-[#EBF4FA] text-[#0B5D9B] font-extrabold flex items-center justify-center text-sm border border-[#BAE6FD]">
              01
            </div>
            <h3 className="text-lg font-bold text-[#092F4F] m-0">Verify Digitally at Source</h3>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Use trusted digital documents from official registries (CBSE, UIDAI, MoRTH) instead of uploading manual copies.
            </p>
          </Card>

          <Card variant="elevated" className="space-y-3">
            <div className="w-10 h-10 rounded-xl bg-[#EBF4FA] text-[#0B5D9B] font-extrabold flex items-center justify-center text-sm border border-[#BAE6FD]">
              02
            </div>
            <h3 className="text-lg font-bold text-[#092F4F] m-0">Informed & Granular Consent</h3>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              See who is asking, what attributes they need, and for what purpose before you approve. Never sign generic agreements.
            </p>
          </Card>

          <Card variant="elevated" className="space-y-3">
            <div className="w-10 h-10 rounded-xl bg-[#EBF4FA] text-[#0B5D9B] font-extrabold flex items-center justify-center text-sm border border-[#BAE6FD]">
              03
            </div>
            <h3 className="text-lg font-bold text-[#092F4F] m-0">Share Cryptographic Proof</h3>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Share an Ed25519-signed verification assertion (DLV token) instead of exposing unredacted document files.
            </p>
          </Card>
        </div>
      </section>

      {/* 3. Audience Split: For Citizens & For Organisations */}
      <section className="space-y-6">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <span className="text-xs uppercase font-extrabold tracking-wider text-[#0B5D9B]">
            Built for Public Services
          </span>
          <h2 className="text-2xl md:text-3xl font-bold text-[#092F4F] m-0">
            One Foundation, Many Services
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div
            onClick={() => onNavigate?.("FOR_CITIZENS")}
            className="p-6 md:p-8 bg-white border border-[#CBD5E1] rounded-2xl shadow-sm hover:border-[#0B5D9B] hover:shadow-md transition-all cursor-pointer space-y-4 group"
          >
            <div className="flex items-center justify-between">
              <div className="w-12 h-12 rounded-xl bg-[#EBF4FA] text-[#0B5D9B] text-xl font-extrabold flex items-center justify-center">
                👤
              </div>
              <span className="text-sm font-bold text-[#0B5D9B] group-hover:translate-x-1 transition-transform">
                Explore Citizen Portal →
              </span>
            </div>
            <div>
              <h3 className="text-xl font-bold text-[#092F4F] m-0">For Citizens</h3>
              <p className="text-xs text-slate-600 mt-1 mb-0 leading-relaxed">
                Manage your verified credentials, sovereign DigiIn ID (<code>DIN-84K2-19Q7</code>), and review active consent grants.
              </p>
            </div>
          </div>

          <div
            onClick={() => onNavigate?.("FOR_ORGANISATIONS")}
            className="p-6 md:p-8 bg-white border border-[#CBD5E1] rounded-2xl shadow-sm hover:border-[#0B5D9B] hover:shadow-md transition-all cursor-pointer space-y-4 group"
          >
            <div className="flex items-center justify-between">
              <div className="w-12 h-12 rounded-xl bg-[#EBF4FA] text-[#0B5D9B] text-xl font-extrabold flex items-center justify-center">
                🏛️
              </div>
              <span className="text-sm font-bold text-[#0B5D9B] group-hover:translate-x-1 transition-transform">
                Explore Verifier Portal →
              </span>
            </div>
            <div>
              <h3 className="text-xl font-bold text-[#092F4F] m-0">For Organisations</h3>
              <p className="text-xs text-slate-600 mt-1 mb-0 leading-relaxed">
                Request only the evidence you need for admissions or jobs, and receive instant verifiable tokens with zero liability.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 4. Ready to Experience Banner */}
      <section className="bg-gradient-to-r from-[#092F4F] to-[#0B5D9B] rounded-2xl p-8 md:p-12 text-white shadow-lg flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-2">
          <span className="text-xs font-bold uppercase tracking-widest text-cyan-300">
            Working Demo Experience
          </span>
          <h2 className="text-2xl md:text-3xl font-extrabold m-0 text-white">
            Try the Complete Verification Journey
          </h2>
          <p className="text-xs md:text-sm text-slate-200 m-0 max-w-xl">
            Experience the citizen flow from request review and granular consent to real-time verification and signed proof generation.
          </p>
        </div>

        <Button
          variant="secondary"
          size="lg"
          onClick={onStartJourney}
          className="shrink-0 bg-white text-[#092F4F] hover:bg-slate-100 font-bold shadow-md"
        >
          Start Verification Flow →
        </Button>
      </section>
    </div>
  );
};
