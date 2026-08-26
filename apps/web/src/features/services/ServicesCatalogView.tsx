import React, { useState } from "react";
import { Button, Card, Badge } from "../../components/ui";
import { useLanguage } from "../../context/LanguageContext";

interface ServiceItem {
  id: string;
  title: string;
  category: "EDUCATION" | "AGRICULTURE" | "TRANSPORT" | "CIVIC";
  department: string;
  description: string;
  timeDigiIn: string;
  timeTraditional: string;
  requiredClaims: string[];
  status: "ACTIVE" | "SANDBOX_READY";
}

const SERVICES: ServiceItem[] = [
  {
    id: "srv_scholarship_du",
    title: "National Merit-cum-Means Scholarship",
    category: "EDUCATION",
    department: "University of Delhi / Ministry of Education",
    description: "Financial assistance for meritorious students from low-income families pursuing higher education.",
    timeDigiIn: "2 minutes",
    timeTraditional: "45 minutes + physical attestation",
    requiredClaims: [
      "Sovereign Identity Assertion",
      "State Domicile Certificate",
      "Income Eligibility (< 2.5L threshold)",
      "CBSE Class XII Marksheet (>= 60%)",
    ],
    status: "ACTIVE",
  },
  {
    id: "srv_land_subsidy_cg",
    title: "PM-Kisan & State Agricultural Subsidy",
    category: "AGRICULTURE",
    department: "State Department of Agriculture & Land Records",
    description: "Direct benefit transfer subsidy for verified agricultural landholders and small farmers.",
    timeDigiIn: "2 minutes",
    timeTraditional: "30 days (Patwari inspection)",
    requiredClaims: [
      "Sovereign Identity Assertion",
      "State Domicile Certificate",
      "Khasra / Land Title Deed Record",
      "Bank Account Linking Assertion",
    ],
    status: "ACTIVE",
  },
  {
    id: "srv_sarathi_dl_renewal",
    title: "Commercial Driver License Renewal (Sarathi)",
    category: "TRANSPORT",
    department: "Ministry of Road Transport and Highways (MoRTH)",
    description: "Instant paperless renewal and endorsement for LMV/TRANS commercial driving licenses.",
    timeDigiIn: "3 minutes",
    timeTraditional: "14 days (RTO visit)",
    requiredClaims: [
      "Sovereign Identity Assertion",
      "Existing Sarathi DL Record",
      "Medical Fitness Self-Declaration",
      "State Address Proof",
    ],
    status: "ACTIVE",
  },
  {
    id: "srv_domicile_caste_cert",
    title: "State Domicile & Caste Verification",
    category: "CIVIC",
    department: "Department of Revenue & Social Welfare",
    description: "Cryptographic proof of state residency and community category for public job quotas.",
    timeDigiIn: "1 minute",
    timeTraditional: "21 days (Tehsildar review)",
    requiredClaims: [
      "Sovereign Identity Assertion",
      "State Domicile Certificate",
      "Family Lineage Record",
    ],
    status: "ACTIVE",
  },
];

interface Props {
  onSelectService: (serviceId: string) => void;
  onViewDetails?: (serviceId: string) => void;
  onBackToHome: () => void;
}

