import React from "react";
import { TrustBadge } from "./TrustBadge";

export interface CredentialCardProps {
  id: string;
  title: string;
  issuer: string;
  level: number;
  issuedDate: string;
  status?: "ACTIVE" | "REVOKED" | "EXPIRED" | "PENDING";
  sha256?: string;
  onView?: () => void;
  onProof?: () => void;
  onShare?: () => void;
}

export const CredentialCard: React.FC<CredentialCardProps> = ({
  title,
  issuer,
  level,
  issuedDate,
  status = "ACTIVE",
  sha256,
  onView,
  onProof,
  onShare,
}) => {
  return (
    <article className="credential-card flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-6 shadow-xs transition-all hover:border-blue-400 hover:shadow-md">
      <div>
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex-1">
            <h3 className="text-base font-bold text-slate-900 leading-snug">{title}</h3>
            <p className="text-xs text-slate-500 font-medium mt-0.5">🏛️ {issuer}</p>
          </div>
          <TrustBadge level={level} size="sm" />
        </div>

        <div className="my-3 space-y-1.5 text-xs text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100">
          <div className="flex justify-between">
            <span className="text-slate-500">Issued Date:</span>
            <span className="font-semibold text-slate-800">{issuedDate}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Status:</span>
            <span className={`font-bold ${status === "ACTIVE" ? "text-emerald-700" : "text-rose-700"}`}>
              {status}
            </span>
          </div>
          {sha256 && (
            <div className="flex justify-between font-mono">
              <span className="text-slate-500">Hash:</span>
              <span className="text-slate-700 truncate max-w-[140px]">{sha256.slice(0, 16)}...</span>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2 pt-3 border-t border-slate-100">
        {onView && (
          <button
            type="button"
            onClick={onView}
            className="flex-1 px-3 py-1.5 rounded-lg text-xs font-bold text-[#0B5D9B] bg-blue-50 hover:bg-blue-100 transition-all cursor-pointer"
          >
            View
          </button>
        )}
        {onProof && (
          <button
            type="button"
            onClick={onProof}
            className="flex-1 px-3 py-1.5 rounded-lg text-xs font-bold text-white bg-[#0B5D9B] hover:bg-[#084B7D] transition-all cursor-pointer shadow-2xs"
          >
            Create Proof
          </button>
        )}
        {onShare && (
          <button
            type="button"
            onClick={onShare}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 transition-all cursor-pointer"
          >
            Share
          </button>
        )}
      </div>
    </article>
  );
};
