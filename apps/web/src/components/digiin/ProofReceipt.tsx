import React from "react";

export interface ProofReceiptProps {
  claimTitle: string;
  issuerName: string;
  sharedWith: string;
  passingYear?: string | number;
  proofToken: string;
  timestamp: string;
  algorithm?: string;
  onDownloadReceipt: () => void;
  onDone: () => void;
  onViewQr?: () => void;
}

export const ProofReceipt: React.FC<ProofReceiptProps> = ({
  claimTitle,
  issuerName,
  sharedWith,
  passingYear,
  proofToken,
  timestamp,
  algorithm = "Ed25519 (EdDSA)",
  onDownloadReceipt,
  onDone,
  onViewQr,
}) => {
  return (
    <div className="proof-receipt-card rounded-2xl border border-emerald-300 bg-white p-6 shadow-lg text-center" role="region" aria-label="Cryptographic Verification Receipt">
      <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-emerald-100 text-emerald-700 text-3xl font-extrabold shadow-xs">
        ✓
      </div>

      <span className="inline-block rounded-full bg-emerald-50 px-3 py-1 text-xs font-extrabold uppercase tracking-wider text-emerald-800 border border-emerald-200 mb-2">
        🛡️ Verification Complete
      </span>
      <h3 className="text-xl font-extrabold text-slate-900 mb-1">{claimTitle}</h3>
      <p className="text-xs text-slate-500 font-medium mb-6">Signed by {issuerName}</p>

      <div className="text-left rounded-xl bg-slate-50 p-4 border border-slate-200 text-xs space-y-2 mb-6 font-mono">
        <div className="flex justify-between">
          <span className="font-sans text-slate-500">Issuer Authority:</span>
          <strong className="text-slate-800">{issuerName}</strong>
        </div>
        {passingYear && (
          <div className="flex justify-between">
            <span className="font-sans text-slate-500">Passing Year:</span>
            <strong className="text-slate-800">{passingYear}</strong>
          </div>
        )}
        <div className="flex justify-between">
          <span className="font-sans text-slate-500">Shared With:</span>
          <strong className="text-blue-700">{sharedWith}</strong>
        </div>
        <div className="flex justify-between">
          <span className="font-sans text-slate-500">Signature Alg:</span>
          <strong className="text-slate-800">{algorithm}</strong>
        </div>
        <div className="flex justify-between">
          <span className="font-sans text-slate-500">Timestamp:</span>
          <span className="text-slate-600">{timestamp}</span>
        </div>
        <div className="pt-2 border-t border-slate-200">
          <span className="font-sans text-slate-500 block mb-1">JWS Compact Token:</span>
          <code className="block bg-white p-2 rounded border border-slate-200 text-[10px] text-slate-700 break-all select-all">
            {proofToken.slice(0, 80)}...
          </code>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        {onViewQr && (
          <button
            type="button"
            onClick={onViewQr}
            className="flex-1 py-2.5 px-4 rounded-xl text-xs font-bold text-blue-800 bg-blue-50 hover:bg-blue-100 border border-blue-200 transition-all cursor-pointer"
          >
            📱 View QR
          </button>
        )}
        <button
          type="button"
          onClick={onDownloadReceipt}
          className="flex-1 py-2.5 px-4 rounded-xl text-xs font-bold text-slate-800 bg-slate-100 hover:bg-slate-200 border border-slate-300 transition-all cursor-pointer"
        >
          💾 Download Receipt
        </button>
        <button
          type="button"
          onClick={onDone}
          className="flex-1 py-2.5 px-4 rounded-xl text-xs font-bold text-white bg-[#0B5D9B] hover:bg-[#084B7D] active:scale-98 transition-all cursor-pointer shadow-xs"
        >
          ✓ Done
        </button>
      </div>
    </div>
  );
};
