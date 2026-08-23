import React from "react";
import { FormPage } from "../../patterns/FormPage";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { Alert } from "../../components/ui/Alert";
import { Stepper } from "../../components/ui/ProgressIndicator";

interface DocumentsReadyViewProps {
  onExecuteVerification: () => void;
  onCancel: () => void;
}

export const DocumentsReadyView: React.FC<DocumentsReadyViewProps> = ({
  onExecuteVerification,
  onCancel,
}) => {
  return (
    <FormPage
      title="Documents Ready for Verification"
      description="2 of 2 requested credentials have been retrieved and validated at source."
      backHref="#/verify/consent"
      backLabel="Cancel"
    >
      <div className="space-y-6">
        <Stepper
          steps={["Review Request", "DigiLocker Auth", "Consent", "Retrieve", "Verify"]}
          currentStep={4}
        />

        <div className="space-y-3">
          <div className="p-4 bg-white border border-emerald-300 rounded-xl shadow-xs flex items-start justify-between gap-3">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <h4 className="text-sm font-bold text-[#092F4F] m-0">Class 10 Certificate</h4>
                <Badge variant="success" size="sm">✓ Level 4 (Gov Verified)</Badge>
              </div>
              <p className="text-xs text-slate-500 m-0">Central Board of Secondary Education (CBSE)</p>
              <div className="text-[11px] text-emerald-700 font-medium">
                ✓ Date of birth verified • Roll Number match 100%
              </div>
            </div>
            <div className="w-8 h-8 rounded-full bg-[#DFF6E8] text-[#14743F] flex items-center justify-center font-bold text-sm shrink-0">
              ✓
            </div>
          </div>

          <div className="p-4 bg-white border border-emerald-300 rounded-xl shadow-xs flex items-start justify-between gap-3">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <h4 className="text-sm font-bold text-[#092F4F] m-0">Class 12 Certificate</h4>
                <Badge variant="success" size="sm">✓ Level 4 (Gov Verified)</Badge>
              </div>
              <p className="text-xs text-slate-500 m-0">Central Board of Secondary Education (CBSE)</p>
              <div className="text-[11px] text-emerald-700 font-medium">
                ✓ Passing year verified • Aggregate &gt;= 60.0% satisfied (ZKP Assertion)
              </div>
            </div>
            <div className="w-8 h-8 rounded-full bg-[#DFF6E8] text-[#14743F] flex items-center justify-center font-bold text-sm shrink-0">
              ✓
            </div>
          </div>
        </div>

        <Alert type="success" title="Source Registries Verified">
          Digital signatures from CBSE have been verified. No raw files will be transferred to ABC University; only a cryptographic proof token will be generated.
        </Alert>

        <div className="flex flex-col sm:flex-row gap-3 pt-2">
          <Button
            variant="primary"
            size="lg"
            className="flex-1"
            onClick={onExecuteVerification}
          >
            Generate Signed Proof & Complete →
          </Button>

          <Button
            variant="secondary"
            size="lg"
            onClick={onCancel}
          >
            Cancel
          </Button>
        </div>
      </div>
    </FormPage>
  );
};
