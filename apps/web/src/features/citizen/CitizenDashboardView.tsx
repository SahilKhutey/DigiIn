import React from "react";
import { Button, DigiInIDCard } from "../../components/ui";
import { useAuth } from "../../context/AuthContext";
import { WalletDocument } from "../../types";

interface CitizenDashboardViewProps {
  walletDocuments: WalletDocument[];
  onSelectDocument: (docId: string) => void;
  onNavigateUpload: () => void;
  onNavigateWallet: () => void;
  onNavigateConsent: () => void;
  onNavigateScholarship: () => void;
  onNavigateAudit: () => void;
  onOpenScanner?: () => void;
  onOpenEkyc?: (doc?: WalletDocument) => void;
}

export const CitizenDashboardView: React.FC<CitizenDashboardViewProps> = ({
  walletDocuments,
  onSelectDocument,
  onNavigateUpload,
  onNavigateWallet,
  onNavigateConsent,
  onNavigateScholarship,
  onNavigateAudit,
  onOpenScanner,
  onOpenEkyc,
}) => {
  const { user } = useAuth();
  const citizenDigiinId = user?.digiinId || "DI-7K4M-9Q2X-8P6R";

  return (
    <div className="space-y-8 max-w-[1200px] mx-auto py-2">
      {/* 1. Header & Sovereign ID */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#092F4F] m-0">
            Good afternoon, {user?.name || "Rahul Sharma"}.
          </h1>
          <p className="text-xs text-slate-500 mt-1 m-0">
            DigiIn Sovereign ID: <code className="font-mono font-bold text-[#0B5D9B] bg-slate-100 px-2 py-0.5 rounded">{citizenDigiinId}</code>
          </p>
        </div>

        <div className="flex items-center gap-3">
          {onOpenEkyc && (
            <button
              type="button"
              onClick={() => onOpenEkyc()}
              className="px-3.5 py-2 rounded-xl text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-300 transition-all cursor-pointer"
            >
              🆔 eKYC Status
            </button>
          )}
          <Button
            variant="primary"
            size="sm"
            onClick={onNavigateScholarship}
            className="shadow-sm font-bold text-xs"
          >
            Start Verification Journey →
          </Button>
        </div>
      </div>

      {/* DigiIn Sovereign ID Card Banner */}
      <DigiInIDCard
        idNumber={citizenDigiinId}
        holderName={user?.name || "Rahul Sharma"}
        status="Active & Sovereign"
      />

      {/* 2. Priority Pending Request (Action Needed) */}
      <div className="bg-amber-50/90 border border-amber-300 rounded-2xl p-5 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-3.5">
          <span className="text-2xl mt-0.5">⚠️</span>
          <div>
            <div className="font-extrabold text-sm text-amber-950">
              Action needed
            </div>
            <p className="text-xs text-amber-900 m-0 mt-0.5 leading-relaxed">
              <strong>NTA</strong> wants to verify your <strong>Class XII qualification</strong>. Purpose: <strong>JEE application</strong>. Expires in <strong>14 minutes</strong>.
            </p>
          </div>
        </div>

        <Button
          variant="primary"
          size="sm"
          onClick={onNavigateConsent}
          className="bg-amber-800 hover:bg-amber-900 text-white font-bold shrink-0 shadow-xs cursor-pointer"
        >
          Review request →
        </Button>
      </div>

      {/* 3. Quick Actions Dock */}
      <div>
        <div className="text-xs uppercase font-extrabold tracking-wider text-slate-400 mb-3">
          Quick actions
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Action 1: Upload */}
          <button
            type="button"
            onClick={onNavigateUpload}
            className="p-5 bg-white border border-slate-200 rounded-2xl shadow-2xs hover:border-[#0B5D9B] hover:shadow-xs transition-all text-left space-y-2 cursor-pointer group"
          >
            <div className="h-10 w-10 rounded-xl bg-blue-50 text-[#0B5D9B] text-xl flex items-center justify-center font-bold">
              📁
            </div>
            <div className="font-extrabold text-sm text-[#092F4F] group-hover:text-[#0B5D9B]">
              Upload
            </div>
            <div className="text-xs text-slate-500">
              Add a document for verification
            </div>
          </button>

          {/* Action 2: Verify */}
          <button
            type="button"
            onClick={onNavigateConsent}
            className="p-5 bg-white border border-slate-200 rounded-2xl shadow-2xs hover:border-emerald-600 hover:shadow-xs transition-all text-left space-y-2 cursor-pointer group"
          >
            <div className="h-10 w-10 rounded-xl bg-emerald-50 text-emerald-700 text-xl flex items-center justify-center font-bold">
              🛡️
            </div>
            <div className="font-extrabold text-sm text-[#092F4F] group-hover:text-emerald-700">
              Verify
            </div>
            <div className="text-xs text-slate-500">
              Review a verification request
            </div>
          </button>

          {/* Action 3: Share */}
          <button
            type="button"
            onClick={onNavigateConsent}
            className="p-5 bg-white border border-slate-200 rounded-2xl shadow-2xs hover:border-amber-600 hover:shadow-xs transition-all text-left space-y-2 cursor-pointer group"
          >
            <div className="h-10 w-10 rounded-xl bg-amber-50 text-amber-700 text-xl flex items-center justify-center font-bold">
              🔐
            </div>
            <div className="font-extrabold text-sm text-[#092F4F] group-hover:text-amber-700">
              Share
            </div>
            <div className="text-xs text-slate-500">
              Manage active sharing permissions
            </div>
          </button>
        </div>
      </div>

      {/* 4. Credentials Summary & List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-extrabold text-[#092F4F] m-0">
              Your credentials
            </h2>
            <p className="text-xs text-slate-500 m-0">
              3 verified · 1 pending · 0 expired
            </p>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={onNavigateWallet}
            className="font-bold text-xs"
          >
            View all →
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            {
              id: "doc_cbse_xii_2026",
              title: "Class XII Certificate",
              issuer: "CBSE Central Registry",
              statusText: "✓ Verified",
              statusClass: "bg-emerald-50 text-emerald-800 border-emerald-300",
              roll: "26182910",
              icon: "🎓",
            },
            {
              id: "doc_aadhaar_ekyc",
              title: "Aadhaar Identity Assertion",
              issuer: "UIDAI Authority",
              statusText: "✓ Verified",
              statusClass: "bg-emerald-50 text-emerald-800 border-emerald-300",
              roll: "XXXX-XXXX-8492",
              icon: "🆔",
            },
            {
              id: "doc_morth_dl",
              title: "Driving Licence (LMV)",
              issuer: "Ministry of Road Transport (MoRTH)",
              statusText: "✓ Verified",
              statusClass: "bg-emerald-50 text-emerald-800 border-emerald-300",
              roll: "DL-0420260019283",
              icon: "🚗",
            },
            {
              id: "doc_btech_degree",
              title: "B.Tech Degree Certificate",
              issuer: "State Technical University",
              statusText: "⟳ Pending Review",
              statusClass: "bg-amber-50 text-amber-800 border-amber-300",
              roll: "STU-2026-ENG-491",
              icon: "📜",
            },
          ].map((doc) => (
            <div
              key={doc.id}
              onClick={() => onSelectDocument(doc.id)}
              className="bg-white border border-slate-200 rounded-2xl p-5 shadow-2xs hover:border-[#0B5D9B] hover:shadow-xs transition-all cursor-pointer flex flex-col justify-between group"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xl">{doc.icon}</span>
                  <span className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border ${doc.statusClass}`}>
                    {doc.statusText}
                  </span>
                </div>
                <div>
                  <h3 className="text-sm font-bold text-[#092F4F] m-0 group-hover:text-[#0B5D9B] transition-colors">
                    {doc.title}
                  </h3>
                  <p className="text-xs text-slate-500 m-0">
                    {doc.issuer}
                  </p>
                </div>
              </div>

              <div className="pt-3 mt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                <span className="font-mono text-slate-500 text-[11px]">{doc.roll}</span>
                <span className="text-[#0B5D9B] font-bold group-hover:underline">
                  View →
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 5. Recent Sovereign Activity Timeline */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-extrabold text-[#092F4F] m-0">
            Recent activity
          </h2>
          <button
            type="button"
            onClick={onNavigateAudit}
            className="text-xs font-bold text-[#0B5D9B] hover:underline cursor-pointer"
          >
            Full audit log →
          </button>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-2xs space-y-3 text-xs">
          <div className="flex items-center justify-between text-slate-700 py-1 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <span className="text-emerald-600 font-bold">✓</span>
              <span><strong>Verification completed</strong> · NTA (JEE application)</span>
            </div>
            <span className="text-slate-400 text-[11px] font-mono">15:51</span>
          </div>

          <div className="flex items-center justify-between text-slate-700 py-1 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <span className="text-blue-600 font-bold">✓</span>
              <span><strong>Consent granted</strong> · NTA</span>
            </div>
            <span className="text-slate-400 text-[11px] font-mono">15:48</span>
          </div>

          <div className="flex items-center justify-between text-slate-700 py-1">
            <div className="flex items-center gap-2">
              <span className="text-slate-500 font-bold">📁</span>
              <span><strong>Document uploaded</strong> · Class XII Certificate</span>
            </div>
            <span className="text-slate-400 text-[11px] font-mono">14:32</span>
          </div>
        </div>
      </div>
    </div>
  );
};