export const ServicesCatalogView: React.FC<Props> = ({
  onSelectService,
  onViewDetails,
  onBackToHome,
}) => {
  const { locale } = useLanguage();
  const hi = locale === "hi";

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");

  const filteredServices = SERVICES.filter((s) => {
    const matchesSearch =
      s.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.department.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === "ALL" || s.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-8 max-w-6xl mx-auto px-4 py-4">
      {/* Header Banner */}
      <div className="bg-white border border-[#CBD5E1] rounded-2xl p-6 md:p-8 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-widest text-[#0B5D9B] bg-[#EBF4FA] px-3 py-1 rounded-full border border-[#BAE6FD]">
                Public Service Gateway
              </span>
              <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-300">
                ⚡ 100% Zero-Upload Verification
              </span>
            </div>
            <h1 className="text-2xl md:text-4xl font-extrabold text-[#092F4F] m-0">
              {hi ? "डिजिटल सार्वजनिक सेवाएँ" : "Public Services & Schemes"}
            </h1>
            <p className="text-sm md:text-base text-slate-600 max-w-2xl m-0">
              {hi
                ? "बिना बार-बार दस्तावेज़ अपलोड किए सीधे सत्यापित दावों के साथ सरकारी और शैक्षणिक सेवाओं के लिए आवेदन करें।"
                : "Apply for public, educational, and civic benefits instantly using your DigiIn verified credentials — zero document re-uploads."}
            </p>
          </div>
          <Button variant="outline" size="sm" onClick={onBackToHome}>
            ← {hi ? "मुखपृष्ठ पर लौटें" : "Back to Home"}
          </Button>
        </div>

        {/* Search & Category Filter Bar */}
        <div className="mt-6 pt-6 border-t border-slate-200 flex flex-col md:flex-row items-center gap-4">
          <div className="w-full md:w-80">
            <input
              type="text"
              placeholder={hi ? "सेवा या विभाग खोजें..." : "Search services, schemes, or departments..."}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-[#CBD5E1] text-sm text-[#092F4F] bg-[#F8FAFC] focus:bg-white focus:border-[#0B5D9B] focus:outline-none focus:ring-2 focus:ring-[#0B5D9B]/20"
            />
          </div>

          {/* Category Pills */}
          <div className="flex items-center flex-wrap gap-2 w-full md:w-auto">
            {[
              { id: "ALL", label: hi ? "सभी सेवाएँ" : "All Services" },
              { id: "EDUCATION", label: hi ? "🎓 शिक्षा" : "🎓 Education" },
              { id: "AGRICULTURE", label: hi ? "🌾 कृषि व भूमि" : "🌾 Agriculture" },
              { id: "TRANSPORT", label: hi ? "🚗 परिवहन" : "🚗 Transport" },
              { id: "CIVIC", label: hi ? "📜 नागरिक प्रमाण पत्र" : "📜 Civic" },
            ].map((cat) => (
              <button
                key={cat.id}
                type="button"
                onClick={() => setSelectedCategory(cat.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  selectedCategory === cat.id
                    ? "bg-[#0B5D9B] text-white shadow-xs"
                    : "bg-[#F1F5F9] text-slate-700 hover:bg-slate-200"
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Services Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filteredServices.map((service) => (
          <div
            key={service.id}
            className="bg-white border border-[#CBD5E1] rounded-2xl p-6 shadow-xs hover:border-[#0B5D9B] hover:shadow-md transition-all flex flex-col justify-between"
          >
            <div className="space-y-4">
              {/* Card Header */}
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-[11px] font-bold uppercase tracking-wider text-[#0B5D9B]">
                    {service.department}
                  </div>
                  <h3 className="text-lg font-bold text-[#092F4F] mt-1 m-0">
                    {service.title}
                  </h3>
                </div>
                <span className="text-[11px] font-extrabold px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-300 whitespace-nowrap">
                  ⏱️ {service.timeDigiIn}
                </span>
              </div>

              {/* Description */}
              <p className="text-xs text-slate-600 leading-relaxed m-0">
                {service.description}
              </p>

              {/* Time Savings Comparison */}
              <div className="bg-[#F8FAFC] border border-slate-200 rounded-xl p-3 text-xs space-y-1.5">
                <div className="flex items-center justify-between text-slate-600">
                  <span>Traditional Process:</span>
                  <span className="font-semibold text-red-600 line-through">{service.timeTraditional}</span>
                </div>
                <div className="flex items-center justify-between font-bold text-emerald-800">
                  <span>With DigiIn Verified Claims:</span>
                  <span>⚡ {service.timeDigiIn} (0 Uploads)</span>
                </div>
              </div>

              {/* Required Claims List */}
              <div className="space-y-1.5">
                <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                  Verified Claims Requested:
                </div>
                <div className="space-y-1">
                  {service.requiredClaims.map((claim, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-xs text-[#092F4F]">
                      <span className="text-emerald-600 font-bold">✓</span>
                      <span>{claim}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Card Action */}
            <div className="pt-5 mt-5 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3">
              <button
                type="button"
                onClick={() => (onViewDetails ? onViewDetails(service.id) : onSelectService(service.id))}
                className="text-xs font-bold text-[#0B5D9B] hover:underline cursor-pointer"
              >
                View Details & Eligibility →
              </button>

              <Button
                variant="primary"
                size="sm"
                onClick={() => onSelectService(service.id)}
                className="shadow-xs font-bold"
              >
                {service.id === "srv_scholarship_du" ? "Apply with DigiIn →" : "Start Journey →"}
              </Button>
            </div>
          </div>
        ))}
      </div>

      {filteredServices.length === 0 && (
        <div className="text-center py-12 bg-white rounded-2xl border border-slate-200 p-8 space-y-3">
          <span className="text-4xl">🔍</span>
          <h3 className="text-lg font-bold text-slate-800 m-0">No services found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto m-0">
            Try adjusting your search query or select "All Services" above.
          </p>
        </div>
      )}
    </div>
  );
};
