import React from "react";
import { FormPage } from "../../patterns/FormPage";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Alert } from "../../components/ui/Alert";
import { Stepper } from "../../components/ui/ProgressIndicator";

interface VerificationRequestReviewViewProps {
  onContinue: () => void;
  onDecline: () => void;
}

export const VerificationRequestReviewView: React.FC<VerificationRequestReviewViewProps> = ({
  onContinue,
  onDecline,
}) => {
  return (
    <FormPage
      title="Verification Request"
      description="Review the requesting organisation and the specific documents required before connecting your records."
      backHref="#/dashboard"
      backLabel="Back to Dashboard"
    >
      <div className="space-y-6">
        <Stepper
          steps={["Review Request", "DigiLocker Auth", "Consent", "Retrieve", "Verify"]}
          currentStep={0}
        />

        {/* Organization Identity Header */}
        <div className="p-4 bg-[#EBF4FA] border border-[#BAE6FD] rounded-xl flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-[#0B5D9B] text-white flex items-center justify-center font-extrabold text-xl shadow-xs">
              AU
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-[#092F4F] m-0">ABC University</h3>
                <Badge variant="success" size="sm">✓ Accredited Institution</Badge>
              </div>
              <p className="text-xs text-slate-600 m-0">
                Undergraduate Admission Eligibility Verification (AY 2026-27)
              </p>
            </div>
          </div>
        </div>

        {/* Itemized Requested Documents */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold uppercase tracking-wider text-[#092F4F] m-0">
              Requested Documents (2)
            </h4>
            <span className="text-xs text-slate-500 font-semibold">Purpose: Eligibility</span>
          </div>

          <div className="space-y-2">
            <div className="p-3.5 bg-white border border-[#CBD5E1] rounded-xl flex items-start justify-between gap-3">
              <div>
                <h5 className="text-sm font-bold text-[#092F4F] m-0">Class 10 Certificate</h5>
                <p className="text-xs text-slate-500 m-0">Central Board of Secondary Education (CBSE)</p>
                <div className="text-[11px] text-slate-600 mt-1">
                  Required claims: <em>Date of birth, Secondary completion status</em>
                </div>
              </div>
              <Badge variant="info">Requested</Badge>
            </div>

            <div className="p-3.5 bg-white border border-[#CBD5E1] rounded-xl flex items-start justify-between gap-3">
              <div>
                <h5 className="text-sm font-bold text-[#092F4F] m-0">Class 12 Certificate</h5>
                <p className="text-xs text-slate-500 m-0">Central Board of Secondary Education (CBSE)</p>
                <div className="text-[11px] text-slate-600 mt-1">
                  Required claims: <em>Passing year, Aggregate Percentage &gt;= 60.0%</em>
                </div>
              </div>
              <Badge variant="info">Requested</Badge>
            </div>
          </div>
        </div>

        <Alert type="info" title="Zero Raw Document Retention">
          Connecting to DigiLocker will allow DigiIn to verify the requested attributes at the source registry. ABC University will receive a mathematical proof assertion without storing your raw certificates.
        </Alert>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 pt-2">
          <Button
            variant="primary"
            size="lg"
            className="flex-1"
            onClick={onContinue}
          >
            Connect DigiLocker & Continue →
          </Button>

          <Button
            variant="secondary"
            size="lg"
            onClick={onDecline}
          >
            Decline Request
          </Button>
        </div>
      </div>
    </FormPage>
  );
};
