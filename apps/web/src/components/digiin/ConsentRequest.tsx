import React from "react";

export interface ConsentRequestProps {
  requesterName: string;
  purpose: string;
  audience: string;
  expiresInMinutes?: number;
  attributes: Array<{ name: string; label: string; required?: boolean; selected: boolean }>;
  onToggleAttribute: (name: string) => void;
  isPredicateOnly: boolean;
  onTogglePredicateOnly: (val: boolean) => void;
  onAllow: () => void;
  onDecline: () => void;
  isLoading?: boolean;
}

export const ConsentRequest: React.FC<ConsentRequestProps> = ({
  requesterName,
  purpose,
  expiresInMinutes = 15,
  attributes,
  onToggleAttribute,
  isPredicateOnly,
  onTogglePredicateOnly,
  onAllow,
  onDecline,
  isLoading = false,
}) => {
  return (
    <div className="consent-request-box rounded-2xl border border-blue-200 bg-white p-6 shadow-md" role="region" aria-label="Verification Consent Request">
      <div className="flex items-center gap-3 mb-4 pb-4 border-b border-slate-100">
        <div className="h-10 w-10 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xl font-bold">
          🛡️
        </div>
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-blue-700">Inbound Request</span>
          <h3 className="text-lg font-extrabold text-slate-900">{requesterName}</h3>
        </div>
      </div>

      <div className="mb-4 bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2">
        <div>
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">Bounded Purpose:</span>
          <p className="text-sm font-semibold text-slate-800">{purpose}</p>
        </div>
        <div className="flex items-center justify-between text-xs text-slate-600 pt-2 border-t border-slate-200/60">
          <span>⏱️ Single-use validity:</span>
          <strong className="text-blue-800">Expires in {expiresInMinutes} minutes</strong>
        </div>
      </div>

      {/* Privacy Mode Toggle */}
      <div className="mb-5 p-3.5 rounded-xl bg-indigo-50/80 border border-indigo-200">
        <div className="flex items-center justify-between">
          <div>
            <strong className="text-xs font-bold text-indigo-950 block">Zero-Knowledge Predicate Mode</strong>
            <span className="text-xs text-indigo-800">Prove eligibility without sharing raw DOB or full marks</span>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={isPredicateOnly}
            onClick={() => onTogglePredicateOnly(!isPredicateOnly)}
            className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors ${
              isPredicateOnly ? "bg-indigo-700" : "bg-slate-300"
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-sm transition ${
                isPredicateOnly ? "translate-x-5" : "translate-x-0"
              }`}
            />
          </button>
        </div>
      </div>

      {/* Attributes Checklist */}
      <div className="mb-6">
        <span className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-2">
          Requested Credential Claims:
        </span>
        <div className="space-y-2">
          {attributes.map((attr) => (
            <label
              key={attr.name}
              className={`flex items-center justify-between p-3 rounded-xl border transition-all cursor-pointer ${
                attr.selected ? "bg-blue-50/60 border-blue-300 text-blue-950" : "bg-white border-slate-200 text-slate-600"
              }`}
            >
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={attr.selected}
                  onChange={() => onToggleAttribute(attr.name)}
                  disabled={attr.required}
                  className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-semibold">{attr.label}</span>
              </div>
              {attr.required && (
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-200 text-slate-700">
                  Required
                </span>
              )}
            </label>
          ))}
        </div>
      </div>

      {/* Sovereign Privacy Guarantee Banner */}
      <div className="mb-6 rounded-xl bg-emerald-50 p-3.5 border border-emerald-200 text-xs text-emerald-900 flex items-start gap-2.5">
        <span className="text-base">ℹ️</span>
        <div>
          <strong>Zero Raw File Transfer:</strong> Your original document PDF is never downloaded or transferred. Only cryptographic mathematical assertions are issued.
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-3 pt-2">
        <button
          type="button"
          onClick={onDecline}
          disabled={isLoading}
          className="flex-1 py-2.5 px-4 rounded-xl text-sm font-bold text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 transition-all cursor-pointer"
        >
          Decline Request
        </button>
        <button
          type="button"
          onClick={onAllow}
          disabled={isLoading}
          className="flex-2 py-2.5 px-4 rounded-xl text-sm font-bold text-white bg-[#0B5D9B] hover:bg-[#084B7D] active:scale-98 shadow-sm transition-all cursor-pointer"
        >
          {isLoading ? "Authorizing Proof..." : "Allow Verification Proof &rarr;"}
        </button>
      </div>
    </div>
  );
};
