import React from "react";
import { ServicePage } from "../../patterns/ServicePage";
import { Card } from "../../components/ui/Card";

export const TermsView: React.FC = () => {
  return (
    <ServicePage
      title="Terms of Public Service"
      description="Guidelines governing sovereign verifiable credential exchanges between citizens, issuers, and requesting entities on DigiIn."
      breadcrumbs={[
        { label: "Home", href: "#/" },
        { label: "Terms of Service" },
      ]}
    >
      <div className="space-y-4">
        <Card variant="elevated" className="space-y-3 text-xs text-slate-600 leading-relaxed">
          <h3 className="text-base font-bold text-[#092F4F] m-0">1. Citizen Sovereignty & Consent</h3>
          <p className="m-0">
            No credential assertion is ever generated or transferred without the explicit, purpose-bound authorization of the citizen holding the DigiIn account.
          </p>

          <h3 className="text-base font-bold text-[#092F4F] mt-4 mb-0">2. Prohibited Over-Collection</h3>
          <p className="m-0">
            Requesting entities (Universities, Employers, Government Bodies) agree to request only the minimum necessary attributes required to fulfill their stated statutory or admission purpose.
          </p>

          <h3 className="text-base font-bold text-[#092F4F] mt-4 mb-0">3. Cryptographic Proof Validity</h3>
          <p className="m-0">
            DigiIn cryptographically signs claims using Ed25519 keys based on source registry verification. Proofs are valid strictly for the duration specified in the token payload claims.
          </p>
        </Card>
      </div>
    </ServicePage>
  );
};
