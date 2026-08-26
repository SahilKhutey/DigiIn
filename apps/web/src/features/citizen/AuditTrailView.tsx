import React, { useState } from "react";
import { Button, Card, Badge } from "../../components/ui";
import { useLanguage } from "../../context/LanguageContext";

interface AuditEvent {
  id: string;
  timestamp: string;
  type: "VERIFICATION" | "CONSENT_GRANTED" | "CONSENT_REVOKED" | "DOCUMENT_SYNC";
  requester: string;
  purpose: string;
  attributes: string[];
  bytesTransferred: number;
  merkleHash: string;
}

export const AuditTrailView: React.FC = () => {
  const { locale } = useLanguage();
  const hi = locale === "hi";

  const [filter, setFilter] = useState<string>("ALL");
  const [downloaded, setDownloaded] = useState(false);

  const events: AuditEvent[] = [
    {
      id: "aud_01",
      timestamp: "22 Aug 2026, 14:15 IST",
      type: "VERIFICATION",
      requester: "University of Delhi (DU)",
      purpose: "National Merit-cum-Means Scholarship Eligibility",
      attributes: ["Name: Rahul Sharma", "Domicile: Delhi", "Income Threshold: < ₹2.5L", "Class XII: Passed (>=60%)"],
      bytesTransferred: 0,
      merkleHash: "0x8f2a...91b4",
    },
    {
      id: "aud_02",
      timestamp: "22 Aug 2026, 14:10 IST",
      type: "CONSENT_GRANTED",
      requester: "University of Delhi (DU)",
      purpose: "Single-Use Scholarship Verification Token",
      attributes: ["4 Scoped Claims Approved", "Aadhaar Number Withheld", "Scans Withheld"],
      bytesTransferred: 0,
      merkleHash: "0x7c1e...44d2",
    },
    {
      id: "aud_03",
      timestamp: "20 Aug 2026, 10:45 IST",
      type: "CONSENT_REVOKED",
      requester: "Third-Party Fintech API",
      purpose: "On-demand access grant terminated by citizen",
      attributes: ["Bank Account Assertion Revoked"],
      bytesTransferred: 0,
      merkleHash: "0x3a9f...88c1",
    },
    {
      id: "aud_04",
      timestamp: "18 Aug 2026, 09:30 IST",
      type: "DOCUMENT_SYNC",
      requester: "CBSE Central Registry",
      purpose: "Authoritative Board Certificate NAD Hash Synchronization",
      attributes: ["Class XII Marksheet SHA-256 Registered"],
      bytesTransferred: 0,
      merkleHash: "0x1d4b...55f0",
    },
  ];

  const filteredEvents = events.filter((e) => {
    if (filter === "ALL") return true;
    return e.type === filter;
  });

  const handleDownloadDigest = () => {
    setDownloaded(true);
    setTimeout(() => setDownloaded(false), 3000);
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto py-2">
      {/* Header Banner */}
      <div className="bg-white border border-[#CBD5E1] rounded-3xl p-6 md:p-8 shadow-xs space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <span className="text-xs font-bold uppercase tracking-widest text-[#0B5D9B]">
              {hi ? "अपरिवर्तनीय संप्रभु लेखापरीक्षा" : "Immutable Sovereign Audit Trail"}
            </span>
            <h1 className="text-2xl md:text-3xl font-extrabold text-[#092F4F] m-0">
              {hi ? "सत्यापन और सहमति इतिहास" : "Audit & Verification History"}
            </h1>
            <p className="text-xs md:text-sm text-slate-600 m-0">
              Cryptographically anchored chronological record of all authorizations, verifications, and revocations under the DPDP Act 2023.
            </p>
          </div>

          <Button
            variant="outline"
            size="md"
            onClick={handleDownloadDigest}
            className="font-bold shrink-0 shadow-2xs"
          >
            {downloaded ? "✓ Digest Downloaded" : "📄 Download Signed Digest"}
          </Button>
        </div>

        {/* Filter Chips */}
        <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-200">
          {[
            { id: "ALL", label: `All Events (${events.length})` },
            { id: "VERIFICATION", label: "Verifications" },
            { id: "CONSENT_GRANTED", label: "Consent Grants" },
            { id: "CONSENT_REVOKED", label: "Revocations" },
            { id: "DOCUMENT_SYNC", label: "Registry Syncs" },
          ].map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setFilter(tab.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-colors cursor-pointer ${
                filter === tab.id
                  ? "bg-[#0B5D9B] text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Chronological Event Stream */}
      <div className="space-y-4">
        {filteredEvents.map((evt) => {
          const typeBadge = {
            VERIFICATION: { label: "✓ Verification Completed", bg: "bg-emerald-50 text-emerald-800 border-emerald-300" },
            CONSENT_GRANTED: { label: "🔐 Consent Authorized", bg: "bg-sky-50 text-[#0B5D9B] border-sky-300" },
            CONSENT_REVOKED: { label: "✕ Grant Revoked", bg: "bg-red-50 text-red-800 border-red-300" },
            DOCUMENT_SYNC: { label: "🔄 Registry Synced", bg: "bg-purple-50 text-purple-800 border-purple-300" },
          }[evt.type];

          return (
            <div
              key={evt.id}
              className="bg-white border border-[#CBD5E1] rounded-2xl p-5 shadow-2xs space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className={`text-[11px] font-extrabold px-2.5 py-0.5 rounded-full border ${typeBadge.bg}`}>
                    {typeBadge.label}
                  </span>
                  <span className="text-xs font-bold text-[#092F4F]">{evt.requester}</span>
                </div>

                <div className="text-xs text-slate-500 font-mono">
                  {evt.timestamp}
                </div>
              </div>

              <div className="text-xs text-slate-600">
                <strong>Purpose:</strong> {evt.purpose}
              </div>

              <div className="p-3 bg-[#F8FAFC] border border-slate-200 rounded-xl space-y-1">
                <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wide">
                  Scoped Attributes
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {evt.attributes.map((attr, idx) => (
                    <span
                      key={idx}
                      className="text-[11px] font-medium bg-white px-2 py-0.5 rounded border border-slate-200 text-slate-700"
                    >
                      {attr}
                    </span>
                  ))}
                </div>
              </div>

              <div className="pt-2 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-500 font-mono">
                <div>Raw File Exposure: <strong className="text-emerald-700 font-bold">{evt.bytesTransferred} Bytes</strong></div>
                <div>Merkle Root Anchor: <span className="text-slate-700">{evt.merkleHash}</span></div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
