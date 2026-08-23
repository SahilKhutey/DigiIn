import React, { useState } from "react";

export interface DigiInIDCardProps {
  idNumber?: string;
  holderName?: string;
  status?: string;
  className?: string;
}

export const DigiInIDCard: React.FC<DigiInIDCardProps> = ({
  idNumber = "DIN-84K2-19Q7",
  holderName = "Rahul Sharma",
  status = "Active & Sovereign",
  className = "",
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(idNumber);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`bg-gradient-to-br from-[#092F4F] via-[#0B4F71] to-[#0B5D9B] text-white rounded-2xl p-6 shadow-md relative overflow-hidden ${className}`}>
      <div className="flex justify-between items-start mb-4">
        <div>
          <span className="text-[10px] uppercase font-bold tracking-widest text-slate-300 block">
            Digital Public Infrastructure
          </span>
          <h4 className="text-lg font-bold text-white m-0">DigiIn Sovereign ID</h4>
        </div>
        <div className="text-2xl" aria-hidden="true">🇮🇳</div>
      </div>

      <div className="my-4">
        <span className="text-xs text-slate-300 block">Universal Verification Reference</span>
        <code className="text-2xl font-extrabold font-mono tracking-wider text-cyan-300 block mt-1">
          {idNumber}
        </code>
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-white/20 text-xs">
        <div>
          <span className="text-slate-300 block text-[11px]">Account Status</span>
          <span className="font-bold text-emerald-300 flex items-center gap-1">
            ✓ {status}
          </span>
        </div>

        <button
          type="button"
          onClick={handleCopy}
          className="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white font-bold transition-colors cursor-pointer border border-white/30"
        >
          {copied ? "✓ Copied" : "Copy ID"}
        </button>
      </div>
    </div>
  );
};
