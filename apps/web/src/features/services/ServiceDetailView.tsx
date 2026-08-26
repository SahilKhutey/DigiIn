import React from "react";
import { Button, Card, Badge } from "../../components/ui";
import { useLanguage } from "../../context/LanguageContext";

export interface ServiceDetailData {
  id: string;
  title: string;
  category: "EDUCATION" | "AGRICULTURE" | "TRANSPORT" | "CIVIC";
  department: string;
  description: string;
  longDescription: string;
  timeDigiIn: string;
  timeTraditional: string;
  requiredClaims: { name: string; issuer: string; isPredicate?: boolean }[];
  withheldAttributes: string[];
  eligibility: string[];
}

export const SERVICE_REGISTRY: Record<string, ServiceDetailData> = {
  srv_scholarship_du: {
    id: "srv_scholarship_du",
    title: "National Merit-cum-Means Scholarship",
    category: "EDUCATION",
    department: "University of Delhi / Ministry of Education",
    description: "Financial assistance for meritorious students from low-income families pursuing higher education.",
    longDescription:
      "This flagship scholarship program provides annual financial grants to eligible higher secondary and university students. By integrating DigiIn, students do not need to scan physical marksheets, income certificates, or caste affidavits. All eligibility assertions are proven via Ed25519-signed cryptographic tokens directly from the CBSE and Revenue registries.",
    timeDigiIn: "2 minutes",
    timeTraditional: "45 minutes + physical notarization",
    requiredClaims: [
      { name: "Sovereign Identity Assertion (Name & DOB)", issuer: "UIDAI eKYC" },
      { name: "State Domicile Certificate", issuer: "State Revenue Dept." },
      { name: "Family Income Eligibility (< ₹2.5L threshold)", issuer: "Revenue Board", isPredicate: true },
      { name: "Class XII Senior Marksheet (>= 60%)", issuer: "CBSE Central Registry" },
    ],
    withheldAttributes: [
      "Full 12-digit Aadhaar number (only masked token passed)",
      "Unredacted physical marksheet scan copies",
      "Parental bank account statements & tax filings",
    ],
    eligibility: [
      "Must have passed Class XII examination with >= 60% aggregate score.",
      "Annual family income must not exceed ₹2,50,000.",
      "Must hold a valid Indian citizenship demographic assertion.",
    ],
  },
  srv_land_subsidy_cg: {
    id: "srv_land_subsidy_cg",
    title: "PM-Kisan & State Agricultural Subsidy",
    category: "AGRICULTURE",
    department: "State Department of Agriculture & Land Records",
    description: "Direct benefit transfer subsidy for verified agricultural landholders and small farmers.",
    longDescription:
      "Provides direct income support and fertilizer subsidy allocations to landowning farmer families. DigiIn automates the verification of Khasra land parcel ownership directly from the State Revenue & Land Records Registry without requiring physical Patwari field inspections.",
    timeDigiIn: "2 minutes",
    timeTraditional: "30 days (Patwari manual field visit)",
    requiredClaims: [
      { name: "Sovereign Identity Assertion", issuer: "UIDAI eKYC" },
      { name: "State Domicile Certificate", issuer: "State Revenue Dept." },
      { name: "Khasra / Land Title Deed Record", issuer: "Land Records Authority" },
      { name: "Bank Account Linking Assertion", issuer: "NPCI DBT Gateway" },
    ],
    withheldAttributes: [
      "Full family property survey records",
      "Historical land tax receipts",
    ],
    eligibility: [
      "Small and marginal farmer families with cultivable landholding.",
      "Land title ownership recorded in authoritative state digitized land registry.",
    ],
  },
  srv_sarathi_dl_renewal: {
    id: "srv_sarathi_dl_renewal",
    title: "Commercial Driver License Renewal (Sarathi)",
    category: "TRANSPORT",
    department: "Ministry of Road Transport and Highways (MoRTH)",
    description: "Instant paperless renewal and endorsement for LMV/TRANS commercial driving licenses.",
    longDescription:
      "Enables commercial and transport vehicle drivers to renew their licenses, update vehicle endorsements, and verify medical fitness self-declarations without queueing at local Regional Transport Offices (RTOs).",
    timeDigiIn: "3 minutes",
    timeTraditional: "14 days (RTO in-person visit)",
    requiredClaims: [
      { name: "Sovereign Identity Assertion", issuer: "UIDAI eKYC" },
      { name: "Existing Sarathi DL Record", issuer: "MoRTH National Registry" },
      { name: "Medical Fitness Self-Declaration", issuer: "Citizen Attested" },
      { name: "State Address Proof", issuer: "State Authority" },
    ],
    withheldAttributes: [
      "Physical plastic DL card confiscation",
      "Biometric fingerprint raw templates",
    ],
    eligibility: [
      "Must hold a non-expired or recently expired driving license on Sarathi.",
      "Zero active judicial driving disqualification orders.",
    ],
  },
  srv_domicile_caste_cert: {
    id: "srv_domicile_caste_cert",
    title: "State Domicile & Category Verification",
    category: "CIVIC",
    department: "Department of Revenue & Social Welfare",
    description: "Cryptographic proof of state residency and community category for public job quotas.",
    longDescription:
      "Allows job applicants and students to prove state residency and reserved category eligibility with zero-knowledge predicates without exposing personal family lineage records to third-party recruiters.",
    timeDigiIn: "1 minute",
    timeTraditional: "21 days (Tehsildar review)",
    requiredClaims: [
      { name: "Sovereign Identity Assertion", issuer: "UIDAI eKYC" },
      { name: "State Domicile Certificate", issuer: "State Revenue Dept." },
      { name: "Category Entitlement Assertion", issuer: "Social Welfare Dept.", isPredicate: true },
    ],
    withheldAttributes: [
      "Complete family lineage documents",
      "Caste genealogical affidavits",
    ],
    eligibility: [
      "Permanent resident of the state for minimum statutory duration.",
      "Valid certificate recorded in state e-District database.",
    ],
  },
};

