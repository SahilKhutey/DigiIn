import React from "react";
import { useLanguage } from "../context/LanguageContext";
import { useAuth } from "../context/AuthContext";

export type AppView =
  | "LANDING"
  | "SERVICES"
  | "ABOUT"
  | "HOW_IT_WORKS"
  | "FOR_CITIZENS"
  | "FOR_ORGANISATIONS"
  | "SECURITY"
  | "ACCESSIBILITY"
  | "HELP"
  | "CONTACT"
  | "TERMS"
  | "PRIVACY"
  | "SIGN_IN"
  | "OTP"
  | "ONBOARDING"
  | "SCHOLARSHIP"
  | "JOURNEY"
  | "WALLET"
  | "VERIFIER"
  | "CONSENT"
  | "DEMO_LAB"
  | "SCANNER";


interface GovHeaderProps {
  currentView: AppView;
  onViewChange: (view: AppView) => void;
  onOpenScanner?: () => void;
  onOpenEkyc?: () => void;
}

export const GovHeader: React.FC<GovHeaderProps> = ({
  currentView,
  onViewChange,
  onOpenScanner,
  onOpenEkyc,
}) => {
  const { locale, setLocale, t } = useLanguage();
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <header className="ux4g-header border-b border-[#CBD5E1] bg-white shadow-xs sticky top-0 z-50">
      {/* 1. Official Government Top Banner */}
      <div className="bg-[#092F4F] text-white text-xs py-1 px-4 md:px-8 flex items-center justify-between border-b border-[#1A3B5C]">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-300">भारत सरकार</span>
          <span className="text-slate-500">•</span>
          <span className="text-slate-300">Government of India</span>
        </div>
        <div className="flex items-center gap-4 text-[11px]">
          <span className="hidden sm:inline text-slate-300">
            Digital India Initiative • UX4G 3.0 Standard
          </span>
          <div className="flex items-center gap-1 border-l border-slate-700 pl-3">
            <button
              type="button"
              onClick={() => setLocale(locale === "en" ? "hi" : "en")}
              className="text-white hover:text-cyan-300 font-bold cursor-pointer transition-colors"
              aria-label="Switch Language"
            >
              {locale === "en" ? "हिन्दी (HI)" : "English (EN)"}
            </button>
          </div>
        </div>
      </div>

      {/* 2. Main Identity & Navigation Bar */}
      <div className="max-w-7xl mx-auto px-4 md:px-8 py-3 flex flex-wrap items-center justify-between gap-4">
        {/* Brand & National Identity */}
        <div
          className="flex items-center gap-3 cursor-pointer select-none"
          onClick={() => onViewChange("LANDING")}
        >
          <div className="w-10 h-10 rounded-lg bg-[#0B5D9B] text-white flex items-center justify-center font-extrabold text-xl shadow-sm border border-[#074B7D]">
            D
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-xl text-[#092F4F] tracking-tight">
                DigiIn
              </span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-[#EBF4FA] text-[#0B5D9B] border border-[#BAE6FD]">
                UX4G 3.0
              </span>
            </div>
            <p className="text-xs text-slate-500 m-0">
              {t("app.subtitle")}
            </p>
          </div>
        </div>

        {/* Public Navigation Links */}
        <nav className="hidden lg:flex items-center gap-1 text-xs font-bold" aria-label="Public Navigation">
          <button
            type="button"
            className={`px-2.5 py-1.5 rounded-lg transition-colors cursor-pointer ${
              currentView === "ABOUT" ? "bg-[#EBF4FA] text-[#0B5D9B]" : "text-slate-600 hover:text-[#092F4F]"
            }`}
            onClick={() => onViewChange("ABOUT")}
          >
            About
          </button>
          <button
            type="button"
            className={`px-2.5 py-1.5 rounded-lg transition-colors cursor-pointer ${
              currentView === "HOW_IT_WORKS" ? "bg-[#EBF4FA] text-[#0B5D9B]" : "text-slate-600 hover:text-[#092F4F]"
            }`}
            onClick={() => onViewChange("HOW_IT_WORKS")}
          >
            How It Works
          </button>
          <button
            type="button"
            className={`px-2.5 py-1.5 rounded-lg transition-colors cursor-pointer ${
              currentView === "FOR_CITIZENS" ? "bg-[#EBF4FA] text-[#0B5D9B]" : "text-slate-600 hover:text-[#092F4F]"
            }`}
            onClick={() => onViewChange("FOR_CITIZENS")}
          >
            For Citizens
          </button>
          <button
            type="button"
            className={`px-2.5 py-1.5 rounded-lg transition-colors cursor-pointer ${
              currentView === "FOR_ORGANISATIONS" ? "bg-[#EBF4FA] text-[#0B5D9B]" : "text-slate-600 hover:text-[#092F4F]"
            }`}
            onClick={() => onViewChange("FOR_ORGANISATIONS")}
          >
            For Organisations
          </button>
          <button
            type="button"
            className={`px-2.5 py-1.5 rounded-lg transition-colors cursor-pointer ${
              currentView === "SECURITY" ? "bg-[#EBF4FA] text-[#0B5D9B]" : "text-slate-600 hover:text-[#092F4F]"
            }`}
            onClick={() => onViewChange("SECURITY")}
          >
            Security
          </button>
          <button
            type="button"
            className={`px-2.5 py-1.5 rounded-lg transition-colors cursor-pointer ${
              currentView === "HELP" ? "bg-[#EBF4FA] text-[#0B5D9B]" : "text-slate-600 hover:text-[#092F4F]"
            }`}
            onClick={() => onViewChange("HELP")}
          >
            Help & FAQ
          </button>
        </nav>

        {/* Perspective & Session Action Section */}
        <div className="flex items-center flex-wrap gap-2">
          {/* User Session Pill */}
          {isAuthenticated && user ? (
            <div className="flex items-center gap-2 bg-[#EBF4FA] px-3 py-1.5 rounded-xl border border-[#BAE6FD]">
              <span className="text-xs font-bold text-[#092F4F]">👤 {user.name}</span>
              <code className="text-[11px] font-mono font-bold text-[#0B5D9B] bg-white px-1.5 py-0.5 rounded border border-[#CBD5E1]">
                {user.digiinId}
              </code>
              <button
                type="button"
                onClick={() => {
                  logout();
                  onViewChange("SIGN_IN");
                }}
                className="text-[11px] font-bold text-slate-500 hover:text-red-700 transition-colors cursor-pointer ml-1"
                title="Sign Out"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => onViewChange("SIGN_IN")}
              className="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-[#0B5D9B] text-white hover:bg-[#074B7D] transition-all cursor-pointer shadow-xs"
            >
              Sign In
            </button>
          )}

          {/* Perspective / Journey Switcher Tabs */}
          <div className="flex items-center flex-wrap gap-1 bg-[#F1F5F9] p-1 rounded-xl border border-[#CBD5E1]">
            <button
              type="button"
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                currentView === "SERVICES"
                  ? "bg-[#0B5D9B] text-white shadow-sm"
                  : "text-[#475569] hover:text-[#092F4F] hover:bg-slate-200"
              }`}
              onClick={() => onViewChange("SERVICES")}
              aria-label="Public Services Directory"
            >
              🏛️ Services
            </button>

            <button
              type="button"
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                currentView === "SCHOLARSHIP"
                  ? "bg-green-700 text-white shadow-sm"
                  : "text-[#475569] hover:text-[#092F4F] hover:bg-slate-200"
              }`}
              onClick={() => onViewChange("SCHOLARSHIP")}
              aria-label="Start Scholarship Journey"
            >
              🎓 Scholarship
            </button>


            <button
              type="button"
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                currentView === "JOURNEY"
                  ? "bg-[#0B5D9B] text-white shadow-sm"
                  : "text-[#475569] hover:text-[#092F4F] hover:bg-slate-200"
              }`}
              onClick={() => onViewChange("JOURNEY")}
            >
              🚀 Verify Flow
            </button>

            <button
              type="button"
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                currentView === "WALLET"
                  ? "bg-[#0B5D9B] text-white shadow-sm"
                  : "text-[#475569] hover:text-[#092F4F] hover:bg-slate-200"
              }`}
              onClick={() => onViewChange("WALLET")}
            >
              🗂️ Vault
            </button>

            <button
              type="button"
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                currentView === "VERIFIER"
                  ? "bg-[#0B5D9B] text-white shadow-sm"
                  : "text-[#475569] hover:text-[#092F4F] hover:bg-slate-200"
              }`}
              onClick={() => onViewChange("VERIFIER")}
            >
              🏛️ Verifier
            </button>

            <button
              type="button"
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                currentView === "CONSENT"
                  ? "bg-[#0B5D9B] text-white shadow-sm"
                  : "text-[#475569] hover:text-[#092F4F] hover:bg-slate-200"
              }`}
              onClick={() => onViewChange("CONSENT")}
            >
              🛡️ Audit
            </button>

            <button
              type="button"
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                currentView === "DEMO_LAB"
                  ? "bg-purple-700 text-white shadow-sm"
                  : "text-[#475569] hover:text-[#092F4F] hover:bg-slate-200"
              }`}
              onClick={() => onViewChange("DEMO_LAB")}
              aria-label="Verification Demo Lab"
            >
              ⚗️ Lab
            </button>

            {onOpenScanner && (
              <button
                type="button"
                onClick={onOpenScanner}
                className="px-2 py-1 rounded-lg text-xs font-bold text-[#0B5D9B] bg-white border border-[#CBD5E1] hover:bg-[#EBF4FA] transition-all cursor-pointer"
                title="Air-gapped offline asymmetric cryptographic proof verification"
              >
                📷 QR
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
