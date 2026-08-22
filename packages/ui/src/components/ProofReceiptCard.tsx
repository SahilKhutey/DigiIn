import React from "react";
import { StatusBadge } from "./StatusBadge";

export interface ProofReceiptCardProps {
  receiptId: string;
  requesterName: string;
  credentialType: string;
  disclosureLevel: string;
  verifiedAt: string;
  expiresAt: string;
  disclosedAttributes?: Record<string, any>;
  predicatesSatisfied?: Array<{ claim: string; expression: string; satisfied: boolean }>;
  documentShared?: boolean;
}

export const ProofReceiptCard: React.FC<ProofReceiptCardProps> = ({
  receiptId,
  requesterName,
  credentialType,
  disclosureLevel,
  verifiedAt,
  expiresAt,
  disclosedAttributes = {},
  predicatesSatisfied = [],
  documentShared = false,
}) => {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Sovereign Proof Receipt
          </span>
          <h3 className="text-base font-bold text-slate-900">{credentialType}</h3>
        </div>
        <StatusBadge status="VERIFIED" size="sm" />
      </div>

      <div className="mt-3 grid grid-cols-2 gap-3 text-xs">
        <div>
          <span className="text-slate-500">Authorized Requester:</span>
          <p className="font-semibold text-slate-800">{requesterName}</p>
        </div>
        <div>
          <span className="text-slate-500">Disclosure Policy:</span>
          <p className="font-semibold text-slate-800">{disclosureLevel}</p>
        </div>
        <div>
          <span className="text-slate-500">Verified Timestamp:</span>
          <p className="font-mono text-slate-700">{verifiedAt.slice(0, 19)}</p>
        </div>
        <div>
          <span className="text-slate-500">Expires At:</span>
          <p className="font-mono text-slate-700">{expiresAt.slice(0, 19)}</p>
        </div>
      </div>

      {predicatesSatisfied.length > 0 && (
        <div className="mt-4 rounded-lg bg-emerald-50 p-3 border border-emerald-100">
          <span className="text-xs font-bold text-emerald-800">
            Zero-Knowledge Predicates Proved (No Raw Data Disclosed)
          </span>
          <ul className="mt-1.5 space-y-1 text-xs text-emerald-700">
            {predicatesSatisfied.map((p, i) => (
              <li key={i} className="flex items-center gap-1.5">
                <span>✓</span>
                <span className="font-mono font-medium">{p.expression}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {Object.keys(disclosedAttributes).length > 0 && (
        <div className="mt-3 rounded-lg bg-slate-50 p-3 border border-slate-100">
          <span className="text-xs font-bold text-slate-700">Disclosed Claim Attributes</span>
          <div className="mt-1.5 grid grid-cols-2 gap-2 text-xs">
            {Object.entries(disclosedAttributes).map(([k, v]) => (
              <div key={k}>
                <span className="text-slate-500">{k}:</span>{" "}
                <span className="font-semibold text-slate-800">{String(v)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3 text-xs text-slate-500">
        <span>Raw File Transfer: {documentShared ? "YES" : "ZERO (0 bytes)"}</span>
        <span className="font-mono text-[10px]">Receipt: {receiptId}</span>
      </div>
    </div>
  );
};
