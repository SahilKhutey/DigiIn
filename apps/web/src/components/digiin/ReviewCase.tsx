import React from "react";
import type { VerificationCase, FieldComparison } from "../../types";

export interface ReviewCaseProps {
  caseItem: VerificationCase;
  fieldComparisons?: FieldComparison[];
  onApprove: (caseId: string) => void;
  onReject: (caseId: string) => void;
  onTransfer?: (caseId: string) => void;
  onClarify?: (caseId: string) => void;
}

export const ReviewCase: React.FC<ReviewCaseProps> = ({
  caseItem,
  fieldComparisons = [],
  onApprove,
  onReject,
  onTransfer,
  onClarify,
}) => {
  return (
    <div className="review-case-card rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4 pb-4 border-b border-slate-100">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Case ID: {caseItem.caseId}</span>
          <h3 className="text-lg font-bold text-slate-900">{caseItem.claimedIssuer}</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-extrabold px-2.5 py-1 rounded-full bg-blue-50 text-blue-800 border border-blue-200">
            Score: {caseItem.automatedMatchScore}%
          </span>
          <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-amber-50 text-amber-800 border border-amber-200">
            {caseItem.status}
          </span>
        </div>
      </div>

      {fieldComparisons.length > 0 && (
        <div className="mb-6 overflow-hidden rounded-xl border border-slate-200 text-xs">
          <div className="grid grid-cols-3 bg-slate-50 p-3 font-bold text-slate-600 uppercase border-b border-slate-200">
            <span>Field</span>
            <span>Citizen Upload OCR</span>
            <span>Registry Official Record</span>
          </div>
          <div className="divide-y divide-slate-100">
            {fieldComparisons.map((fc, idx) => (
              <div key={idx} className="grid grid-cols-3 p-3 items-center hover:bg-slate-50/50">
                <span className="font-semibold text-slate-700">{fc.label || fc.field}</span>
                <span className="text-slate-800">{fc.citizenValue}</span>
                <div className="flex items-center justify-between pr-2">
                  <span className="text-slate-900 font-medium">{fc.registryValue}</span>
                  <span className={`font-bold ${fc.isMatch ? "text-emerald-600" : "text-rose-600"}`}>
                    {fc.isMatch ? "✓ MATCH" : "⚠️ DIFF"}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100">
        <button
          type="button"
          onClick={() => onApprove(caseItem.caseId)}
          className="flex-1 py-2 px-3 rounded-xl text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 transition-all cursor-pointer shadow-xs"
        >
          ✓ Approve Verification
        </button>
        <button
          type="button"
          onClick={() => onReject(caseItem.caseId)}
          className="flex-1 py-2 px-3 rounded-xl text-xs font-bold text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 transition-all cursor-pointer"
        >
          ✕ Reject
        </button>
        {onTransfer && (
          <button
            type="button"
            onClick={() => onTransfer(caseItem.caseId)}
            className="py-2 px-3 rounded-xl text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 transition-all cursor-pointer"
          >
            ↗ Transfer Queue
          </button>
        )}
        {onClarify && (
          <button
            type="button"
            onClick={() => onClarify(caseItem.caseId)}
            className="py-2 px-3 rounded-xl text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 transition-all cursor-pointer"
          >
            💬 Request Evidence
          </button>
        )}
      </div>
    </div>
  );
};