interface ServiceDetailViewProps {
  serviceId: string;
  onStartService: (serviceId: string) => void;
  onBack: () => void;
}

export const ServiceDetailView: React.FC<ServiceDetailViewProps> = ({
  serviceId,
  onStartService,
  onBack,
}) => {
  const { locale } = useLanguage();
  const hi = locale === "hi";

  const service = SERVICE_REGISTRY[serviceId] || SERVICE_REGISTRY.srv_scholarship_du;

  return (
    <div className="space-y-8 max-w-4xl mx-auto py-4">
      {/* Top Breadcrumb & Back Action */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={onBack}
          className="inline-flex items-center gap-1.5 text-sm font-bold text-[#0B5D9B] hover:underline cursor-pointer"
        >
          ← {hi ? "सार्वजनिक सेवा सूची पर वापस" : "Back to Services Catalog"}
        </button>

        <span className="text-xs font-semibold text-slate-500">
          Service Code: <code className="text-[#092F4F] font-bold">{service.id}</code>
        </span>
      </div>

      {/* Main Header Banner */}
      <div className="bg-white border border-[#CBD5E1] rounded-3xl p-8 md:p-10 shadow-xs space-y-6">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
          <div className="space-y-3 max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-widest text-[#0B5D9B] bg-[#EBF4FA] px-3 py-1 rounded-full border border-[#BAE6FD]">
                {service.department}
              </span>
              <span className="text-xs font-extrabold px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-300">
                ⚡ {service.timeDigiIn} Instant
              </span>
            </div>

            <h1 className="text-2xl md:text-4xl font-extrabold text-[#092F4F] m-0">
              {service.title}
            </h1>

            <p className="text-sm md:text-base text-slate-600 leading-relaxed m-0">
              {service.description}
            </p>
          </div>

          <div className="shrink-0 flex flex-col gap-2">
            <Button
              variant="primary"
              size="lg"
              onClick={() => onStartService(service.id)}
              className="font-bold text-base shadow-sm px-8"
            >
              Start Application with DigiIn →
            </Button>
            <span className="text-[11px] text-center text-slate-500 font-medium">
              🔒 100% Zero Raw Document Uploads
            </span>
          </div>
        </div>

        {/* Time Savings Comparison Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 bg-[#F8FAFC] border border-slate-200 rounded-2xl">
          <div className="space-y-1">
            <div className="text-xs font-bold text-slate-500 uppercase tracking-wide">
              Traditional Physical Process
            </div>
            <div className="text-base font-bold text-red-600 line-through">
              {service.timeTraditional}
            </div>
            <div className="text-xs text-slate-500">
              Requires physical copies, notary attestations & multiple office visits.
            </div>
          </div>

          <div className="space-y-1">
            <div className="text-xs font-bold text-emerald-700 uppercase tracking-wide">
              With DigiIn Verified Claims
            </div>
            <div className="text-base font-extrabold text-emerald-800">
              ⚡ {service.timeDigiIn} (Zero Uploads)
            </div>
            <div className="text-xs text-emerald-700">
              Ed25519-signed verification tokens generated from authoritative registries.
            </div>
          </div>
        </div>
      </div>

      {/* 2-Column Details Layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left: How It Works & Required Claims */}
        <div className="space-y-6">
          <Card variant="default" className="p-6 space-y-4 rounded-2xl bg-white border border-[#CBD5E1]">
            <h3 className="text-lg font-bold text-[#092F4F] m-0">
              ✓ Verified Claims Required
            </h3>
            <p className="text-xs text-slate-600 m-0">
              DigiIn will query these authoritative issuers for verifiable claims only:
            </p>

            <div className="space-y-2.5">
              {service.requiredClaims.map((claim, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-3 p-3 bg-[#F8FAFC] border border-slate-200 rounded-xl text-xs"
                >
                  <span className="text-emerald-600 font-bold text-base leading-none">✓</span>
                  <div>
                    <div className="font-bold text-[#092F4F]">{claim.name}</div>
                    <div className="text-[11px] text-slate-500">Authoritative Issuer: {claim.issuer}</div>
                    {claim.isPredicate && (
                      <span className="inline-block mt-1 text-[10px] font-extrabold text-[#0B5D9B] bg-[#EBF4FA] px-2 py-0.5 rounded border border-[#BAE6FD]">
                        Zero-Knowledge Predicate (Threshold Only)
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card variant="default" className="p-6 space-y-3 rounded-2xl bg-white border border-[#CBD5E1]">
            <h3 className="text-lg font-bold text-[#092F4F] m-0">
              Eligibility Prerequisites
            </h3>
            <ul className="space-y-2 text-xs text-slate-600 list-disc pl-5 m-0">
              {service.eligibility.map((el, i) => (
                <li key={i}>{el}</li>
              ))}
            </ul>
          </Card>
        </div>

        {/* Right: Privacy & Security Protections */}
        <div className="space-y-6">
          <Card variant="default" className="p-6 space-y-4 rounded-2xl bg-white border border-[#CBD5E1]">
            <div className="flex items-center gap-2">
              <span className="text-xl">🛡️</span>
              <h3 className="text-lg font-bold text-[#092F4F] m-0">
                What is NOT Transferred
              </h3>
            </div>
            <p className="text-xs text-slate-600 m-0">
              To protect your sovereign privacy under the DPDP Act 2023:
            </p>

            <div className="space-y-2">
              {service.withheldAttributes.map((attr, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-2 p-3 bg-red-50/70 border border-red-200 rounded-xl text-xs text-red-900"
                >
                  <span className="text-red-600 font-bold">✕</span>
                  <span className="font-medium">{attr}</span>
                </div>
              ))}
            </div>

            <div className="p-3.5 bg-[#EBF4FA] border border-[#BAE6FD] rounded-xl text-xs text-[#092F4F] space-y-1">
              <div className="font-bold">Digital Trust Guarantee:</div>
              <p className="text-[11px] text-slate-600 m-0 leading-relaxed">
                The receiving authority only receives a short-lived, purpose-bound Ed25519 token. You can audit or revoke active grants anytime from your Citizen Consent Dashboard.
              </p>
            </div>
          </Card>

          {/* Bottom Action Card */}
          <div className="p-6 bg-gradient-to-br from-[#092F4F] to-[#0B5D9B] text-white rounded-2xl shadow-xs space-y-4">
            <h3 className="text-lg font-bold m-0 text-white">
              Ready to Apply?
            </h3>
            <p className="text-xs text-slate-200 m-0 leading-relaxed">
              Experience the fast 2-minute citizen flow with zero document re-uploads.
            </p>
            <Button
              variant="secondary"
              size="md"
              fullWidth
              onClick={() => onStartService(service.id)}
              className="bg-white text-[#092F4F] font-bold shadow-xs hover:bg-slate-100"
            >
              Start Application Now →
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
