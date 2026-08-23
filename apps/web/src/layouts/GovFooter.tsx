import React from "react";
import { AppView } from "./GovHeader";

interface GovFooterProps {
  onNavigate?: (view: AppView) => void;
}

export const GovFooter: React.FC<GovFooterProps> = ({ onNavigate }) => {
  return (
    <footer className="ux4g-footer bg-[#092F4F] text-slate-300 mt-20 border-t-4 border-[#0B5D9B]">
      {/* Top Footer Pillars */}
      <div className="max-w-7xl mx-auto px-4 md:px-8 py-10 grid grid-cols-1 md:grid-cols-4 gap-8">
        {/* Col 1: Platform Mission */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded bg-[#0B5D9B] text-white flex items-center justify-center font-bold text-sm">
              D
            </div>
            <span className="font-extrabold text-lg text-white">DigiIn</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed m-0">
            Sovereign credential & document verification platform for Indian Digital Public Services. Enforcing zero raw document transfers with cryptographically signed verifiable claims.
          </p>
          <div className="flex items-center gap-2 pt-1">
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold bg-[#102A43] text-emerald-300 px-2.5 py-1 rounded border border-emerald-500/30">
              ✓ WCAG 2.1 AA Compliant
            </span>
          </div>
        </div>

        {/* Col 2: Citizen Trust Framework */}
        <div className="space-y-2 text-xs">
          <h4 className="text-white font-bold uppercase tracking-wider text-xs border-b border-slate-700 pb-2 m-0">
            Trust & Security
          </h4>
          <ul className="space-y-1.5 text-slate-300 list-none p-0 m-0">
            <li>• Zero Document Retention</li>
            <li>• Ed25519 Signed Verifiable Proofs</li>
            <li>• Granular Purpose-Bound Consent</li>
            <li>• Air-gapped Offline QR Validation</li>
            <li>• RFC 7517 Public JWKS Discovery</li>
          </ul>
        </div>

        {/* Col 3: Public Navigation */}
        <div className="space-y-2 text-xs">
          <h4 className="text-white font-bold uppercase tracking-wider text-xs border-b border-slate-700 pb-2 m-0">
            Public Portal
          </h4>
          <ul className="space-y-1.5 text-slate-300 list-none p-0 m-0">
            <li>
              <button
                type="button"
                className="text-slate-300 hover:text-white cursor-pointer transition-colors"
                onClick={() => onNavigate?.("ABOUT")}
              >
                About DigiIn
              </button>
            </li>
            <li>
              <button
                type="button"
                className="text-slate-300 hover:text-white cursor-pointer transition-colors"
                onClick={() => onNavigate?.("HOW_IT_WORKS")}
              >
                How It Works
              </button>
            </li>
            <li>
              <button
                type="button"
                className="text-slate-300 hover:text-white cursor-pointer transition-colors"
                onClick={() => onNavigate?.("FOR_CITIZENS")}
              >
                For Citizens
              </button>
            </li>
            <li>
              <button
                type="button"
                className="text-slate-300 hover:text-white cursor-pointer transition-colors"
                onClick={() => onNavigate?.("FOR_ORGANISATIONS")}
              >
                For Organisations
              </button>
            </li>
            <li>
              <button
                type="button"
                className="text-slate-300 hover:text-white cursor-pointer transition-colors"
                onClick={() => onNavigate?.("HELP")}
              >
                Help & FAQ
              </button>
            </li>
            <li>
              <button
                type="button"
                className="text-slate-300 hover:text-white cursor-pointer transition-colors"
                onClick={() => onNavigate?.("CONTACT")}
              >
                Contact Desk
              </button>
            </li>
          </ul>
        </div>

        {/* Col 4: Diagnostics & Support Reference */}
        <div className="space-y-2 text-xs">
          <h4 className="text-white font-bold uppercase tracking-wider text-xs border-b border-slate-700 pb-2 m-0">
            Audit & Support
          </h4>
          <p className="text-slate-300 text-xs leading-relaxed m-0">
            Every transaction generates an immutable opaque diagnostic reference:
          </p>
          <div className="bg-[#102A43] p-2.5 rounded border border-slate-700 font-mono text-[11px] text-cyan-300 select-all">
            REF: DIGIIN-PROD-2026-UX4G
          </div>
          <p className="text-[11px] text-slate-400 m-0">
            Complies with Digital Personal Data Protection (DPDP) Act 2023.
          </p>
        </div>
      </div>

      {/* Bottom Legal & Attribution */}
      <div className="bg-[#051E33] py-4 px-4 md:px-8 border-t border-slate-800 text-center text-xs text-slate-400">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>
            Designed following UX4G 3.0 Guidelines for Government of India Portals.
          </span>
          <div className="flex items-center gap-4">
            <button
              type="button"
              onClick={() => onNavigate?.("PRIVACY")}
              className="text-slate-400 hover:text-white transition-colors cursor-pointer"
            >
              Privacy Policy
            </button>
            <span>•</span>
            <button
              type="button"
              onClick={() => onNavigate?.("TERMS")}
              className="text-slate-400 hover:text-white transition-colors cursor-pointer"
            >
              Terms of Service
            </button>
            <span>•</span>
            <button
              type="button"
              onClick={() => onNavigate?.("ACCESSIBILITY")}
              className="text-slate-400 hover:text-white transition-colors cursor-pointer"
            >
              Accessibility Statement
            </button>
          </div>
        </div>
      </div>
    </footer>
  );
};
