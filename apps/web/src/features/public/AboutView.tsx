import React from "react";
import { ServicePage } from "../../patterns/ServicePage";
import { Card, CardTitle, CardDescription } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";

interface AboutViewProps {
  onStartJourney: () => void;
}

export const AboutView: React.FC<AboutViewProps> = ({ onStartJourney }) => {
  return (
    <ServicePage
      title="A Trusted Verification Layer for Citizen Services"
      description="DigiIn is built around a single sovereign principle: citizens should never have to repeatedly submit paper or unredacted digital document copies to every service that needs to verify them."
      breadcrumbs={[
        { label: "Home", href: "#/" },
        { label: "About DigiIn" },
      ]}
      actions={
        <Button variant="primary" onClick={onStartJourney}>
          Try Verification Flow →
        </Button>
      }
    >
      <div className="space-y-8">
        {/* Section 1: The Problem vs Solution */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card variant="bordered" className="border-amber-400 bg-white">
            <div className="flex items-center gap-2 mb-3">
              <Badge variant="warning">The Status Quo</Badge>
              <h3 className="text-lg font-bold text-[#092F4F] m-0">Repeated Document Submissions</h3>
            </div>
            <ul className="space-y-2 text-xs text-slate-600 list-none p-0 m-0">
              <li className="flex items-start gap-2">
                <span className="text-amber-600 font-bold">✕</span>
                Citizens upload full, unredacted marksheet copies for admissions, jobs, and schemes.
              </li>
              <li className="flex items-start gap-2">
                <span className="text-amber-600 font-bold">✕</span>
                Institutions store petabytes of personal PII, creating massive data leakage risks.
              </li>
              <li className="flex items-start gap-2">
                <span className="text-amber-600 font-bold">✕</span>
                Verifications take days or weeks of manual back-and-forth phone calls and physical audits.
              </li>
            </ul>
          </Card>

          <Card variant="bordered" className="border-emerald-500 bg-white">
            <div className="flex items-center gap-2 mb-3">
              <Badge variant="success">The DigiIn Standard</Badge>
              <h3 className="text-lg font-bold text-[#092F4F] m-0">Zero Raw Document Transfers</h3>
            </div>
            <ul className="space-y-2 text-xs text-slate-600 list-none p-0 m-0">
              <li className="flex items-start gap-2">
                <span className="text-emerald-600 font-bold">✓</span>
                Connect trusted government sources (CBSE, UIDAI, MoRTH) once.
              </li>
              <li className="flex items-start gap-2">
                <span className="text-emerald-600 font-bold">✓</span>
                Grant purpose-specific, granular consent for only the required attributes.
              </li>
              <li className="flex items-start gap-2">
                <span className="text-emerald-600 font-bold">✓</span>
                Share cryptographically signed Ed25519 verifiable assertions in 3 seconds.
              </li>
            </ul>
          </Card>
        </div>

        {/* Section 2: Core Engineering Principles */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-[#092F4F] m-0">Our Founding Principles</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card variant="elevated" className="space-y-2">
              <div className="w-9 h-9 rounded-lg bg-[#EBF4FA] text-[#0B5D9B] font-bold flex items-center justify-center text-sm border border-[#BAE6FD]">
                01
              </div>
              <h4 className="text-base font-bold text-[#092F4F] m-0">Citizen Sovereignty</h4>
              <p className="text-xs text-slate-600 leading-relaxed m-0">
                You own your records. Consent is explicit, purpose-limited, and instantly revocable.
              </p>
            </Card>

            <Card variant="elevated" className="space-y-2">
              <div className="w-9 h-9 rounded-lg bg-[#EBF4FA] text-[#0B5D9B] font-bold flex items-center justify-center text-sm border border-[#BAE6FD]">
                02
              </div>
              <h4 className="text-base font-bold text-[#092F4F] m-0">Minimum Disclosure</h4>
              <p className="text-xs text-slate-600 leading-relaxed m-0">
                Verify assertions (e.g. <em>Aggregate &gt;= 60%</em>) using Zero-Knowledge proofs rather than sharing raw marks.
              </p>
            </Card>

            <Card variant="elevated" className="space-y-2">
              <div className="w-9 h-9 rounded-lg bg-[#EBF4FA] text-[#0B5D9B] font-bold flex items-center justify-center text-sm border border-[#BAE6FD]">
                03
              </div>
              <h4 className="text-base font-bold text-[#092F4F] m-0">Public Trust & Standards</h4>
              <p className="text-xs text-slate-600 leading-relaxed m-0">
                Built strictly on UX4G 3.0 government accessibility and DPDP Act 2023 compliance.
              </p>
            </Card>
          </div>
        </div>
      </div>
    </ServicePage>
  );
};
