import React, { useEffect, useState } from "react";
import { FormPage } from "../../patterns/FormPage";
import { Stepper, ProgressIndicator } from "../../components/ui/ProgressIndicator";
import { digiLockerService } from "../../services/digilocker/digilockerService";
import { RetrievalProgressStep } from "../../services/digilocker/digilockerTypes";

interface DocumentRetrievalProgressViewProps {
  onComplete: () => void;
}

export const DocumentRetrievalProgressView: React.FC<DocumentRetrievalProgressViewProps> = ({
  onComplete,
}) => {
  const [progress, setProgress] = useState<RetrievalProgressStep>({
    step: "CONNECTING",
    percent: 10,
    message: "Initiating secure connection to DigiLocker gateway...",
  });

  useEffect(() => {
    let isMounted = true;
    digiLockerService.retrieveDocuments("req_abc_univ_2026", (p) => {
      if (isMounted) {
        setProgress(p);
      }
    }).then(() => {
      if (isMounted) {
        setTimeout(onComplete, 600);
      }
    });

    return () => {
      isMounted = false;
    };
  }, [onComplete]);

  return (
    <FormPage
      title="Retrieving Document Records"
      description="Connecting to official government registries to fetch certified digital credential claims."
      backHref="#/verify/consent"
      backLabel="Cancel"
    >
      <div className="space-y-8 py-4">
        <Stepper
          steps={["Review Request", "DigiLocker Auth", "Consent", "Retrieve", "Verify"]}
          currentStep={3}
        />

        <div className="space-y-4 text-center">
          <div className="w-16 h-16 rounded-2xl bg-[#EBF4FA] border-2 border-[#BAE6FD] text-[#0B5D9B] text-2xl font-bold flex items-center justify-center mx-auto shadow-xs animate-pulse">
            ⬇️
          </div>

          <div className="space-y-1">
            <h3 className="text-lg font-bold text-[#092F4F] m-0">
              Fetching from Government Registries
            </h3>
            <p className="text-xs text-slate-600 m-0" aria-live="polite">
              {progress.message}
            </p>
          </div>

          <div className="w-full bg-slate-200 rounded-full h-2.5 overflow-hidden">
            <div
              className="bg-[#0B5D9B] h-2.5 rounded-full transition-all duration-300"
              style={{ width: `${progress.percent}%` }}
            />
          </div>

          <div className="text-[11px] text-slate-400 font-mono">
            Security Status: TLS 1.3 • End-to-End Encrypted Tunnel
          </div>
        </div>
      </div>
    </FormPage>
  );
};
