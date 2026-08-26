import React from "react";
import { Button } from "../ui/Button";

export interface VerificationCardProps {
  requester: string;
  claimTitle: string;
  purpose: string;
  expiresIn: string;
  onReview: () => void;
  className?: string;
}

export const VerificationCard: React.FC<VerificationCardProps> = ({
  requester,
  claimTitle,
  purpose,
  expiresIn,
  onReview,
  className = "",
}) => {
  return (
    <div
      className={`bg-white border border-slate-200 rounded-2xl p-5 shadow-2xs hover:border-[#0B5D9B] hover:shadow-xs transition-all space-y-4 ${className}`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
          {requester}
        </span>
        <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200">
          Expires in {expiresIn}
        </span>
      </div>

      <div className="space-y-1">
        <h3 className="text-base font-bold text-[#092F4F] m-0">
          {claimTitle}
        </h3>
        <p className="text-xs text-slate-500 m-0">
          Purpose: <strong>{purpose}</strong>
        </p>
      </div>

      <div className="pt-2 border-t border-slate-100 flex items-center justify-end">
        <Button
          variant="primary"
          size="sm"
          onClick={onReview}
          className="font-bold text-xs shadow-xs cursor-pointer"
        >
          Review request →
        </Button>
      </div>
    </div>
  );
};
