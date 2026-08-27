import React from "react";
import { ServicePage } from "../../patterns/ServicePage";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";

interface ForCitizensViewProps {
  onStartJourney: () => void;
  onOpenWallet: () => void;
}

export const ForCitizensView: React.FC<ForCitizensViewProps> = ({
  onStartJourney,
  onOpenWallet,
}) => {
  return (
    <ServicePage
      title="For Citizens: Your Documents, Your Consent, Your Choice"
      description="DigiIn gives you a single, secure digital identity to verify your credentials across public services without handing over unredacted documents."
      breadcrumbs={[
        { label: "Home", href: "#/" },
        { label: "For Citizens" },
      ]}
      actions={
        <div className="flex gap-2">
          <Button variant="primary" onClick={onStartJourney}>
            Start Verification →
          </Button>
          <Button variant="secondary" onClick={onOpenWallet}>
            Open Vault
          </Button>
        </div>
      }
    >
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card variant="elevated" className="space-y-3">
            <span className="text-xs uppercase font-extrabold tracking-wider text-[#0B5D9B]">
              Sovereign Account
            </span>
            <h3 className="text-xl font-bold text-[#092F4F] m-0">Keep Verification Ready</h3>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Your DigiIn ID gives you instant access to all your verified education, identity, and transport records in one place.
            </p>
            <ul className="space-y-1.5 text-xs text-slate-700 list-none p-0 pt-2">
              <li>✓ Unique DigiIn ID (<code>DI-7K4M-9Q2X-8P6R</code>) for verified public services</li>
              <li>✓ Instant trust posture metrics across all your certificates</li>
              <li>✓ 1-click revocation of active sharing permissions</li>
            </ul>
          </Card>

          <Card variant="elevated" className="space-y-3">
            <span className="text-xs uppercase font-extrabold tracking-wider text-[#0B5D9B]">
              Informed Consent
            </span>
            <h3 className="text-xl font-bold text-[#092F4F] m-0">Know Before You Share</h3>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Never sign away generic permissions. You see the requesting organization, their official purpose, and exact data fields before authorizing.
            </p>
            <ul className="space-y-1.5 text-xs text-slate-700 list-none p-0 pt-2">
              <li>✓ Purpose limitation prevents oversharing and secondary data reuse</li>
              <li>✓ Zero-Knowledge Proof mode shares only pass/fail assertions</li>
              <li>✓ Immutable sovereign audit ledger logs every verification event</li>
            </ul>
          </Card>
        </div>
      </div>
    </ServicePage>
  );
};
