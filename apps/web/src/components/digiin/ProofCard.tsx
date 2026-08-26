import React from "react";
import { Button } from "../ui/Button";

export interface ProofCardProps {
  claimTitle: string;
  issuer: string;
  verifiedFor: string;
  status?: "Valid" | "Expired" | "Revoked";
  createdDate: string;
  onViewProof: () => void;
  onDownloadReceipt?: () => void;
  className?: string;
}

export const ProofCard: React.FC<ProofCardProps> = ({
  claimTitle,
  issuer,
  verifiedFor,
  status = "Valid",
  createdDate,
  onViewProof,
  onDownloadReceipt,
  className = "",
}) => {
  return (
    <div
      className={`bg-white border border-slate-200 rounded-2xl p-5 shadow-2xs space-y-4 ${className}`}
    >
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-extrabold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-300">
          ✓ {status} proof
        </span>
        <span className="text-[11px] text-slate-400 font-mono">
          {createdDate}
        </span>
      </div>

      <div className="space-y-1">
        <h3 className="text-base font-bold text-[#092F4F] m-0">
          {claimTitle}
        </h3>
        <div className="text-xs text-slate-500 space-y-0.5">
          <div>Issuer: <strong className="text-slate-700">{issuer}</strong></div>
          <div>Verified for: <strong className="text-slate-700">{verifiedFor}</strong></div>
        </div>
      </div>

      <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
        {onDownloadReceipt && (
          <Button
            variant="secondary"
            size="sm"
            onClick={onDownloadReceipt}
            className="text-xs font-bold cursor-pointer"
          >
            Download receipt
          </Button>
        )}
        <Button
          variant="primary"
          size="sm"
          onClick={onViewProof}
          className="text-xs font-bold shadow-xs cursor-pointer"
        >
          View proof →
        </Button>
      </div>
    </div>
  );
};
