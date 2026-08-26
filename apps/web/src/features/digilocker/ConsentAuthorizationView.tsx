import React, { useState, useEffect } from "react";
import { Button } from "../../components/ui/Button";

interface ConsentAuthorizationViewProps {
  onAuthorize: (options: { zkpMode: boolean; durationHours: number }) => void;
  onDecline: () => void;
}

export const ConsentAuthorizationView: React.FC<ConsentAuthorizationViewProps> = ({
  onAuthorize,
  onDecline,
}) => {
  const [step, setStep] = useState<"request" | "confirmation" | "processing">("request");
  const [processingStage, setProcessingStage] = useState(1);

  useEffect(() => {
    if (step === "processing") {
      const t1 = setTimeout(() => setProcessingStage(2), 500);
      const t2 = setTimeout(() => setProcessingStage(3), 1000);
      const t3 = setTimeout(() => {
        onAuthorize({ zkpMode: true, durationHours: 24 });
      }, 1500);
      return () => {
        clearTimeout(t1);
        clearTimeout(t2);
        clearTimeout(t3);
      };
    }
  }, [step, onAuthorize]);

  // Step 3: Processing Screen
  if (step === "processing") {
    return (
      <div className="max-w-md mx-auto py-12 text-center space-y-6">
        <div className="w-16 h-16 rounded-full bg-blue-50 text-[#0B5D9B] text-2xl flex items-center justify-center mx-auto animate-pulse">
          🛡️
        </div>
        <div className="space-y-1">
          <h2 className="text-2xl font-extrabold text-[#092F4F] m-0">Verifying</h2>
          <p className="text-xs sm:text-sm text-slate-500 m-0">
            Checking your credential and generating a secure proof.
          </p>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-2xs space-y-3 text-left text-xs font-semibold">
          <div className="flex items-center gap-2.5 text-emerald-800">
            <span>✓</span>
            <span>Request accepted</span>
          </div>
          <div className={`flex items-center gap-2.5 ${processingStage >= 2 ? "text-emerald-800" : "text-slate-400"}`}>
            <span>{processingStage >= 2 ? "✓" : "○"}</span>
            <span>Credential checked against CBSE</span>
          </div>
          <div className={`flex items-center gap-2.5 ${processingStage >= 3 ? "text-emerald-800" : "text-[#0B5D9B]"}`}>
            <span>{processingStage >= 3 ? "✓" : "⟳"}</span>
            <span>Generating single-use proof token</span>
          </div>
        </div>
      </div>
    );
  }

  // Step 2: Confirmation Dialog Screen
  if (step === "confirmation") {
    return (
      <div className="max-w-xl mx-auto py-6 space-y-6">
        <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-xs space-y-6">
          <div className="space-y-1 border-b border-slate-100 pb-4">
            <span className="text-xs uppercase font-extrabold tracking-wider text-[#0B5D9B]">
              Step 2 of 2
            </span>
            <h1 className="text-2xl font-extrabold text-[#092F4F] m-0">
              Review before sharing
            </h1>
            <p className="text-xs text-slate-500 m-0">
              Please confirm the exact claims that will be cryptographically attested.
            </p>
          </div>

          <div className="space-y-4 text-xs">
            <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl space-y-1.5 text-emerald-950">
              <div className="font-bold text-emerald-900">You will share:</div>
              <ul className="list-disc pl-4 space-y-0.5 m-0 text-emerald-900 font-medium">
                <li>Qualification (Class XII)</li>
                <li>Passing year (2026)</li>
                <li>With: <strong>NTA</strong></li>
                <li>Purpose: <strong>JEE application</strong></li>
              </ul>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5 text-slate-700">
              <div className="font-bold text-slate-800">What will NOT be shared:</div>
              <p className="m-0 leading-relaxed text-slate-600">
                Your original physical PDF document, subject marksheets, residential address, or other personal data will not be transmitted.
              </p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 pt-2 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setStep("request")}
              className="px-5 py-2.5 rounded-xl border border-slate-300 text-xs font-bold text-slate-700 hover:bg-slate-50 cursor-pointer"
            >
              Back
            </button>
            <Button
              variant="primary"
              size="md"
              onClick={() => setStep("processing")}
              className="flex-1 shadow-sm font-bold text-xs cursor-pointer"
            >
              Confirm and verify →
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Step 1: Verification Request Screen (Answers Who? What? Why? How long?)
  return (
    <div className="max-w-xl mx-auto py-6 space-y-6">
      <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-xs space-y-6">
        <div className="flex items-start justify-between border-b border-slate-100 pb-4">
          <div className="space-y-1">
            <span className="text-xs uppercase font-extrabold tracking-wider text-amber-700 bg-amber-50 px-2.5 py-0.5 rounded-full border border-amber-200">
              Verification Request
            </span>
            <h1 className="text-2xl font-extrabold text-[#092F4F] m-0">
              NTA wants to verify your credentials
            </h1>
            <p className="text-xs text-slate-500 m-0">
              Expires in <strong className="text-amber-800">14 minutes</strong>
            </p>
          </div>
        </div>

        {/* 4 Questions Summary */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-0.5">
            <span className="text-slate-400 font-semibold uppercase text-[10px]">Who?</span>
            <div className="font-bold text-[#092F4F]">National Testing Agency (NTA)</div>
          </div>

          <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-0.5">
            <span className="text-slate-400 font-semibold uppercase text-[10px]">What?</span>
            <div className="font-bold text-[#092F4F]">Class XII Qualification</div>
          </div>

          <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-0.5">
            <span className="text-slate-400 font-semibold uppercase text-[10px]">Why?</span>
            <div className="font-bold text-[#092F4F]">JEE Admissions 2026</div>
          </div>

          <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-0.5">
            <span className="text-slate-400 font-semibold uppercase text-[10px]">How long?</span>
            <div className="font-bold text-amber-800">Single-use proof (15 min)</div>
          </div>
        </div>

        {/* Breakdown */}
        <div className="space-y-3 text-xs">
          <div className="p-3.5 bg-blue-50/70 border border-blue-200 rounded-xl space-y-1">
            <div className="font-bold text-[#092F4F]">Requested information:</div>
            <div className="flex items-center gap-4 text-slate-700">
              <span>✓ Qualification</span>
              <span>✓ Passing year (2026)</span>
            </div>
          </div>

          <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
            <div className="font-bold text-slate-700">Not requested:</div>
            <div className="text-slate-500">
              Original PDF file · Subject marks · Residential address
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 pt-2 border-t border-slate-100">
          <button
            type="button"
            onClick={onDecline}
            className="px-5 py-2.5 rounded-xl border border-slate-300 text-xs font-bold text-slate-700 hover:bg-slate-50 cursor-pointer"
          >
            Decline
          </button>
          <Button
            variant="primary"
            size="md"
            onClick={() => setStep("confirmation")}
            className="flex-1 shadow-sm font-bold text-xs cursor-pointer"
          >
            Allow verification →
          </Button>
        </div>
      </div>
    </div>
  );
};
