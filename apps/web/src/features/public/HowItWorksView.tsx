import React from "react";
import { ServicePage } from "../../patterns/ServicePage";
import { Card } from "../../components/ui/Card";
import { Alert } from "../../components/ui/Alert";
import { Button } from "../../components/ui/Button";

interface HowItWorksViewProps {
  onStartJourney: () => void;
}

export const HowItWorksView: React.FC<HowItWorksViewProps> = ({ onStartJourney }) => {
  const steps = [
    {
      num: "01",
      title: "Organization Request",
      desc: "An accredited entity (such as ABC University or an employer) defines the exact credentials and attributes required for an admission or job application.",
      note: "No generic requests are allowed; every inquiry requires an accredited purpose.",
    },
    {
      num: "02",
      title: "Granular Review & Consent",
      desc: "The citizen opens the verification link or scans the QR code. DigiIn presents an itemized table of requested documents and purpose before seeking authorization.",
      note: "Citizens can toggle Zero-Knowledge Proof (ZKP) mode to share assertions instead of raw data.",
    },
    {
      num: "03",
      title: "Real-Time Issuer Verification",
      desc: "DigiIn queries official registries (CBSE, UIDAI, state education boards) directly to validate the claims in real-time.",
      note: "Takes less than 1.5 seconds with tamper-evident digital signature validation.",
    },
    {
      num: "04",
      title: "Cryptographic Proof Receipt",
      desc: "The organization receives an Ed25519-signed verification token (DLV-8F72-A92C) that can be verified offline via public JWKS discovery without storing any raw files.",
      note: "Zero document retention by design.",
    },
  ];

  return (
    <ServicePage
      title="How DigiIn Verification Works"
      description="A clear, predictable, 4-step citizen journey designed to eliminate paperwork and protect citizen privacy."
      breadcrumbs={[
        { label: "Home", href: "#/" },
        { label: "How It Works" },
      ]}
      actions={
        <Button variant="primary" onClick={onStartJourney}>
          Experience Demo Journey →
        </Button>
      }
    >
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {steps.map((step) => (
            <Card key={step.num} variant="elevated" className="space-y-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-[#0B5D9B] text-white font-extrabold flex items-center justify-center text-sm shadow-sm">
                  {step.num}
                </div>
                <h3 className="text-lg font-bold text-[#092F4F] m-0">{step.title}</h3>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed m-0">{step.desc}</p>
              <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-[11px] text-slate-500 font-medium">
                💡 {step.note}
              </div>
            </Card>
          ))}
        </div>

        <Alert type="info" title="Zero Raw Document Storage Guarantee">
          DigiIn never stores copies of your unredacted certificates on third-party servers. All exchanges occur through cryptographically signed claim assertions adhering to RFC 7515/7519 standards.
        </Alert>
      </div>
    </ServicePage>
  );
};
