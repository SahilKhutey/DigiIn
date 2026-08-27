import React, { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { useLanguage } from "../../context/LanguageContext";
import { Button, Card, Badge } from "../../components/ui";
import QRCode from "qrcode";

export type IdentityTab =
  | "overview"
  | "personal"
  | "verification"
  | "access"
  | "activity"
  | "security";

interface Props {
  initialTab?: IdentityTab;
  onNavigateToDocuments?: () => void;
  onNavigateToServices?: () => void;
  onNavigateToVerification?: () => void;
}

export const IdentityCenterView: React.FC<Props> = ({
  initialTab = "overview",
  onNavigateToDocuments,
  onNavigateToServices,
  onNavigateToVerification,
}) => {
  const { user } = useAuth();
  const { locale } = useLanguage();
  const [activeTab, setActiveTab] = useState<IdentityTab>(initialTab);

  const accountId = user?.digiinId || "DI-7K4M-9Q2X-8P6R";
  const citizenName = user?.name || "Rahul Sharma";

  // Modal states
  const [showAboutModal, setShowAboutModal] = useState(false);
  const [showQrModal, setShowQrModal] = useState(false);
  const [qrDataUrl, setQrDataUrl] = useState<string>("");
  const [selectedClaim, setSelectedClaim] = useState<any | null>(null);
  const [serviceToRevoke, setServiceToRevoke] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    const payload = `digiin://verify?id=${accountId}&t=${Date.now()}`;
    QRCode.toDataURL(payload, { width: 180, margin: 2, color: { dark: "#092F4F", light: "#FFFFFF" } })
      .then((url) => setQrDataUrl(url))
      .catch((err) => console.error("Error generating QR:", err));
  }, [accountId]);

  // Active services state (for revocation demo)
  const [services, setServices] = useState([
    {
      id: "dept_du_scholarship_portal",
      name: "University of Delhi — Scholarship Board",
      department: "Ministry of Education",
      purpose: "Merit-cum-Means Scholarship 2026",
      status: "ACTIVE",
      allowedScopes: ["Education (Class XII)", "Income Eligibility", "State Domicile"],
      approvedDate: "27 Aug 2026",
      expiresDate: "27 Aug 2027",
    },
    {
      id: "dept_revenue_nct_delhi",
      name: "Department of Revenue, Govt of NCT Delhi",
      department: "State Revenue Department",
      purpose: "EWS & Domicile Attestation",
      status: "ACTIVE",
      allowedScopes: ["Income Eligibility", "State Domicile"],
      approvedDate: "26 Aug 2026",
      expiresDate: "26 Aug 2027",
    },
    {
      id: "dept_municipal_land_records",
      name: "Municipal Corporation — Land Records",
      department: "Urban Local Bodies",
      purpose: "Property Record Attestation",
      status: "ACTIVE",
      allowedScopes: ["State Domicile"],
      approvedDate: "25 Aug 2026",
      expiresDate: "25 Feb 2027",
    },
  ]);

  // Pending incoming request state
  const [pendingRequest, setPendingRequest] = useState<any | null>({
    ref: "VR-82J4K7",
    serviceName: "National Testing Agency (NTA)",
    department: "Department of Higher Education",
    purpose: "CUET / JEE Entrance Quota Verification",
    requestedScopes: ["Class XII Marksheet", "State Domicile Certificate"],
    requestedAgo: "3 minutes ago",
    expiresIn: "06:42",
  });

  const verifiedClaims = [
    {
      id: "identity",
      title: "Sovereign Identity Assertion",
      status: "VERIFIED",
      level: "Level 4 (Direct UIDAI eKYC)",
      document: "Aadhaar Identity Assertion",
      verifiedDate: "10 Jan 2026",
      validUntil: "Lifetime",
      usedBy: "3 Services",
      issuer: "UIDAI eKYC Gateway",
    },
    {
      id: "education",
      title: "Class XII Senior Secondary Marksheet",
      status: "VERIFIED",
      level: "Level 5 (Cryptographically Sealed)",
      document: "CBSE Senior Secondary Marksheet",
      verifiedDate: "15 May 2026",
      validUntil: "Lifetime",
      usedBy: "2 Services",
      issuer: "Central Board of Secondary Education (CBSE)",
    },
    {
      id: "income",
      title: "Annual Household Income (< 2.5 Lakhs)",
      status: "VERIFIED",
      level: "Level 4 (Issuer Verified)",
      document: "Income Certificate 2026-27",
      verifiedDate: "10 Feb 2026",
      validUntil: "31 Mar 2027",
      usedBy: "2 Services",
      issuer: "Revenue Department, Govt of NCT Delhi",
    },
    {
      id: "domicile",
      title: "State Domicile Certificate",
      status: "VERIFIED",
      level: "Level 4 (Issuer Verified)",
      document: "NCT Delhi Domicile Certificate",
      verifiedDate: "15 Jan 2026",
      validUntil: "15 Jan 2031",
      usedBy: "3 Services",
      issuer: "Department of Revenue & Home Affairs",
    },
    {
      id: "caste",
      title: "Social Category / Caste Certificate",
      status: "VERIFIED",
      level: "Level 4 (Issuer Verified)",
      document: "OBC-NCL Certificate",
      verifiedDate: "20 Jan 2026",
      validUntil: "20 Jan 2028",
      usedBy: "1 Service",
      issuer: "District Magistrate Office, Central Delhi",
    },
    {
      id: "address",
      title: "State Residence / Address Proof",
      status: "PENDING",
      level: "Level 2 (Format Checked)",
      document: "Electricity Bill (Self-Uploaded)",
      verifiedDate: "Pending Review",
      validUntil: "N/A",
      usedBy: "0 Services",
      issuer: "BSES Yamuna Power Ltd",
    },
  ];

  const handleCopyId = () => {
    navigator.clipboard?.writeText(accountId);
    setCopiedId(true);
    setTimeout(() => setCopiedId(false), 2000);
  };

  const handleApproveRequest = () => {
    setNotice("✓ Verification approved. Ed25519 signed assertion emitted to National Testing Agency.");
    setPendingRequest(null);
    setTimeout(() => setNotice(null), 4000);
  };

  const handleDenyRequest = () => {
    setNotice("✕ Verification request denied. No information was shared.");
    setPendingRequest(null);
    setTimeout(() => setNotice(null), 4000);
  };

  const handleConfirmRevoke = () => {
    if (!serviceToRevoke) return;
    setServices((prev) => prev.filter((s) => s.id !== serviceToRevoke));
    setNotice("✓ Access revoked. Service can no longer verify your DigiIn claims.");
    setServiceToRevoke(null);
    setTimeout(() => setNotice(null), 4000);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 py-2">
      {/* 1. Header & Breadcrumbs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <nav className="text-xs font-semibold text-slate-500 mb-1" aria-label="Breadcrumb">
            <span>DigiIn</span>
            <span className="mx-1.5">/</span>
            <span className="text-[#0B5D9B]">My Identity</span>
            {activeTab !== "overview" && (
              <>
                <span className="mx-1.5">/</span>
                <span className="capitalize text-slate-800">{activeTab}</span>
              </>
            )}
          </nav>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#092F4F] m-0 flex items-center gap-2.5">
            <span>🪪</span> My DigiIn Identity Center
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-1 m-0">
            Your persistent sovereign identity, verified credentials, and consent control hub.
          </p>
        </div>

        {/* Quick Actions */}
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowAboutModal(true)}
            className="text-xs font-bold border-slate-300 text-slate-700 hover:bg-slate-50"
          >
            ℹ️ About ID
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setShowQrModal(true)}
            className="text-xs font-bold bg-[#092F4F] text-white hover:bg-[#071F34]"
          >
            📱 Show QR
          </Button>
        </div>
      </div>

      {/* Global Notification Banner */}
      {notice && (
        <div
          className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-300 text-xs font-bold text-emerald-900 flex items-center justify-between shadow-xs animate-fadeIn"
          role="status"
        >
          <span>{notice}</span>
          <button
            type="button"
            onClick={() => setNotice(null)}
            className="text-emerald-700 hover:text-emerald-950 text-sm font-extrabold ml-2"
          >
            ✕
          </button>
        </div>
      )}

      {/* 2. Sub-Navigation Tabs */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 border-b border-slate-200 text-xs font-bold">
        {[
          { id: "overview", label: "Overview", icon: "🏠" },
          { id: "personal", label: "Personal Information", icon: "👤" },
          { id: "verification", label: "Verification Status", icon: "✓", badge: "6" },
          { id: "access", label: "Access & Consent", icon: "🔐", badge: pendingRequest ? "1 Pending" : "3" },
          { id: "activity", label: "Activity Timeline", icon: "📋" },
          { id: "security", label: "Security & Trust", icon: "🛡️" },
        ].map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id as IdentityTab)}
              className={`flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl transition-all whitespace-nowrap cursor-pointer ${
                isActive
                  ? "bg-[#0B5D9B] text-white shadow-xs"
                  : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
              {tab.badge && (
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-full font-extrabold ml-1 ${
                    isActive
                      ? "bg-white/20 text-white"
                      : "bg-slate-100 text-slate-700 border border-slate-300"
                  }`}
                >
                  {tab.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* 3. Tab Contents */}

      {/* TAB 1: OVERVIEW */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          {/* Hero Account ID Card */}
          <div className="bg-gradient-to-br from-[#092F4F] via-[#0B5D9B] to-[#074B7D] text-white rounded-3xl p-6 sm:p-8 shadow-md relative overflow-hidden">
            {/* Background Decorative Pattern */}
            <div className="absolute -right-12 -bottom-12 w-64 h-64 rounded-full bg-white/5 pointer-events-none blur-xl" />
            <div className="absolute right-8 top-8 text-white/10 font-mono text-7xl font-black select-none pointer-events-none">
              DI
            </div>

            <div className="relative z-10 space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-extrabold uppercase tracking-wider text-cyan-200">
                    Sovereign DigiIn Identity
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 text-[11px] font-bold flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                    Active & Verified
                  </span>
                </div>
                <span className="text-xs text-slate-300 font-medium">
                  {citizenName}
                </span>
              </div>

              {/* Account ID Display */}
              <div className="space-y-1">
                <div className="text-xs text-slate-300 font-medium">Your DigiIn Account ID:</div>
                <div className="font-mono text-2xl sm:text-4xl font-extrabold tracking-widest text-white select-all">
                  {accountId}
                </div>
              </div>

              {/* Trust Subtext */}
              <p className="text-xs text-cyan-100/80 max-w-xl m-0">
                This public ID identifies your DigiIn account. It allows authorized government services to request verified claims without accessing your raw documents.
              </p>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center gap-3 pt-2">
                <button
                  type="button"
                  onClick={handleCopyId}
                  className="px-4 py-2 rounded-xl bg-white text-[#092F4F] font-bold text-xs hover:bg-slate-100 transition-all flex items-center gap-1.5 shadow-sm cursor-pointer"
                >
                  <span>{copiedId ? "✓" : "📋"}</span>
                  <span>{copiedId ? "Copied to Clipboard" : "Copy Account ID"}</span>
                </button>

                <button
                  type="button"
                  onClick={() => setShowQrModal(true)}
                  className="px-4 py-2 rounded-xl bg-white/10 text-white border border-white/20 font-bold text-xs hover:bg-white/20 transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  <span>📱</span>
                  <span>Show QR & OTP</span>
                </button>

                <button
                  type="button"
                  onClick={() => setShowAboutModal(true)}
                  className="px-3 py-2 rounded-xl text-cyan-200 hover:text-white font-semibold text-xs transition-all flex items-center gap-1 cursor-pointer"
                >
                  <span>ℹ️</span>
                  <span>How it works</span>
                </button>
              </div>
            </div>
          </div>

          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div
              onClick={() => setActiveTab("verification")}
              className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs hover:border-[#0B5D9B] transition-all cursor-pointer space-y-1"
            >
              <div className="text-xs font-semibold text-slate-500">Verified Information</div>
              <div className="text-2xl font-extrabold text-[#092F4F] flex items-center justify-between">
                <span>6 Claims</span>
                <span className="text-sm font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-lg border border-emerald-200">
                  ✓ 100% Valid
                </span>
              </div>
              <div className="text-[11px] text-slate-500">Income, Domicile, Class XII, Caste, Identity</div>
            </div>

            <div
              onClick={() => onNavigateToDocuments && onNavigateToDocuments()}
              className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs hover:border-[#0B5D9B] transition-all cursor-pointer space-y-1"
            >
              <div className="text-xs font-semibold text-slate-500">Document Vault</div>
              <div className="text-2xl font-extrabold text-[#092F4F] flex items-center justify-between">
                <span>8 Documents</span>
                <span className="text-sm font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-lg border border-blue-200">
                  SHA-256 Sealed
                </span>
              </div>
              <div className="text-[11px] text-slate-500">Encrypted in content-addressed storage</div>
            </div>

            <div
              onClick={() => setActiveTab("access")}
              className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs hover:border-[#0B5D9B] transition-all cursor-pointer space-y-1"
            >
              <div className="text-xs font-semibold text-slate-500">Authorized Services</div>
              <div className="text-2xl font-extrabold text-[#092F4F] flex items-center justify-between">
                <span>{services.length} Portals</span>
                <span className="text-sm font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-lg border border-amber-200">
                  {pendingRequest ? "1 Request" : "Managed"}
                </span>
              </div>
              <div className="text-[11px] text-slate-500">Education, Revenue & Land Services</div>
            </div>
          </div>

          {/* Pending Verification Request Inbox Alert */}
          {pendingRequest && (
            <div className="bg-amber-50 border-2 border-amber-300 rounded-2xl p-5 shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-lg">🔔</span>
                  <span className="text-xs font-extrabold uppercase tracking-wide text-amber-900">
                    Incoming Verification Request ({pendingRequest.ref})
                  </span>
                </div>
                <span className="text-xs font-mono font-bold text-amber-800 bg-amber-100 px-2.5 py-0.5 rounded-md border border-amber-300">
                  Expires in {pendingRequest.expiresIn}
                </span>
              </div>

              <div className="text-xs text-amber-950 space-y-1">
                <div>
                  <strong>{pendingRequest.serviceName}</strong> is requesting to verify your:
                </div>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {pendingRequest.requestedScopes.map((scope: string) => (
                    <span
                      key={scope}
                      className="px-2.5 py-1 bg-white text-slate-800 font-bold rounded-lg border border-amber-300 text-xs shadow-2xs"
                    >
                      ✓ {scope}
                    </span>
                  ))}
                </div>
              </div>

              <div className="pt-2 flex items-center justify-between text-xs border-t border-amber-200">
                <span className="text-amber-800 text-[11px]">
                  Purpose: <strong>{pendingRequest.purpose}</strong> (0 raw documents shared)
                </span>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleDenyRequest}
                    className="text-xs font-bold text-red-700 border-red-300 hover:bg-red-50"
                  >
                    Deny
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={handleApproveRequest}
                    className="text-xs font-bold bg-[#092F4F] hover:bg-[#071F34]"
                  >
                    Approve Verification
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Associated Information Quick Navigation */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
            <h2 className="text-base font-bold text-[#092F4F] m-0">Associated Information Hub</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div
                onClick={() => setActiveTab("personal")}
                className="p-4 bg-slate-50 border border-slate-200 rounded-xl hover:bg-slate-100 transition-all cursor-pointer flex items-center justify-between"
              >
                <div className="space-y-0.5">
                  <strong className="text-sm font-bold text-slate-900 block">Personal Information</strong>
                  <span className="text-slate-500">Demographic details & contact attributes</span>
                </div>
                <span className="text-slate-400 font-bold text-lg">→</span>
              </div>

              <div
                onClick={() => setActiveTab("verification")}
                className="p-4 bg-slate-50 border border-slate-200 rounded-xl hover:bg-slate-100 transition-all cursor-pointer flex items-center justify-between"
              >
                <div className="space-y-0.5">
                  <strong className="text-sm font-bold text-slate-900 block">Verified Claims (6)</strong>
                  <span className="text-slate-500">Issuer-verified credentials & levels</span>
                </div>
                <span className="text-slate-400 font-bold text-lg">→</span>
              </div>

              <div
                onClick={() => setActiveTab("access")}
                className="p-4 bg-slate-50 border border-slate-200 rounded-xl hover:bg-slate-100 transition-all cursor-pointer flex items-center justify-between"
              >
                <div className="space-y-0.5">
                  <strong className="text-sm font-bold text-slate-900 block">Service Access & Consents</strong>
                  <span className="text-slate-500">Manage approved department verifications</span>
                </div>
                <span className="text-slate-400 font-bold text-lg">→</span>
              </div>

              <div
                onClick={() => setActiveTab("activity")}
                className="p-4 bg-slate-50 border border-slate-200 rounded-xl hover:bg-slate-100 transition-all cursor-pointer flex items-center justify-between"
              >
                <div className="space-y-0.5">
                  <strong className="text-sm font-bold text-slate-900 block">Activity & Audit Trail</strong>
                  <span className="text-slate-500">Who accessed what information</span>
                </div>
                <span className="text-slate-400 font-bold text-lg">→</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: PERSONAL INFORMATION */}
      {activeTab === "personal" && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-xs space-y-6">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4">
            <div>
              <h2 className="text-lg font-bold text-[#092F4F] m-0">Personal Profile Information</h2>
              <p className="text-xs text-slate-500 mt-0.5 m-0">
                Basic account attributes linked to your DigiIn Sovereign ID.
              </p>
            </div>
            <span className="text-xs font-bold text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-300">
              ✓ eKYC Matched
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
              <span className="text-slate-500 font-medium">Full Legal Name:</span>
              <div className="text-sm font-bold text-slate-900">{citizenName}</div>
            </div>

            <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1 font-mono">
              <span className="font-sans text-slate-500 font-medium">DigiIn Sovereign ID:</span>
              <div className="text-sm font-bold text-[#0B5D9B]">{accountId}</div>
            </div>

            <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
              <span className="text-slate-500 font-medium">Date of Birth (Masked):</span>
              <div className="text-sm font-mono font-bold text-slate-800">•• / •• / 2004</div>
            </div>

            <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
              <span className="text-slate-500 font-medium">Gender:</span>
              <div className="text-sm font-bold text-slate-800">Male</div>
            </div>

            <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
              <span className="text-slate-500 font-medium">Mobile Number (Masked):</span>
              <div className="text-sm font-mono font-bold text-slate-800">+91 ••••••••42</div>
            </div>

            <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
              <span className="text-slate-500 font-medium">Registered Email (Masked):</span>
              <div className="text-sm font-mono font-bold text-slate-800">r•••••••@example.gov.in</div>
            </div>

            <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1 sm:col-span-2 font-mono">
              <span className="font-sans text-slate-500 font-medium">Ed25519 Root Key Fingerprint:</span>
              <div className="text-[11px] text-slate-700 break-all">
                SHA256:4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: VERIFICATION STATUS */}
      {activeTab === "verification" && (
        <div className="space-y-6">
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
              <div>
                <h2 className="text-lg font-bold text-[#092F4F] m-0">Verified Information Records</h2>
                <p className="text-xs text-slate-500 mt-0.5 m-0">
                  Pre-verified attributes available for selective disclosure to government portals.
                </p>
              </div>
              <span className="text-xs font-extrabold text-emerald-800 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-300">
                ✓ 5 Level-4/5 Sealed
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {verifiedClaims.map((claim) => (
                <div
                  key={claim.id}
                  onClick={() => setSelectedClaim(claim)}
                  className="p-4 bg-slate-50 border border-slate-200 hover:border-[#0B5D9B] rounded-xl transition-all cursor-pointer space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-900">{claim.title}</span>
                    <span
                      className={`text-[10px] font-extrabold px-2 py-0.5 rounded-full ${
                        claim.status === "VERIFIED"
                          ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                          : "bg-amber-100 text-amber-800 border border-amber-300"
                      }`}
                    >
                      {claim.status === "VERIFIED" ? "✓ Verified" : "⏳ Pending"}
                    </span>
                  </div>

                  <div className="text-[11px] text-slate-600 space-y-0.5">
                    <div>Level: <strong className="text-slate-800">{claim.level}</strong></div>
                    <div>Source: <span className="text-slate-700">{claim.issuer}</span></div>
                    <div>Valid Until: <span className="text-slate-700">{claim.validUntil}</span></div>
                  </div>

                  <div className="pt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px] font-bold text-[#0B5D9B]">
                    <span>Used by {claim.usedBy}</span>
                    <span>View Details →</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: ACCESS & CONSENT */}
      {activeTab === "access" && (
        <div className="space-y-6">
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h2 className="text-lg font-bold text-[#092F4F] m-0">Authorized Government Services</h2>
                <p className="text-xs text-slate-500 mt-0.5 m-0">
                  Services permitted to verify specific claims. You can revoke access anytime.
                </p>
              </div>
              <span className="text-xs font-bold text-blue-800 bg-blue-50 px-2.5 py-1 rounded-full border border-blue-300">
                {services.length} Active Authorizations
              </span>
            </div>

            <div className="space-y-3">
              {services.map((svc) => (
                <div
                  key={svc.id}
                  className="p-4 bg-slate-50 border border-slate-200 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <strong className="text-sm font-bold text-slate-900">{svc.name}</strong>
                      <span className="text-[10px] font-bold px-2 py-0.2 bg-emerald-100 text-emerald-800 rounded-full border border-emerald-300">
                        ● Active
                      </span>
                    </div>
                    <div className="text-xs text-slate-500">
                      Purpose: <strong>{svc.purpose}</strong> · Approved: <strong>{svc.approvedDate}</strong>
                    </div>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {svc.allowedScopes.map((scope) => (
                        <span
                          key={scope}
                          className="px-2 py-0.5 bg-white text-slate-700 font-semibold rounded border border-slate-300 text-[10px]"
                        >
                          ✓ {scope}
                        </span>
                      ))}
                    </div>
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setServiceToRevoke(svc.id)}
                    className="text-xs font-bold text-red-700 border-red-300 hover:bg-red-50 shrink-0"
                  >
                    Revoke Access
                  </Button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: ACTIVITY TIMELINE */}
      {activeTab === "activity" && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
          <h2 className="text-lg font-bold text-[#092F4F] m-0">Universal Sovereign Activity Timeline</h2>
          <p className="text-xs text-slate-500 mt-0.5 m-0">
            Append-only, tamper-evident audit record of every access attempt, consent decision, and verification disclosure.
          </p>

          <div className="space-y-4 pt-2 divide-y divide-slate-100 text-xs">
            <div className="pt-3 space-y-1">
              <div className="flex items-center justify-between">
                <strong className="text-slate-900">University of Delhi — Scholarship Board</strong>
                <span className="text-slate-500 text-[11px]">Today, 09:43 AM</span>
              </div>
              <p className="text-slate-600 m-0">
                Verified: <strong>Class XII (CBSE 94.2%)</strong>, <strong>Income (&lt; 2.5L)</strong>, and <strong>State Domicile</strong>. (0 raw files transferred).
              </p>
              <div className="text-[10px] text-emerald-800 font-bold">✓ Status: VERIFIED · Assertion PRF-9A1B2C3D4E5F</div>
            </div>

            <div className="pt-3 space-y-1">
              <div className="flex items-center justify-between">
                <strong className="text-slate-900">Department of Revenue — Govt of NCT Delhi</strong>
                <span className="text-slate-500 text-[11px]">Yesterday, 02:20 PM</span>
              </div>
              <p className="text-slate-600 m-0">
                Verified: <strong>Income (&lt; 2.5L)</strong> and <strong>State Domicile</strong> for EWS scheme renewal.
              </p>
              <div className="text-[10px] text-emerald-800 font-bold">✓ Status: VERIFIED · Assertion PRF-77K31C</div>
            </div>

            <div className="pt-3 space-y-1">
              <div className="flex items-center justify-between">
                <strong className="text-slate-900">Municipal Corporation — Land Title Record</strong>
                <span className="text-slate-500 text-[11px]">25 Aug 2026, 11:15 AM</span>
              </div>
              <p className="text-slate-600 m-0">
                Verified: <strong>State Domicile (Delhi Resident)</strong>.
              </p>
              <div className="text-[10px] text-emerald-800 font-bold">✓ Status: VERIFIED · Assertion PRF-55X99A</div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 6: SECURITY & TRUST */}
      {activeTab === "security" && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-6">
          <div>
            <h2 className="text-lg font-bold text-[#092F4F] m-0">Security & Cryptographic Trust Architecture</h2>
            <p className="text-xs text-slate-500 mt-0.5 m-0">
              Cryptographic controls protecting your DigiIn identity from unauthorized access and data harvesting.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5">
              <div className="flex items-center gap-1.5 font-bold text-slate-900">
                <span>🛡️</span> Asymmetric Ed25519 Root Signatures
              </div>
              <p className="text-slate-600 m-0">
                All verification assertions are cryptographically signed using RFC 8032 / RFC 7515 asymmetric signatures.
              </p>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5">
              <div className="flex items-center gap-1.5 font-bold text-slate-900">
                <span>🔒</span> Zero-Knowledge Minimum Disclosure
              </div>
              <p className="text-slate-600 m-0">
                Departments receive boolean eligibility assertions and verified levels with 0 raw PDF bytes transferred.
              </p>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5">
              <div className="flex items-center gap-1.5 font-bold text-slate-900">
                <span>⏱️</span> Short-Lived Ephemeral Expirations
              </div>
              <p className="text-slate-600 m-0">
                Verification requests and QR tokens expire strictly in 10 minutes (600s) to prevent replay vulnerabilities.
              </p>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5">
              <div className="flex items-center gap-1.5 font-bold text-slate-900">
                <span>🛑</span> Anti-Enumeration Rate Limiting
              </div>
              <p className="text-slate-600 m-0">
                Uniform timing responses and tenant rate limiters prevent automated account scanning or existence probing.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 4. MODALS */}

      {/* A. About ID Modal */}
      {showAboutModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fadeIn">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 border border-slate-200">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-[#092F4F] m-0 flex items-center gap-2">
                <span>🛡️</span> About your DigiIn Account ID
              </h3>
              <button
                type="button"
                onClick={() => setShowAboutModal(false)}
                className="text-slate-400 hover:text-slate-700 text-lg font-bold"
              >
                ✕
              </button>
            </div>

            <div className="text-xs text-slate-600 space-y-3">
              <p className="m-0 font-medium">
                Your DigiIn Account ID (<strong>{accountId}</strong>) is your permanent, sovereign identifier on the DigiIn national platform.
              </p>
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl text-blue-900 space-y-1">
                <strong>Key Security Invariant:</strong>
                <div>
                  Your ID alone grants <strong>zero access</strong> to your stored documents. When a department enters your ID, DigiIn always requires your explicit approval.
                </div>
              </div>
              <ul className="list-disc pl-4 space-y-1 text-slate-700">
                <li>Contains <strong>Zero Personal Information</strong> (no Aadhaar, DOB, or phone numbers).</li>
                <li>Allows you to reuse verified records across multiple government services.</li>
                <li>Eliminates repeated document re-uploads.</li>
              </ul>
            </div>

            <div className="pt-2 flex justify-end">
              <Button
                variant="primary"
                size="sm"
                onClick={() => setShowAboutModal(false)}
                className="font-bold bg-[#092F4F] hover:bg-[#071F34]"
              >
                Got it
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* B. Show QR Modal */}
      {showQrModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fadeIn">
          <div className="bg-white rounded-2xl max-w-sm w-full p-6 shadow-2xl space-y-4 border border-slate-200 text-center">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2">
              <h3 className="text-sm font-bold text-[#092F4F] m-0">DigiIn In-Person Verification</h3>
              <button
                type="button"
                onClick={() => setShowQrModal(false)}
                className="text-slate-400 hover:text-slate-700 text-lg font-bold"
              >
                ✕
              </button>
            </div>

            {/* QR Code Container */}
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl flex justify-center items-center">
              {qrDataUrl ? (
                <img
                  src={qrDataUrl}
                  alt="DigiIn Verification QR Code"
                  className="w-40 h-40 object-contain rounded-lg"
                />
              ) : (
                <div className="w-40 h-40 flex items-center justify-center text-xs text-slate-400">
                  Generating QR...
                </div>
              )}
            </div>

            <div className="space-y-1">
              <div className="font-mono text-sm font-bold text-[#0B5D9B]">{accountId}</div>
              <div className="text-[11px] text-slate-500">
                6-Digit Counter Code: <strong className="text-slate-900 font-mono text-xs">482 913</strong> (Expires in 08:42)
              </div>
            </div>

            <p className="text-[10px] text-slate-400 m-0">
              Identifier only • Contains zero raw document binaries
            </p>

            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowQrModal(false)}
              className="w-full font-bold"
            >
              Close
            </Button>
          </div>
        </div>
      )}

      {/* C. Claim Detail Modal */}
      {selectedClaim && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fadeIn">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 border border-slate-200">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-sm font-bold text-[#092F4F] m-0">{selectedClaim.title}</h3>
              <button
                type="button"
                onClick={() => setSelectedClaim(null)}
                className="text-slate-400 hover:text-slate-700 text-lg font-bold"
              >
                ✕
              </button>
            </div>

            <div className="text-xs text-slate-700 space-y-2.5">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Status:</span>
                <span className="font-bold text-emerald-800">✓ {selectedClaim.status}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Verification Level:</span>
                <span className="font-bold">{selectedClaim.level}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Issuing Authority:</span>
                <span className="font-bold">{selectedClaim.issuer}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Verified On:</span>
                <span className="font-mono">{selectedClaim.verifiedDate}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Valid Until:</span>
                <span className="font-mono">{selectedClaim.validUntil}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Associated Usages:</span>
                <span className="font-bold text-[#0B5D9B]">{selectedClaim.usedBy}</span>
              </div>
            </div>

            <div className="pt-2 flex justify-end gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSelectedClaim(null)}
                className="text-xs font-bold"
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* D. Revoke Confirmation Modal */}
      {serviceToRevoke && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fadeIn">
          <div className="bg-white rounded-2xl max-w-sm w-full p-6 shadow-2xl space-y-4 border border-slate-200">
            <div className="text-center space-y-2">
              <div className="w-12 h-12 rounded-full bg-red-100 text-red-600 flex items-center justify-center mx-auto text-xl font-bold">
                ⚠️
              </div>
              <h3 className="text-base font-bold text-slate-900 m-0">Revoke Service Access?</h3>
              <p className="text-xs text-slate-500 m-0">
                This service will immediately lose the ability to verify your DigiIn claims. You can re-authorize anytime.
              </p>
            </div>

            <div className="flex items-center gap-3 pt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setServiceToRevoke(null)}
                className="w-full text-xs font-bold"
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={handleConfirmRevoke}
                className="w-full text-xs font-bold bg-red-600 hover:bg-red-700"
              >
                Revoke Access
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
