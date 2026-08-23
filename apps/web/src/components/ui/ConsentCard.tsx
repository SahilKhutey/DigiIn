import React, { useState } from "react";
import { Badge } from "./Badge";
import { Button } from "./Button";
import { Alert } from "./Alert";

export interface RequestedDoc {
  name: string;
  purpose: string;
  authority: string;
}

export interface ConsentCardProps {
  requesterName: string;
  purpose: string;
  documents: RequestedDoc[];
  onConsent: (zkpMode: boolean) => void;
  onCancel?: () => void;
  className?: string;
}

export const ConsentCard: React.FC<ConsentCardProps> = ({
  requesterName,
  purpose,
  documents,
  onConsent,
  onCancel,
  className = "",
}) => {
  const [zkpMode, setZkpMode] = useState(true);
  const [agreed, setAgreed] = useState(false);

  return (
    <div className={`bg-white border border-[#CBD5E1] rounded-2xl p-6 shadow-sm space-y-6 ${className}`}>
      <div className="border-b border-slate-200 pb-4 space-y-1">
        <Badge variant="warning" size="sm">Informed Consent Authorization</Badge>
        <h3 className="text-xl font-bold text-[#092F4F] m-0">Authorize Document Sharing</h3>
        <p className="text-sm text-slate-600 m-0">
          <strong>{requesterName}</strong> is requesting verified credentials for <strong>{purpose}</strong>.
        </p>
      </div>

      <div className="space-y-3">
        <h4 className="text-xs uppercase font-extrabold tracking-wider text-slate-500 m-0">
          Requested Credentials ({documents.length})
        </h4>
        <div className="space-y-2">
          {documents.map((doc, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-3.5 bg-slate-50 border border-slate-200 rounded-xl"
            >
              <div>
                <strong className="text-sm text-[#092F4F] block">{doc.name}</strong>
                <span className="text-xs text-slate-500">{doc.purpose}</span>
              </div>
              <Badge variant="info" size="sm">{doc.authority}</Badge>
            </div>
          ))}
        </div>
      </div>

      <Alert type="info" title="Zero-Knowledge Minimum Disclosure Protection">
        Only mathematical assertions will be shared. Your unredacted certificates and personal address are never disclosed.
      </Alert>

      <div className="border border-[#CBD5E1] rounded-xl p-4 flex items-center justify-between gap-4 bg-white">
        <div>
          <strong className="text-sm text-[#092F4F] block">Zero-Knowledge Proof (ZKP) Mode</strong>
          <span className="text-xs text-slate-500">Share verifiable predicates (e.g. aggregate &gt;= 60%) instead of raw marks.</span>
        </div>
        <input
          type="checkbox"
          checked={zkpMode}
          onChange={(e) => setZkpMode(e.target.checked)}
          className="w-5 h-5 accent-[#0B5D9B] cursor-pointer"
        />
      </div>

      <label className="flex items-start gap-3 p-4 rounded-xl bg-[#EBF4FA] border border-[#BAE6FD] cursor-pointer">
        <input
          type="checkbox"
          checked={agreed}
          onChange={(e) => setAgreed(e.target.checked)}
          className="w-5 h-5 accent-[#0B5D9B] mt-0.5 cursor-pointer"
        />
        <span className="text-xs text-[#0A6990] leading-relaxed">
          <strong>I give explicit consent</strong> for DigiIn to verify these credentials against official government issuers and share proof tokens with {requesterName}.
        </span>
      </label>

      <div className="flex items-center justify-between gap-4 pt-3 border-t border-slate-200">
        {onCancel && (
          <Button variant="secondary" onClick={onCancel}>
            ← Cancel / Back
          </Button>
        )}
        <Button
          variant="primary"
          size="lg"
          disabled={!agreed}
          onClick={() => onConsent(zkpMode)}
        >
          Authorize & Give Consent →
        </Button>
      </div>
    </div>
  );
};
