import React, { useState } from "react";
import { Button } from "../../components/ui";

interface DocumentDetailViewProps {
  documentId: string;
  onBack: () => void;
  onShare: (docId: string) => void;
  onStartCorrection: (docId: string) => void;
  onPrintSupportSheet?: (docId: string) => void;
}

export const DocumentDetailView: React.FC<DocumentDetailViewProps> = ({
  documentId,
  onBack,
  onShare,
  onStartCorrection,
  onPrintSupportSheet,
}) => {
  const [copiedHash, setCopiedHash] = useState(false);

  const doc = {
    id: documentId,
    title: "Class XII Certificate",
    issuer: "CBSE",
    authorityLevel: "Level 4",
    status: "Active",
    issueDate: "15 May 2026",
    candidateName: "Rahul Sharma",
    rollNumber: "26182910",
    school: "Delhi Public School, R.K. Puram",
    sha256Hash: "8f9a2b1c4e7d0f3a6b5c8e9d2a4f7b0e3c6a9d1f5e8b2a4c7d0f3a6b5c8e9d2a",
  };

  const handleCopyHash = () => {
    navigator.clipboard?.writeText(doc.sha256Hash);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto py-2">
      {/* Back button */}
      <div>
        <button
          type="button"
          onClick={onBack}
          className="inline-flex items-center gap-1.5 text-sm font-bold text-[#0B5D9B] hover:underline cursor-pointer"
        >
          ← Documents
        </button>
      </div>

      {/* Main Document Inspection Card */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-2xs space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pb-6 border-b border-slate-100">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="text-xs font-extrabold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-300">
                ✓ Verified
              </span>
              <span className="text-xs font-semibold text-slate-500">
                Status: {doc.status}
              </span>
            </div>

            <h1 className="text-2xl font-extrabold text-[#092F4F] m-0">
              {doc.title}
            </h1>

            <p className="text-xs sm:text-sm text-slate-600 m-0">
              Issuer: <strong>{doc.issuer}</strong> · Issued: <strong>{doc.issueDate}</strong> · Level: <strong>{doc.authorityLevel}</strong>
            </p>
          </div>

          <div className="flex flex-wrap gap-2.5">
            <Button
              variant="primary"
              size="sm"
              onClick={() => onShare(doc.id)}
              className="font-bold shadow-xs cursor-pointer"
            >
              Create proof →
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onShare(doc.id)}
              className="font-bold cursor-pointer"
            >
              Share
            </Button>
          </div>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
            <div className="text-slate-500 font-medium">Candidate Name</div>
            <div className="text-sm font-bold text-[#092F4F]">{doc.candidateName}</div>
          </div>

          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
            <div className="text-slate-500 font-medium">Roll Number</div>
            <div className="text-sm font-mono font-bold text-[#092F4F]">{doc.rollNumber}</div>
          </div>

          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
            <div className="text-slate-500 font-medium">Institution</div>
            <div className="text-sm font-bold text-[#092F4F]">{doc.school}</div>
          </div>

          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
            <div className="text-slate-500 font-medium">Sovereign Account Owner</div>
            <div className="text-sm font-mono font-bold text-[#0B5D9B]">DI-7K4M-9Q2X-8P6R</div>
          </div>

          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-1 sm:col-span-2">
            <div className="text-slate-500 font-medium">Verification Level</div>
            <div className="text-sm font-bold text-emerald-800">{doc.authorityLevel} (Direct Authoritative Registry)</div>
          </div>
        </div>

        {/* Information Panel */}
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl text-xs text-blue-900 flex items-start gap-2.5">
          <span className="text-base">ℹ️</span>
          <div>
            <strong>About verification:</strong> This document was verified against its issuing authority.
          </div>
        </div>

        {/* Cryptographic Provenance */}
        <div className="p-4 bg-slate-900 text-slate-300 rounded-xl space-y-2 font-mono text-xs">
          <div className="flex items-center justify-between text-slate-400 text-[11px]">
            <span>SHA-256 Hash</span>
            <button
              type="button"
              onClick={handleCopyHash}
              className="text-cyan-400 hover:underline cursor-pointer"
            >
              {copiedHash ? "✓ Copied" : "Copy"}
            </button>
          </div>
          <div className="text-[11px] text-cyan-300 break-all">{doc.sha256Hash}</div>
        </div>

        {/* Secondary Report Action */}
        <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
          <button
            type="button"
            onClick={() => onStartCorrection(doc.id)}
            className="text-slate-500 hover:text-red-700 font-semibold cursor-pointer"
          >
            Report a problem
          </button>
          {onPrintSupportSheet && (
            <button
              type="button"
              onClick={() => onPrintSupportSheet(doc.id)}
              className="text-slate-500 hover:text-[#0B5D9B] font-semibold cursor-pointer"
            >
              🖨️ Support sheet
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
