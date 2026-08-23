import React from "react";
import { ServicePage } from "../../patterns/ServicePage";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";

interface HelpFaqViewProps {
  onOpenContact: () => void;
}

export const HelpFaqView: React.FC<HelpFaqViewProps> = ({ onOpenContact }) => {
  const faqs = [
    {
      q: "What is DigiIn and how does it differ from regular DigiLocker?",
      a: "DigiIn is the next-generation verification layer built on top of DigiLocker. While DigiLocker stores your documents, DigiIn enables selective verification—sharing cryptographically signed assertions (e.g. 'Rahul passed 12th with >60%') with zero raw document files transferred.",
    },
    {
      q: "Does DigiIn store copies of my certificates?",
      a: "No. DigiIn adheres to a strict Zero Raw Document Storage policy. When a university or employer requests verification, DigiIn queries the official issuer in real-time, generates an Ed25519-signed proof, and immediately purges intermediate data.",
    },
    {
      q: "What is Zero-Knowledge Proof (ZKP) mode in DigiIn?",
      a: "ZKP mode allows you to prove that a qualification criteria is met (such as age >= 18 or marks >= 60%) without disclosing your exact date of birth, address, or subject-by-subject score breakdown.",
    },
    {
      q: "How does an organization verify my proof token offline?",
      a: "Proof tokens are self-contained RFC 7515/7519 JSON Web Signatures (JWS). Any verifier can validate the signature using DigiIn's public RFC 7517 JWKS key set without needing an active internet connection or server database query.",
    },
    {
      q: "What happens if my demographic details don't match the issuer registry?",
      a: "DigiIn features an Explainable Discrepancy Engine. It identifies the exact mismatched field (e.g. spelling variation) and gives you a 1-click option to submit supporting evidence to the Government Officer Adjudication Queue for manual review.",
    },
  ];

  return (
    <ServicePage
      title="Help Centre & Frequently Asked Questions"
      description="Find clear answers regarding document verification, citizen consent, cryptographic proof receipts, and security."
      breadcrumbs={[
        { label: "Home", href: "#/" },
        { label: "Help & FAQ" },
      ]}
      actions={
        <Button variant="secondary" onClick={onOpenContact}>
          Contact Support →
        </Button>
      }
    >
      <div className="space-y-4">
        <div className="space-y-3">
          {faqs.map((faq, idx) => (
            <details
              key={idx}
              className="bg-white border border-[#CBD5E1] rounded-xl p-4 cursor-pointer transition-all hover:border-[#94A3B8] open:border-[#0B5D9B] open:shadow-xs group"
              open={idx === 0}
            >
              <summary className="font-bold text-[#092F4F] text-sm md:text-base select-none flex items-center justify-between list-none">
                <span>{faq.q}</span>
                <span className="text-slate-400 text-lg font-bold group-open:rotate-45 transition-transform" aria-hidden="true">
                  +
                </span>
              </summary>
              <p className="text-xs text-slate-600 mt-3 pt-3 border-t border-slate-200 leading-relaxed m-0">
                {faq.a}
              </p>
            </details>
          ))}
        </div>

        <Card variant="elevated" className="text-center p-6 space-y-2 mt-6">
          <h3 className="text-lg font-bold text-[#092F4F] m-0">Still have questions?</h3>
          <p className="text-xs text-slate-600 m-0">
            Our support team and developer integration engineers are available to assist.
          </p>
          <div className="pt-2">
            <Button variant="primary" size="sm" onClick={onOpenContact}>
              Send a Support Inquiry
            </Button>
          </div>
        </Card>
      </div>
    </ServicePage>
  );
};
