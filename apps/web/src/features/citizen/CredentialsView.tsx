import React, { useState } from "react";
import { Button, Modal } from "../../components/ui";

export interface CredentialItem {
  id: string;
  title: string;
  issuer: string;
  qualification: string;
  passingYear: string;
  status: "Active" | "Pending" | "Expired";
  issuedDate: string;
  sha256: string;
}

const DEFAULT_CREDENTIALS: CredentialItem[] = [
  {
    id: "cred_cbse_xii_2026",
    title: "Class XII Qualification",
    issuer: "CBSE",
    qualification: "Class XII",
    passingYear: "2026",
    status: "Active",
    issuedDate: "15 May 2026",
    sha256: "8f9a2b1c4e7d0f3a6b5c8e9d2a4f7b0e3c6a9d1f5e8b2a4c7d0f3a6b5c8e9d2a",
  },
  {
    id: "cred_uidai_ekyc_2026",
    title: "Aadhaar Identity Assertion",
    issuer: "UIDAI",
    qualification: "Identity & Age Verification",
    passingYear: "2026",
    status: "Active",
    issuedDate: "10 Jan 2026",
    sha256: "3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e",
  },
  {
    id: "cred_morth_dl_2026",
    title: "Driving Licence (LMV)",
    issuer: "MoRTH",
    qualification: "Light Motor Vehicle Endorsement",
    passingYear: "2026",
    status: "Active",
    issuedDate: "02 Feb 2026",
    sha256: "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b",
  },
];

export interface CredentialsViewProps {
  onCreateProof?: (credId: string) => void;
  onShare?: (credId: string) => void;
  onNavigateWallet?: () => void;
}

export const CredentialsView: React.FC<CredentialsViewProps> = ({
  onCreateProof,
  onShare,
  onNavigateWallet,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCred, setSelectedCred] = useState<CredentialItem | null>(null);

  const filteredCredentials = DEFAULT_CREDENTIALS.filter(
    (c) =>
      c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.issuer.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-4xl mx-auto py-2">
      {/* Header */}
      <div className="space-y-1">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-[#092F4F] m-0">
          Credentials
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 m-0">
          Your verified digital credentials.
        </p>
      </div>

      {/* Search Toolbar */}
      <div className="bg-white border border-slate-200 rounded-xl p-3 shadow-2xs">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search credentials..."
          className="w-full bg-transparent text-sm text-slate-800 focus:outline-hidden placeholder:text-slate-400"
        />
      </div>

      {/* Credential List / Grid */}
      {filteredCredentials.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-10 text-center space-y-3">
          <div className="text-3xl">📜</div>
          <h3 className="text-base font-bold text-slate-800 m-0">
            No credentials yet.
          </h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto m-0">
            Verified credentials will appear here once verified by an issuing authority.
          </p>
          <div className="pt-2">
            <Button
              variant="primary"
              size="sm"
              onClick={onNavigateWallet}
              className="font-bold cursor-pointer"
            >
              View documents →
            </Button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredCredentials.map((cred) => (
            <div
              key={cred.id}
              className="bg-white border border-slate-200 rounded-2xl p-5 shadow-2xs hover:border-[#0B5D9B] hover:shadow-xs transition-all flex flex-col justify-between space-y-4"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-500">
                    Issued by <strong>{cred.issuer}</strong>
                  </span>
                  <span className="text-[10px] font-extrabold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-300">
                    ✓ Verified
                  </span>
                </div>

                <div>
                  <h3 className="text-base font-bold text-[#092F4F] m-0">
                    {cred.title}
                  </h3>
                  <p className="text-xs text-slate-500 m-0 mt-0.5">
                    Status: <strong className="text-slate-700">{cred.status}</strong> · Year: <strong>{cred.passingYear}</strong>
                  </p>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-xs font-semibold text-emerald-700">Valid</span>
                <button
                  type="button"
                  onClick={() => setSelectedCred(cred)}
                  className="text-xs font-bold text-[#0B5D9B] hover:underline cursor-pointer"
                >
                  View credential →
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Credential Detail Modal */}
      {selectedCred && (
        <Modal
          isOpen={true}
          onClose={() => setSelectedCred(null)}
          title="Credential Detail"
        >
          <div className="space-y-5 text-xs text-slate-700">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-base font-bold text-[#092F4F] m-0">
                  {selectedCred.title}
                </h3>
                <p className="text-slate-500 m-0">
                  Issuer: <strong>{selectedCred.issuer}</strong>
                </p>
              </div>
              <span className="text-xs font-extrabold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-300">
                ✓ Verified
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-0.5">
                <div className="text-slate-500 text-[11px]">Qualification</div>
                <div className="font-bold text-slate-800">{selectedCred.qualification}</div>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-0.5">
                <div className="text-slate-500 text-[11px]">Passing Year</div>
                <div className="font-bold text-slate-800">{selectedCred.passingYear}</div>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-0.5">
                <div className="text-slate-500 text-[11px]">Status</div>
                <div className="font-bold text-emerald-800">{selectedCred.status}</div>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-0.5">
                <div className="text-slate-500 text-[11px]">Issued Date</div>
                <div className="font-bold text-slate-800">{selectedCred.issuedDate}</div>
              </div>
            </div>

            <div className="pt-2 flex items-center justify-end gap-2 border-t border-slate-100">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => {
                  onShare?.(selectedCred.id);
                  setSelectedCred(null);
                }}
                className="font-bold cursor-pointer"
              >
                Share
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={() => {
                  onCreateProof?.(selectedCred.id);
                  setSelectedCred(null);
                }}
                className="font-bold shadow-xs cursor-pointer"
              >
                Create proof →
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
