import React from "react";
import { ServicePage } from "../../patterns/ServicePage";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";

interface ForOrganisationsViewProps {
  onOpenVerifier: () => void;
}

export const ForOrganisationsView: React.FC<ForOrganisationsViewProps> = ({ onOpenVerifier }) => {
  return (
    <ServicePage
      title="For Organisations: Request Verified Proofs, Not Unredacted Files"
      description="DigiIn allows universities, employers, and government agencies to verify candidate qualifications instantly without managing document liability or PII storage."
      breadcrumbs={[
        { label: "Home", href: "#/" },
        { label: "For Organisations" },
      ]}
      actions={
        <Button variant="primary" onClick={onOpenVerifier}>
          Open Verifier Portal →
        </Button>
      }
    >
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card variant="elevated" className="space-y-3">
            <span className="text-xs uppercase font-extrabold tracking-wider text-[#0B5D9B]">
              Query Gateway
            </span>
            <h3 className="text-xl font-bold text-[#092F4F] m-0">Define Precise Verification Scope</h3>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Create purpose-bound verification queries and generate dynamic scannable QR codes for admissions or job listings.
            </p>
            <ul className="space-y-1.5 text-xs text-slate-700 list-none p-0 pt-2">
              <li>✓ Request only required attributes (e.g. Class 12 passing year + aggregate)</li>
              <li>✓ Receive real-time signed cryptographic tokens directly from issuers</li>
              <li>✓ Full REST API and Webhook integration support</li>
            </ul>
          </Card>

          <Card variant="elevated" className="space-y-3">
            <span className="text-xs uppercase font-extrabold tracking-wider text-[#0B5D9B]">
              Cryptographic Trust
            </span>
            <h3 className="text-xl font-bold text-[#092F4F] m-0">Offline Asymmetric Proof Validation</h3>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Validate proof tokens offline without server dependencies using public RFC 7517 JWKS discovery keys.
            </p>
            <ul className="space-y-1.5 text-xs text-slate-700 list-none p-0 pt-2">
              <li>✓ Ed25519 asymmetric mathematical verification</li>
              <li>✓ Zero liability from storing unredacted citizen identity files</li>
              <li>✓ Fully compliant with DPDP Act 2023 data fiduciary requirements</li>
            </ul>
          </Card>
        </div>
      </div>
    </ServicePage>
  );
};
