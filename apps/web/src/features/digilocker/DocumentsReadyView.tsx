import React from "react";
import { Button } from "../../components/ui/Button";

interface DocumentsReadyViewProps {
  onExecuteVerification: () => void;
  onCancel: () => void;
}

export const DocumentsReadyView: React.FC<DocumentsReadyViewProps> = ({
  onExecuteVerification,
  onCancel,
}) => {
  return (
    <div className="max-w-xl mx-auto py-6 space-y-6">
      <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-xs space-y-6">
        {/* Unmistakable Success State */}
        <div className="text-center space-y-2 border-b border-slate-100 pb-5">
          <div className="w-14 h-14 rounded-full bg-emerald-50 text-emerald-800 text-2xl flex items-center justify-center mx-auto border border-emerald-300">
            ✓
          </div>
          <h1 className="text-2xl font-extrabold text-[#092F4F] m-0">
            Verified
          </h1>
          <p className="text-xs text-slate-500 m-0">
            Proof generated 26 Aug 2026 · 15:51
          </p>
        </div>

        {/* Verification Summary Card */}
        <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl space-y-2.5 text-xs">
          <div className="flex justify-between py-1 border-b border-slate-200">
            <span className="text-slate-500">Qualification:</span>
            <strong className="text-[#092F4F]">Class XII Qualification</strong>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-200">
            <span className="text-slate-500">Issued by:</span>
            <strong className="text-[#092F4F]">CBSE</strong>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-200">
            <span className="text-slate-500">Verified for:</span>
            <strong className="text-[#092F4F]">NTA</strong>
          </div>
          <div className="flex justify-between py-1">
            <span className="text-slate-500">Passing year:</span>
            <strong className="text-[#092F4F]">2026</strong>
          </div>
        </div>

        {/* Proof Token Box */}
        <div className="p-3.5 bg-slate-900 text-slate-300 rounded-xl font-mono text-[11px] space-y-1">
          <div className="text-slate-400 text-[10px]">JWS PROOF TOKEN (Ed25519)</div>
          <div className="text-cyan-300 break-all">
            eyJhbGciOiJFZERTQSI...8f9a2b1c4e7d0f3a6b5c8e9d2a4f7b0e
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 pt-2">
          <Button
            variant="primary"
            size="md"
            className="flex-1 font-bold text-xs shadow-sm cursor-pointer"
            onClick={onExecuteVerification}
          >
            View proof →
          </Button>

          <Button
            variant="secondary"
            size="md"
            onClick={onCancel}
            className="font-bold text-xs cursor-pointer"
          >
            Done
          </Button>
        </div>
      </div>
    </div>
  );
};
