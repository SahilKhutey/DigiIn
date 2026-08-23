import React, { useState } from "react";
import { FormPage } from "../../patterns/FormPage";
import { Button } from "../../components/ui/Button";
import { Alert } from "../../components/ui/Alert";
import { Stepper } from "../../components/ui/ProgressIndicator";

interface ConsentAuthorizationViewProps {
  onAuthorize: (options: { zkpMode: boolean; durationHours: number }) => void;
  onDecline: () => void;
}

export const ConsentAuthorizationView: React.FC<ConsentAuthorizationViewProps> = ({
  onAuthorize,
  onDecline,
}) => {
  const [consentChecked, setConsentChecked] = useState(false);
  const [zkpMode, setZkpMode] = useState(true);
  const [durationHours, setDurationHours] = useState(24);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!consentChecked) return;
    onAuthorize({ zkpMode, durationHours });
  };

  return (
    <FormPage
      title="Provide Informed Consent"
      description="Grant permission to verify your documents for ABC University's undergraduate admission."
      backHref="#/verify/review"
      backLabel="Back to Review"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        <Stepper
          steps={["Review Request", "DigiLocker Auth", "Consent", "Retrieve", "Verify"]}
          currentStep={2}
        />

        {/* Consent Scope Summary */}
        <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
          <h4 className="text-xs uppercase font-extrabold tracking-wider text-[#092F4F] m-0">
            Authorization Scope
          </h4>
          <ul className="space-y-2 text-xs text-slate-700 list-none p-0 m-0">
            <li className="flex items-center gap-2">
              <span className="text-[#14743F] font-bold">✓</span>
              <strong>Requester:</strong> ABC University
            </li>
            <li className="flex items-center gap-2">
              <span className="text-[#14743F] font-bold">✓</span>
              <strong>Purpose:</strong> Undergraduate Admission Eligibility Verification
            </li>
            <li className="flex items-center gap-2">
              <span className="text-[#14743F] font-bold">✓</span>
              <strong>Documents:</strong> Class 10 Certificate & Class 12 Certificate (CBSE)
            </li>
          </ul>
        </div>

        {/* Privacy Options: Zero-Knowledge Predicate Mode */}
        <div className="p-4 bg-[#EBF4FA] border border-[#BAE6FD] rounded-xl space-y-2">
          <label className="flex items-start gap-3 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={zkpMode}
              onChange={(e) => setZkpMode(e.target.checked)}
              className="w-5 h-5 mt-0.5 accent-[#0B5D9B] rounded cursor-pointer"
            />
            <div className="flex-1">
              <span className="text-sm font-bold text-[#092F4F] block">
                Enable Zero-Knowledge Predicate Assertion (Recommended)
              </span>
              <p className="text-xs text-slate-600 mt-0.5 mb-0 leading-relaxed">
                Shares a cryptographic proof that you meet the <em>&gt;= 60.0%</em> criteria without exposing your entire marksheet or subject breakdown.
              </p>
            </div>
          </label>
        </div>

        {/* Consent Validity Duration */}
        <div className="space-y-1.5">
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-600">
            Consent Validity Duration
          </label>
          <select
            value={durationHours}
            onChange={(e) => setDurationHours(Number(e.target.value))}
            className="w-full min-h-[42px] px-3 py-2 text-sm text-[#092F4F] bg-white border border-[#CBD5E1] rounded-xl focus:border-[#0B5D9B] focus:ring-2 focus:ring-[#0B5D9B]/20"
          >
            <option value={24}>24 Hours (Standard)</option>
            <option value={72}>72 Hours</option>
            <option value={168}>7 Days</option>
            <option value={1}>Single-use / 1 Hour</option>
          </select>
        </div>

        {/* Mandatory Explicit Consent Checkbox */}
        <label className="flex items-start gap-3 p-3.5 bg-white border-2 border-[#CBD5E1] rounded-xl cursor-pointer select-none hover:border-[#0B5D9B] transition-colors">
          <input
            type="checkbox"
            checked={consentChecked}
            onChange={(e) => setConsentChecked(e.target.checked)}
            className="w-5 h-5 mt-0.5 accent-[#0B5D9B] rounded cursor-pointer"
            required
          />
          <span className="text-xs font-semibold text-[#092F4F] leading-relaxed">
            I understand and give explicit, purpose-limited consent for DigiIn to verify the requested document claims with official registries for this admission application.
          </span>
        </label>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 pt-2">
          <Button
            variant="primary"
            size="lg"
            type="submit"
            className="flex-1"
            disabled={!consentChecked}
          >
            Grant Consent & Retrieve Records →
          </Button>

          <Button
            variant="secondary"
            size="lg"
            type="button"
            onClick={onDecline}
          >
            Decline
          </Button>
        </div>
      </form>
    </FormPage>
  );
};
