import React, { useState } from "react";
import { Badge } from "./Badge";
import { Button } from "./Button";

export interface ShareVerificationCardProps {
  verificationId?: string;
  verifierName?: string;
  verifiedDate?: string;
  documentsCount?: string;
  onDashboardClick?: () => void;
  className?: string;
}

export const ShareVerificationCard: React.FC<ShareVerificationCardProps> = ({
  verificationId = "DIN-VRF-82A91",
  verifierName = "ABC University Admissions",
  verifiedDate = "23 Aug 2026, 10:30 IST",
  documentsCount = "3 of 3",
  onDashboardClick,
  className = "",
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(`DigiIn Verification Receipt: ${verificationId}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className={`bg-white border border-[#CBD5E1] rounded-2xl p-6 md:p-8 shadow-sm text-center space-y-6 ${className}`}>
      <div className="w-16 h-16 rounded-full bg-[#DFF6E8] text-[#14743F] text-3xl font-extrabold flex items-center justify-center mx-auto shadow-sm">
        ✓
      </div>

      <div className="space-y-1">
        <Badge variant="success" size="sm">Level 4 • Source Verified</Badge>
        <h2 className="text-2xl font-bold text-[#092F4F] m-0">Verification Complete</h2>
        <p className="text-sm text-slate-600 m-0">
          {documentsCount} requested documents were successfully validated against official issuing authorities.
        </p>
      </div>

      <div className="bg-[#F8FAFC] border border-[#CBD5E1] rounded-xl p-5 text-left space-y-3 text-xs">
        <div className="flex justify-between items-center">
          <span className="text-slate-500">Verification ID:</span>
          <code className="text-sm font-bold font-mono text-[#092F4F] bg-white px-2 py-0.5 rounded border border-slate-300">
            {verificationId}
          </code>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-slate-500">Verified For:</span>
          <strong className="text-slate-800">{verifierName}</strong>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-slate-500">Timestamp:</span>
          <strong className="text-slate-800">{verifiedDate}</strong>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
        {onDashboardClick && (
          <Button variant="primary" onClick={onDashboardClick}>
            Go to Dashboard
          </Button>
        )}
        <Button variant="secondary" onClick={handleCopy}>
          {copied ? "✓ Proof Reference Copied" : "Copy Proof Reference"}
        </Button>
      </div>

      {copied && (
        <p className="text-xs font-semibold text-emerald-700 m-0" role="status">
          ✓ Copied to clipboard! Share this reference with {verifierName}.
        </p>
      )}
    </div>
  );
};
