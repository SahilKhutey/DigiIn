import React from "react";
import { ServicePage } from "../../patterns/ServicePage";
import { Card } from "../../components/ui/Card";
import { Alert } from "../../components/ui/Alert";

export const SecurityPrivacyView: React.FC = () => {
  return (
    <ServicePage
      title="Security & Privacy by Design"
      description="Security in DigiIn is not merely an afterthought or backend firewall—it is an explicit, user-facing UX guarantee."
      breadcrumbs={[
        { label: "Home", href: "#/" },
        { label: "Security & Privacy" },
      ]}
    >
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card variant="elevated" className="space-y-2">
            <h3 className="text-base font-bold text-[#092F4F] m-0">Zero Raw Document Retention</h3>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              DigiIn acts as a cryptographic claim pipeline. We exchange signed mathematical proofs rather than storing raw PDF or JPEG files.
            </p>
          </Card>

          <Card variant="elevated" className="space-y-2">
            <h3 className="text-base font-bold text-[#092F4F] m-0">Asymmetric Cryptography (Ed25519)</h3>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Every verification claim is signed using high-performance Edwards-curve Ed25519 keys adhering to RFC 7515/7519 standards.
            </p>
          </Card>

          <Card variant="elevated" className="space-y-2">
            <h3 className="text-base font-bold text-[#092F4F] m-0">DPDP Act 2023 Compliance</h3>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Enforces clear notice, purpose specification, minimum data processing, and citizen withdrawal rights.
            </p>
          </Card>

          <Card variant="elevated" className="space-y-2">
            <h3 className="text-base font-bold text-[#092F4F] m-0">Immutable Audit Trail</h3>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Every verification inquiry, consent grant, and inspection is permanently recorded in a tamper-evident audit ledger.
            </p>
          </Card>
        </div>

        <Alert type="info" title="Public JWKS Discovery">
          Public verification keys are accessible at <code>/.well-known/jwks.json</code> for independent, air-gapped cryptographic validation.
        </Alert>
      </div>
    </ServicePage>
  );
};
