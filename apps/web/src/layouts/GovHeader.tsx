import React, { useState, useEffect } from "react";
import { useLanguage } from "../context/LanguageContext";
import { useAuth } from "../context/AuthContext";

export type AppView =
  | "LANDING"
  | "SERVICES"
  | "SERVICE_DETAIL"
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
  | "DASHBOARD"
  | "IDENTITY"
  | "DOCUMENTS"
  | "DOCUMENT_DETAIL"
  | "UPLOAD"
  | "SCHOLARSHIP"
  | "JOURNEY"
  | "WALLET"
  | "VERIFIER"
  | "CONSENT"
  | "PROOF_RECEIPT"
  | "AUDIT_TRAIL"
  | "SCANNER"
  | "ISSUER_CONSOLE"
  | "VERIFIER_CONSOLE"
  | "ADMIN_CONSOLE"
  | "CREDENTIALS"
  | "NOTIFICATIONS"
  | "VERIFICATION"
  | "SETTINGS"
  | "CORRECTIONS"
  | "SUPPORT"
  | "DEMO_LAB"
  | "ZK_STUDIO"
  | "MOCK_PORTAL";

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
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Close mobile drawer on ESC key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsMobileMenuOpen(false);
      }
    };
    if (isMobileMenuOpen) {
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isMobileMenuOpen]);

  const handleNavClick = (view: AppView) => {
    onViewChange(view);
    setIsMobileMenuOpen(false);
  };

  const isPublicActive = (view: AppView) => currentView === view;

  return (
    <header
      className={`ux4g-header flex flex-col w-full sticky top-0 z-50 transition-all duration-200 ${
        isScrolled
          ? "bg-white/95 backdrop-blur-md shadow-xs border-b border-slate-200"
          : "bg-white border-b border-slate-200"
      }`}
    >
      {/* 1. Official Government Top Strip */}
      <div className="bg-[#092F4F] text-white text-[11px] py-1.5 px-4 md:px-8 flex items-center justify-between border-b border-[#1A3B5C]">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-200">भारत सरकार</span>
          <span className="text-slate-500">•</span>
          <span className="text-slate-200">Government of India</span>
        </div>
        <div className="flex items-center gap-4 text-[11px]">
          <span className="hidden sm:inline text-slate-300">
            Digital Public Infrastructure • UX4G 3.0 Standard
          </span>
          <div className="flex items-center gap-1 border-l border-slate-700 pl-3">
            <button
              type="button"
              onClick={() => setLocale(locale === "en" ? "hi" : "en")}
              className="text-white hover:text-cyan-300 font-bold cursor-pointer transition-colors px-1 py-0.5 rounded focus-visible:outline focus-visible:outline-2 focus-visible:outline-white"
              aria-label="Switch Language"
            >
              {locale === "en" ? "हिन्दी (HI)" : "English (EN)"}
            </button>
          </div>
        </div>
      </div>

      {/* 2. Main Navigation Bar (Clean, Structured Single Row) */}
      <div className="max-w-7xl w-full mx-auto px-4 md:px-8 h-16 flex items-center justify-between gap-6">
        {/* Brand & National Identity */}
        <div
          className="brand flex items-center gap-3 cursor-pointer select-none"
          onClick={() => handleNavClick("LANDING")}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") handleNavClick("LANDING");
          }}
          aria-label="DigiIn Home"
        >
          <div className="w-9 h-9 rounded-xl bg-[#0B5D9B] text-white flex items-center justify-center font-extrabold text-lg shadow-xs border border-[#074B7D]">
            D
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-xl text-[#092F4F] tracking-tight leading-none">
                DigiIn
              </span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-[#EBF4FA] text-[#0B5D9B] border border-[#BAE6FD]">
                UX4G 3.0
              </span>
            </div>
            <p className="text-[11px] text-slate-500 m-0 leading-none mt-1">
              {t("app.subtitle")}
            </p>
          </div>
        </div>

        {/* Desktop Primary Navigation */}
        <nav className="hidden lg:flex items-center gap-1 text-sm font-semibold" aria-label="Main Navigation">
          <button
            type="button"
            className={`px-3.5 py-2 rounded-lg transition-colors cursor-pointer text-xs font-semibold ${
              isPublicActive("LANDING")
                ? "bg-[#EBF4FA] text-[#0B5D9B] font-bold"
                : "text-slate-600 hover:text-[#092F4F] hover:bg-slate-100"
            }`}
            onClick={() => handleNavClick("LANDING")}
          >
            Home
          </button>
          <button
            type="button"
            className={`px-3.5 py-2 rounded-lg transition-colors cursor-pointer text-xs font-semibold ${
              isPublicActive("SERVICES")
                ? "bg-[#EBF4FA] text-[#0B5D9B] font-bold"
                : "text-slate-600 hover:text-[#092F4F] hover:bg-slate-100"
            }`}
            onClick={() => handleNavClick("SERVICES")}
          >
            Services
          </button>
          <button
            type="button"
            className={`px-3.5 py-2 rounded-lg transition-colors cursor-pointer text-xs font-semibold ${
              isPublicActive("HOW_IT_WORKS")
                ? "bg-[#EBF4FA] text-[#0B5D9B] font-bold"
                : "text-slate-600 hover:text-[#092F4F] hover:bg-slate-100"
            }`}
            onClick={() => handleNavClick("HOW_IT_WORKS")}
          >
            How it Works
          </button>
          <button
            type="button"
            className={`px-3.5 py-2 rounded-lg transition-colors cursor-pointer text-xs font-semibold ${
              isPublicActive("SECURITY")
                ? "bg-[#EBF4FA] text-[#0B5D9B] font-bold"
                : "text-slate-600 hover:text-[#092F4F] hover:bg-slate-100"
            }`}
            onClick={() => handleNavClick("SECURITY")}
          >
            Trust
          </button>
          <button
            type="button"
            className={`px-3.5 py-2 rounded-lg transition-colors cursor-pointer text-xs font-semibold ${
              isPublicActive("HELP") || isPublicActive("SUPPORT")
                ? "bg-[#EBF4FA] text-[#0B5D9B] font-bold"
                : "text-slate-600 hover:text-[#092F4F] hover:bg-slate-100"
            }`}
            onClick={() => handleNavClick("HELP")}
          >
            Support
          </button>
        </nav>

        {/* Right Header Actions */}
        <div className="flex items-center gap-3">
          {/* User Session Pill / Sign In */}
          {isAuthenticated && user ? (
            <div className="hidden sm:flex items-center gap-2 bg-[#EBF4FA] px-3 py-1.5 rounded-xl border border-[#BAE6FD]">
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
              onClick={() => handleNavClick("SIGN_IN")}
              className="hidden sm:inline-flex items-center justify-center px-4 py-2 rounded-xl text-xs font-bold text-[#0B5D9B] bg-[#EBF4FA] hover:bg-[#D8ECF8] border border-[#BAE6FD] transition-all cursor-pointer"
            >
              Sign In
            </button>
          )}

          {/* Primary Call to Action Button */}
          <button
            type="button"
            onClick={() => handleNavClick("SCHOLARSHIP")}
            className="inline-flex items-center justify-center px-4 py-2 rounded-xl text-xs font-bold bg-[#0B5D9B] hover:bg-[#074B7D] active:bg-[#053659] text-white shadow-xs transition-all cursor-pointer focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#0B5D9B]"
          >
            Get Started →
          </button>

          {/* Mobile Hamburger Toggle Button */}
          <button
            type="button"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="lg:hidden p-2 rounded-lg text-slate-700 hover:text-[#092F4F] hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#0B5D9B] cursor-pointer"
            aria-label={isMobileMenuOpen ? "Close menu" : "Open menu"}
            aria-expanded={isMobileMenuOpen}
          >
            {isMobileMenuOpen ? (
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* 3. Structured Platform Perspectives & Demos Toolbar */}
      <div className="bg-[#F8FAFC] border-t border-[#E2E8F0] py-1.5 px-4 md:px-8">
        <div className="max-w-7xl mx-auto flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-1.5 overflow-x-auto py-0.5 max-w-full">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mr-1 hidden sm:inline">
              Workspaces:
            </span>

            <button
              type="button"
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer shrink-0 ${
                currentView === "SERVICES"
                  ? "bg-[#0B5D9B] text-white shadow-2xs"
                  : "text-[#475569] hover:text-[#092F4F] hover:bg-slate-200"
              }`}
              onClick={() => handleNavClick("SERVICES")}
            >
              🏛️ Services
            </button>

            <button
              type="button"
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer shrink-0 ${
                currentView === "SCHOLARSHIP"
                  ? "bg-emerald-700 text-white shadow-2xs"
                  : "text-[#475569] hover:text-[#092F4F] hover:bg-slate-200"
              }`}
              onClick={() => handleNavClick("SCHOLARSHIP")}
            >
              🎓 Scholarship
            </button>

            <button
              type="button"
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer shrink-0 ${
                currentView === "JOURNEY"
                  ? "bg-[#0B5D9B] text-white shadow-2xs"
                  : "text-[#475569] hover:text-[#092F4F] hover:bg-slate-200"
              }`}
              onClick={() => handleNavClick("JOURNEY")}
            >
              🚀 Verify Flow
            </button>

            <button
              type="button"
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer shrink-0 ${
                currentView === "WALLET"
                  ? "bg-[#0B5D9B] text-white shadow-2xs"
                  : "text-[#475569] hover:text-[#092F4F] hover:bg-slate-200"
              }`}
              onClick={() => handleNavClick("WALLET")}
            >
              🗂️ Vault
            </button>

            <button
              type="button"
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer shrink-0 ${
                currentView === "VERIFIER"
                  ? "bg-[#0B5D9B] text-white shadow-2xs"
                  : "text-[#475569] hover:text-[#092F4F] hover:bg-slate-200"
              }`}
              onClick={() => handleNavClick("VERIFIER")}
            >
              🏛️ Verifier Console
            </button>

            <button
              type="button"
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer shrink-0 ${
                currentView === "CONSENT"
                  ? "bg-[#0B5D9B] text-white shadow-2xs"
                  : "text-[#475569] hover:text-[#092F4F] hover:bg-slate-200"
              }`}
              onClick={() => handleNavClick("CONSENT")}
            >
              🛡️ Consent & Audit
            </button>

            <button
              type="button"
              className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer shrink-0 ${
                currentView === "DEMO_LAB"
                  ? "bg-purple-700 text-white shadow-2xs"
                  : "text-[#475569] hover:text-[#092F4F] hover:bg-slate-200"
              }`}
              onClick={() => handleNavClick("DEMO_LAB")}
            >
              ⚗️ Lab
            </button>
          </div>

          {onOpenScanner && (
            <button
              type="button"
              onClick={onOpenScanner}
              className="px-2.5 py-1 rounded-lg text-xs font-bold text-[#0B5D9B] bg-white border border-[#CBD5E1] hover:bg-[#EBF4FA] transition-all cursor-pointer shrink-0"
              title="Air-gapped offline asymmetric cryptographic proof verification"
            >
              📷 Offline QR Scanner
            </button>
          )}
        </div>
      </div>

      {/* 4. Interactive Mobile Drawer Menu (Accessible & Responsive) */}
      {isMobileMenuOpen && (
        <div className="lg:hidden fixed inset-0 top-[115px] z-40 bg-slate-900/60 backdrop-blur-xs flex flex-col justify-start">
          <div className="bg-white border-b border-[#CBD5E1] p-6 shadow-xl space-y-6 max-h-[calc(100vh-120px)] overflow-y-auto">
            <div className="space-y-1">
              <div className="text-xs font-extrabold uppercase text-slate-400 tracking-wider mb-2">
                Public Navigation
              </div>
              <button
                type="button"
                onClick={() => handleNavClick("SERVICES")}
                className={`w-full text-left px-4 py-2.5 rounded-xl font-bold text-sm ${
                  isPublicActive("SERVICES") ? "bg-[#EBF4FA] text-[#0B5D9B]" : "text-slate-700 hover:bg-slate-50"
                }`}
              >
                Services
              </button>
              <button
                type="button"
                onClick={() => handleNavClick("HOW_IT_WORKS")}
                className={`w-full text-left px-4 py-2.5 rounded-xl font-bold text-sm ${
                  isPublicActive("HOW_IT_WORKS") ? "bg-[#EBF4FA] text-[#0B5D9B]" : "text-slate-700 hover:bg-slate-50"
                }`}
              >
                How it works
              </button>
              <button
                type="button"
                onClick={() => handleNavClick("SECURITY")}
                className={`w-full text-left px-4 py-2.5 rounded-xl font-bold text-sm ${
                  isPublicActive("SECURITY") ? "bg-[#EBF4FA] text-[#0B5D9B]" : "text-slate-700 hover:bg-slate-50"
                }`}
              >
                Trust
              </button>
              <button
                type="button"
                onClick={() => handleNavClick("HELP")}
                className={`w-full text-left px-4 py-2.5 rounded-xl font-bold text-sm ${
                  isPublicActive("HELP") ? "bg-[#EBF4FA] text-[#0B5D9B]" : "text-slate-700 hover:bg-slate-50"
                }`}
              >
                Support
              </button>
            </div>

            <div className="pt-4 border-t border-slate-200 space-y-3">
              {isAuthenticated && user ? (
                <div className="flex items-center justify-between bg-[#EBF4FA] p-3 rounded-xl">
                  <div>
                    <div className="text-xs font-bold text-[#092F4F]">{user.name}</div>
                    <code className="text-[11px] text-[#0B5D9B]">{user.digiinId}</code>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      logout();
                      setIsMobileMenuOpen(false);
                    }}
                    className="text-xs font-bold text-red-700 px-2 py-1 rounded bg-white"
                  >
                    Sign Out
                  </button>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => handleNavClick("SIGN_IN")}
                  className="w-full py-2.5 rounded-xl text-sm font-bold text-[#0B5D9B] bg-[#EBF4FA] border border-[#BAE6FD] text-center"
                >
                  Sign In to DigiIn
                </button>
              )}

              <button
                type="button"
                onClick={() => handleNavClick("SCHOLARSHIP")}
                className="w-full py-3 rounded-xl text-sm font-bold bg-[#0B5D9B] text-white shadow-md text-center"
              >
                Start Verification Journey →
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};
