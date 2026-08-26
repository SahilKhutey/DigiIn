import React from "react";
import { AppView } from "./GovHeader";

interface GovFooterProps {
  onNavigate?: (view: AppView) => void;
}

export const GovFooter: React.FC<GovFooterProps> = ({ onNavigate }) => {
  return (
    <footer className="bg-[#092F4F] text-slate-300 mt-20 border-t border-[#1A3B5C]">
      <div className="max-w-[1200px] mx-auto px-4 md:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 mb-10">
          {/* Brand Col */}
          <div className="md:col-span-5 space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-[#0B5D9B] text-white flex items-center justify-center font-extrabold text-sm border border-[#074B7D]">
                D
              </div>
              <span className="font-extrabold text-xl text-white tracking-tight">DigiIn</span>
            </div>
            <p className="text-sm text-slate-400 max-w-sm m-0">
              Digital trust infrastructure. Verify once. Use anywhere.
            </p>
          </div>

          {/* Links Grid */}
          <div className="md:col-span-7 grid grid-cols-3 gap-6 text-xs">
            {/* Product */}
            <div className="space-y-3">
              <span className="text-white font-bold uppercase tracking-wider block">
                Product
              </span>
              <ul className="space-y-2 list-none p-0 m-0">
                <li>
                  <button
                    type="button"
                    onClick={() => onNavigate?.("SERVICES")}
                    className="text-slate-400 hover:text-white transition-colors cursor-pointer"
                  >
                    Services
                  </button>
                </li>
                <li>
                  <button
                    type="button"
                    onClick={() => onNavigate?.("SCHOLARSHIP")}
                    className="text-slate-400 hover:text-white transition-colors cursor-pointer"
                  >
                    Verification
                  </button>
                </li>
                <li>
                  <button
                    type="button"
                    onClick={() => onNavigate?.("WALLET")}
                    className="text-slate-400 hover:text-white transition-colors cursor-pointer"
                  >
                    Documents
                  </button>
                </li>
              </ul>
            </div>

            {/* Company */}
            <div className="space-y-3">
              <span className="text-white font-bold uppercase tracking-wider block">
                Company
              </span>
              <ul className="space-y-2 list-none p-0 m-0">
                <li>
                  <button
                    type="button"
                    onClick={() => onNavigate?.("ABOUT")}
                    className="text-slate-400 hover:text-white transition-colors cursor-pointer"
                  >
                    About
                  </button>
                </li>
                <li>
                  <button
                    type="button"
                    onClick={() => onNavigate?.("SECURITY")}
                    className="text-slate-400 hover:text-white transition-colors cursor-pointer"
                  >
                    Trust
                  </button>
                </li>
                <li>
                  <button
                    type="button"
                    onClick={() => onNavigate?.("SECURITY")}
                    className="text-slate-400 hover:text-white transition-colors cursor-pointer"
                  >
                    Security
                  </button>
                </li>
              </ul>
            </div>

            {/* Support */}
            <div className="space-y-3">
              <span className="text-white font-bold uppercase tracking-wider block">
                Support
              </span>
              <ul className="space-y-2 list-none p-0 m-0">
                <li>
                  <button
                    type="button"
                    onClick={() => onNavigate?.("HELP")}
                    className="text-slate-400 hover:text-white transition-colors cursor-pointer"
                  >
                    Help & FAQ
                  </button>
                </li>
                <li>
                  <button
                    type="button"
                    onClick={() => onNavigate?.("CONTACT")}
                    className="text-slate-400 hover:text-white transition-colors cursor-pointer"
                  >
                    Contact
                  </button>
                </li>
                <li>
                  <button
                    type="button"
                    onClick={() => onNavigate?.("PRIVACY")}
                    className="text-slate-400 hover:text-white transition-colors cursor-pointer"
                  >
                    Privacy Policy
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Bottom Legal Strip */}
        <div className="pt-6 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <div>© {new Date().getFullYear()} DigiIn. Sovereign Digital Public Infrastructure.</div>
          <div className="flex items-center gap-4">
            <button
              type="button"
              onClick={() => onNavigate?.("PRIVACY")}
              className="text-slate-400 hover:text-white transition-colors cursor-pointer"
            >
              Privacy
            </button>
            <span>•</span>
            <button
              type="button"
              onClick={() => onNavigate?.("TERMS")}
              className="text-slate-400 hover:text-white transition-colors cursor-pointer"
            >
              Terms
            </button>
            <span>•</span>
            <button
              type="button"
              onClick={() => onNavigate?.("ACCESSIBILITY")}
              className="text-slate-400 hover:text-white transition-colors cursor-pointer"
            >
              Accessibility
            </button>
          </div>
        </div>
      </div>
    </footer>
  );
};
