import React, { useState } from "react";
import { FormPage } from "../../patterns/FormPage";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { useAuth } from "../../context/AuthContext";
import { useLanguage } from "../../context/LanguageContext";

interface OnboardingViewProps {
  onComplete: () => void;
}

export const OnboardingView: React.FC<OnboardingViewProps> = ({ onComplete }) => {
  const { completeOnboarding, user } = useAuth();
  const { setLocale } = useLanguage();
  const [name, setName] = useState(user?.name || "Rahul Sharma");
  const [selectedLang, setSelectedLang] = useState<"en" | "hi">("en");
  const [consentAgreed, setConsentAgreed] = useState(false);
  const [showIdCard, setShowIdCard] = useState(false);
  const [copied, setCopied] = useState(false);

  const assignedDin = "DIN-7K4P-92M8";

  const handleCreateAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!consentAgreed) return;

    await completeOnboarding(name, selectedLang);
    setLocale(selectedLang);
    setShowIdCard(true);
  };

  const handleCopy = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(assignedDin);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  return (
    <FormPage
      title={showIdCard ? "Your DigiIn ID" : "Welcome to DigiIn"}
      description={
        showIdCard
          ? "Your sovereign identity has been created and assigned."
          : "DigiIn helps you securely verify and share your documents when a service needs them."
      }
      backHref="#/sign-in"
      backLabel="Back"
    >
      {showIdCard ? (
        /* DigiIn ID Presentation Card */
        <div className="space-y-6 text-center">
          <div className="p-6 bg-[#092F4F] text-white rounded-2xl shadow-lg border-2 border-[#0B5D9B] space-y-3">
            <span className="text-xs uppercase font-extrabold tracking-widest text-[#94A3B8]">
              Your DigiIn ID
            </span>
            <div className="font-mono text-3xl font-extrabold text-[#38BDF8] tracking-widest py-1">
              {assignedDin}
            </div>
            <p className="text-xs text-slate-300 max-w-sm mx-auto leading-relaxed m-0">
              This ID identifies your DigiIn account. It does not expose your documents by itself.
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3">
            <Button
              variant="secondary"
              size="md"
              type="button"
              onClick={handleCopy}
            >
              {copied ? "✓ Copied!" : "📋 Copy ID"}
            </Button>

            <Button
              variant="primary"
              size="md"
              type="button"
              onClick={onComplete}
            >
              Continue to Dashboard →
            </Button>
          </div>
        </div>
      ) : (
        /* First-Time Onboarding Form */
        <form onSubmit={handleCreateAccount} className="space-y-6">
          {/* 4 Core Account Benefits */}
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
            <h3 className="text-xs uppercase font-bold text-[#092F4F] tracking-wider m-0">
              Your account gives you:
            </h3>
            <ul className="space-y-1.5 text-xs text-slate-700 list-none p-0 m-0">
              <li className="flex items-center gap-2">
                <span className="text-[#14743F] font-bold">✓</span> A unique sovereign DigiIn ID
              </li>
              <li className="flex items-center gap-2">
                <span className="text-[#14743F] font-bold">✓</span> A secure document verification history
              </li>
              <li className="flex items-center gap-2">
                <span className="text-[#14743F] font-bold">✓</span> Control over what you share
              </li>
              <li className="flex items-center gap-2">
                <span className="text-[#14743F] font-bold">✓</span> Consent-based verification
              </li>
            </ul>
          </div>

          {/* Language Preference */}
          <div className="space-y-2">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600">
              Your preferred language
            </label>
            <div className="grid grid-cols-2 gap-3">
              <label
                className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer select-none transition-all ${
                  selectedLang === "en"
                    ? "bg-[#EBF4FA] border-[#0B5D9B] ring-1 ring-[#0B5D9B]"
                    : "bg-white border-[#CBD5E1] hover:border-slate-400"
                }`}
              >
                <input
                  type="radio"
                  name="language"
                  value="en"
                  checked={selectedLang === "en"}
                  onChange={() => setSelectedLang("en")}
                  className="w-4 h-4 accent-[#0B5D9B]"
                />
                <span className="text-sm font-bold text-[#092F4F]">English</span>
              </label>

              <label
                className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer select-none transition-all ${
                  selectedLang === "hi"
                    ? "bg-[#EBF4FA] border-[#0B5D9B] ring-1 ring-[#0B5D9B]"
                    : "bg-white border-[#CBD5E1] hover:border-slate-400"
                }`}
              >
                <input
                  type="radio"
                  name="language"
                  value="hi"
                  checked={selectedLang === "hi"}
                  onChange={() => setSelectedLang("hi")}
                  className="w-4 h-4 accent-[#0B5D9B]"
                />
                <span className="text-sm font-bold text-[#092F4F]">हिन्दी</span>
              </label>
            </div>
          </div>

          {/* Account Creation Consent */}
          <label className="flex items-start gap-3 p-3 bg-slate-50 border border-slate-200 rounded-xl cursor-pointer select-none">
            <input
              type="checkbox"
              checked={consentAgreed}
              onChange={(e) => setConsentAgreed(e.target.checked)}
              className="w-5 h-5 mt-0.5 accent-[#0B5D9B] rounded cursor-pointer"
              required
            />
            <span className="text-xs text-slate-700 leading-relaxed">
              I consent to creating my DigiIn account and linking my verified document records under DPDP Act 2023 protections.
            </span>
          </label>

          <Button
            variant="primary"
            size="lg"
            type="submit"
            fullWidth
            disabled={!consentAgreed}
          >
            Create my DigiIn account →
          </Button>
        </form>
      )}
    </FormPage>
  );
};
