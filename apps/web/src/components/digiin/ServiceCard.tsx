export interface PlatformService {
  id: string;
  title: string;
  category: "EDUCATION" | "AGRICULTURE" | "TRANSPORT" | "CIVIC" | string;
  department: string;
  description: string;
  verificationSpeed?: string;
  manualAlternativeTime?: string;
  requiredClaims?: string[];
  status?: "ACTIVE" | "SANDBOX_READY" | string;
}

export interface ServiceCardProps {
  service: PlatformService;
  onApply: (service: PlatformService) => void;
  onViewDetails?: (service: PlatformService) => void;
}

export const ServiceCard: React.FC<ServiceCardProps> = ({
  service,
  onApply,
  onViewDetails,
}) => {
  return (
    <article
      className="service-card group flex flex-col justify-between rounded-2xl border border-[#CBD5E1] bg-white p-6 shadow-xs transition-all duration-200 hover:-translate-y-1 hover:border-[#0B5D9B] hover:shadow-md"
      aria-labelledby={`service-heading-${service.id}`}
    >
      <div>
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider bg-[#EBF4FA] text-[#0B5D9B] border border-[#CBD5E1]">
            {service.category}
          </span>
          <span className="inline-flex items-center gap-1 text-xs font-extrabold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
            ⚡ {service.verificationSpeed || "2 mins"} vs {service.manualAlternativeTime || "45 mins"}
          </span>
        </div>

        <h3
          id={`service-heading-${service.id}`}
          className="text-lg font-bold text-[#092F4F] mb-1 group-hover:text-[#0B5D9B] transition-colors"
        >
          {service.title}
        </h3>
        <p className="text-xs text-[#475569] font-medium mb-3">
          🏛️ {service.department}
        </p>
        <p className="text-sm text-[#334155] line-clamp-3 mb-4 leading-relaxed">
          {service.description}
        </p>

        {service.requiredClaims && service.requiredClaims.length > 0 && (
          <div className="mb-4 bg-slate-50 p-3 rounded-xl border border-slate-200">
            <span className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Required Claims:
            </span>
            <ul className="text-xs text-slate-600 space-y-1">
              {service.requiredClaims.slice(0, 3).map((claim: string, idx: number) => (
                <li key={idx} className="flex items-center gap-1.5">
                  <span className="text-blue-600 font-bold">✓</span> {claim}
                </li>
              ))}
              {service.requiredClaims.length > 3 && (
                <li className="text-slate-400 italic">
                  +{service.requiredClaims.length - 3} more claims
                </li>
              )}
            </ul>
          </div>
        )}
      </div>

      <div className="flex flex-col sm:flex-row gap-2 pt-4 border-t border-slate-100">
        <button
          type="button"
          onClick={() => onApply(service)}
          className="btn-primary flex-1 inline-flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl text-sm font-bold text-white bg-[#0B5D9B] hover:bg-[#084B7D] active:scale-98 transition-all cursor-pointer shadow-xs focus:ring-2 focus:ring-[#0B5D9B] focus:ring-offset-2"
        >
          Apply with DigiIn &rarr;
        </button>
        {onViewDetails && (
          <button
            type="button"
            onClick={() => onViewDetails(service)}
            className="btn-secondary inline-flex items-center justify-center px-3 py-2.5 rounded-xl text-sm font-semibold text-[#092F4F] bg-[#F8FAFC] border border-[#CBD5E1] hover:bg-[#E2E8F0] active:scale-98 transition-all cursor-pointer"
          >
            Explore Details
          </button>
        )}
      </div>
    </article>
  );
};
