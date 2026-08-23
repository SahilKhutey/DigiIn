import React from "react";
import { ServicePage } from "../../patterns/ServicePage";
import { Card } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";

export const PrivacyPolicyView: React.FC = () => {
  return (
    <ServicePage
      title="Privacy Policy & Data Protection Notice"
      description="DigiIn operates under the Digital Personal Data Protection (DPDP) Act 2023 with a strict zero-document-retention architecture."
      breadcrumbs={[
        { label: "Home", href: "#/" },
        { label: "Privacy Policy" },
      ]}
    >
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Badge variant="success">DPDP Act 2023 Compliant</Badge>
          <Badge variant="info">Zero Retention Standard</Badge>
        </div>

        <Card variant="elevated" className="space-y-3 text-xs text-slate-600 leading-relaxed">
          <h3 className="text-base font-bold text-[#092F4F] m-0">1. Data Minimization & Zero Storage</h3>
          <p className="m-0">
            DigiIn never stores unredacted PDF or image copies of your certificates on central servers. Verification occurs in memory and produces self-contained cryptographic claim assertions.
          </p>

          <h3 className="text-base font-bold text-[#092F4F] mt-4 mb-0">2. Right to Revocation & Erasure</h3>
          <p className="m-0">
            Citizens can instantly revoke active sharing grants from their Citizen Wallet dashboard with 1 click.
          </p>

          <h3 className="text-base font-bold text-[#092F4F] mt-4 mb-0">3. Tamper-Evident Audit Ledger</h3>
          <p className="m-0">
            All verification requests and consent actions are logged into an append-only audit trail accessible exclusively to the citizen.
          </p>
        </Card>
      </div>
    </ServicePage>
  );
};
