import React, { useState, useEffect } from "react";
import { useLanguage } from "../context/LanguageContext";
import { useAuth } from "../context/AuthContext";
import { GovFooter } from "./GovFooter";
import { AppView } from "./GovHeader";

interface PublicShellProps {
  currentView: AppView;
  onViewChange: (view: AppView) => void;
  onOpenScanner?: () => void;
  children: React.ReactNode;
}

export const PublicShell: React.FC<PublicShellProps> = ({
  currentView,
  onViewChange,
  onOpenScanner,
  children,
}) => {
  const { locale, setLocale, t } = useLanguage();
  const { isAuthenticated, user, logout } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

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
    <div className="min-h-screen flex flex-col bg-[#F3F7FA] text-[#092F4F] font-sans antialiased">
      {/* Skip to Main Content Link for Keyboard Accessibility (WCAG 2.1 AA) */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-[#0B5D9B] focus:text-white focus:font-bold focus:rounded-md focus:shadow-lg"
      >
        Skip to main content
      </a>

      {/* 1. Official Government Top Strip */}
      <div className="bg-[#092F4F] text-white text-xs py-1.5 px-4 md:px-8 flex items-center justify-between border-b border-[#1A3B5C] relative z-50">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-300">भारत सरकार</span>
          <span className="text-slate-500">•</span>
          <span className="text-slate-300">Government of India</span>
        </div>

        <div className="flex items-center gap-3 text-[11px]">
          {/* Surface / Role Switcher Menu */}
          <div className="flex items-center gap-1 bg-[#102A43] px-2 py-0.5 rounded border border-slate-700">
            <span className="text-slate-400 font-medium hidden sm:inline">Role Surface:</span>
            <select
              value={
                currentView === "ISSUER_CONSOLE"
                  ? "ISSUER"
                  : currentView === "VERIFIER_CONSOLE"
                  ? "VERIFIER"
                  : currentView === "ADMIN_CONSOLE" || currentView === "DEMO_LAB"
                  ? "ADMIN"
                  : isAuthenticated
                  ? "CITIZEN"
                  : "PUBLIC"
              }
              onChange={(e) => {
                const role = e.target.value;
                if (role === "PUBLIC") onViewChange("LANDING");
                else if (role === "CITIZEN") onViewChange(isAuthenticated ? "DASHBOARD" : "SIGN_IN");
                else if (role === "ISSUER") onViewChange("ISSUER_CONSOLE");
                else if (role === "VERIFIER") onViewChange("VERIFIER_CONSOLE");
                else if (role === "ADMIN") onViewChange("ADMIN_CONSOLE");
              }}
              className="bg-transparent text-cyan-300 font-bold border-none text-[11px] cursor-pointer focus:outline-none"
              aria-label="Switch User Role Surface"
            >
              <option value="PUBLIC" className="bg-[#092F4F] text-white">🌐 Public Portal</option>
              <option value="CITIZEN" className="bg-[#092F4F] text-white">👤 Citizen App</option>
              <option value="ISSUER" className="bg-[#092F4F] text-white">🏛️ Issuer Console</option>
              <option value="VERIFIER" className="bg-[#092F4F] text-white">🔍 Verifier Portal</option>
              <option value="ADMIN" className="bg-[#092F4F] text-white">⚙️ Admin / Operations</option>
            </select>
          </div>

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

      {/* 2. Public 76px Header */}
      <header className="ux4g-header border-b border-[#CBD5E1] bg-white sticky top-0 z-40 shadow-xs">
        <div className="max-w-7xl w-full mx-auto px-4 md:px-8 min-h-[76px] flex items-center justify-between gap-4">
          {/* Brand */}
          <div
            className="flex items-center gap-3 cursor-pointer select-none py-2"
            onClick={() => handleNavClick("LANDING")}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") handleNavClick("LANDING");
            }}
            aria-label="DigiIn Home"
          >
            <div className="w-10 h-10 rounded-xl bg-[#0B5D9B] text-white flex items-center justify-center font-extrabold text-xl shadow-xs border border-[#074B7D]">
              D
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-xl text-[#092F4F] tracking-tight">
                  DigiIn
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#EBF4FA] text-[#0B5D9B] border border-[#BAE6FD]">
                  UX4G 3.0
                </span>
              </div>
              <p className="text-xs text-slate-500 m-0 leading-none mt-0.5">
                {t("app.subtitle")}
              </p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center gap-1 text-sm font-semibold" aria-label="Main Navigation">
            <button
              type="button"
              className={`px-3 py-2 rounded-lg transition-colors cursor-pointer ${
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
              className={`px-3 py-2 rounded-lg transition-colors cursor-pointer ${
                isPublicActive("SERVICES") || isPublicActive("SERVICE_DETAIL")
                  ? "bg-[#EBF4FA] text-[#0B5D9B] font-bold"
                  : "text-slate-600 hover:text-[#092F4F] hover:bg-slate-100"
              }`}
              onClick={() => handleNavClick("SERVICES")}
            >
              Services
            </button>
            <button
              type="button"
              className={`px-3 py-2 rounded-lg transition-colors cursor-pointer ${
                isPublicActive("HOW_IT_WORKS")
                  ? "bg-[#EBF4FA] text-[#0B5D9B] font-bold"
                  : "text-slate-600 hover:text-[#092F4F] hover:bg-slate-100"
              }`}
              onClick={() => handleNavClick("HOW_IT_WORKS")}
            >
              How It Works
            </button>
            <button
              type="button"
              className={`px-3 py-2 rounded-lg transition-colors cursor-pointer ${
                isPublicActive("ABOUT")
                  ? "bg-[#EBF4FA] text-[#0B5D9B] font-bold"
                  : "text-slate-600 hover:text-[#092F4F] hover:bg-slate-100"
              }`}
              onClick={() => handleNavClick("ABOUT")}
            >
              About
            </button>
            <button
              type="button"
              className={`px-3 py-2 rounded-lg transition-colors cursor-pointer ${
                isPublicActive("HELP")
                  ? "bg-[#EBF4FA] text-[#0B5D9B] font-bold"
                  : "text-slate-600 hover:text-[#092F4F] hover:bg-slate-100"
              }`}
              onClick={() => handleNavClick("HELP")}
            >
              Help & FAQ
            </button>
            <button
              type="button"
              className={`px-3 py-2 rounded-lg transition-colors cursor-pointer ${
                isPublicActive("CONTACT")
                  ? "bg-[#EBF4FA] text-[#0B5D9B] font-bold"
                  : "text-slate-600 hover:text-[#092F4F] hover:bg-slate-100"
              }`}
              onClick={() => handleNavClick("CONTACT")}
            >
              Contact
            </button>
          </nav>

          {/* Right Header Actions */}
          <div className="flex items-center gap-3">
            {isAuthenticated && user ? (
              <div className="hidden sm:flex items-center gap-2 bg-[#EBF4FA] px-3 py-1.5 rounded-xl border border-[#BAE6FD]">
                <button
                  type="button"
                  onClick={() => onViewChange("DASHBOARD")}
                  className="text-xs font-bold text-[#092F4F] hover:text-[#0B5D9B] cursor-pointer"
                >
                  👤 {user.name}
                </button>
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

            <button
              type="button"
              onClick={() => handleNavClick(isAuthenticated ? "DASHBOARD" : "SCHOLARSHIP")}
              className="inline-flex items-center justify-center px-4 py-2 rounded-xl text-xs font-bold bg-[#0B5D9B] hover:bg-[#074B7D] active:bg-[#053659] text-white shadow-xs transition-all cursor-pointer focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#0B5D9B]"
            >
              {isAuthenticated ? "Citizen Portal →" : "Get Started →"}
            </button>

            {/* Mobile Hamburger Button */}
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

        {/* Mobile Navigation Drawer */}
        {isMobileMenuOpen && (
          <div className="lg:hidden fixed inset-0 top-[115px] z-40 bg-slate-900/60 backdrop-blur-xs flex flex-col justify-start">
            <div className="bg-white border-b border-[#CBD5E1] p-6 shadow-xl space-y-6 max-h-[calc(100vh-120px)] overflow-y-auto">
              <div className="space-y-1">
                <div className="text-xs font-extrabold uppercase text-slate-400 tracking-wider mb-2">
                  Public Navigation
                </div>
                <button
                  type="button"
                  onClick={() => handleNavClick("LANDING")}
                  className={`w-full text-left px-3 py-2.5 rounded-xl font-bold text-sm ${
                    isPublicActive("LANDING") ? "bg-[#EBF4FA] text-[#0B5D9B]" : "text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  🏠 Home
                </button>
                <button
                  type="button"
                  onClick={() => handleNavClick("SERVICES")}
                  className={`w-full text-left px-3 py-2.5 rounded-xl font-bold text-sm ${
                    isPublicActive("SERVICES") ? "bg-[#EBF4FA] text-[#0B5D9B]" : "text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  🏛️ Services Catalog
                </button>
                <button
                  type="button"
                  onClick={() => handleNavClick("HOW_IT_WORKS")}
                  className={`w-full text-left px-3 py-2.5 rounded-xl font-bold text-sm ${
                    isPublicActive("HOW_IT_WORKS") ? "bg-[#EBF4FA] text-[#0B5D9B]" : "text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  ⚙️ How DigiIn Works
                </button>
                <button
                  type="button"
                  onClick={() => handleNavClick("ABOUT")}
                  className={`w-full text-left px-3 py-2.5 rounded-xl font-bold text-sm ${
                    isPublicActive("ABOUT") ? "bg-[#EBF4FA] text-[#0B5D9B]" : "text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  ℹ️ About & Trust
                </button>
                <button
                  type="button"
                  onClick={() => handleNavClick("HELP")}
                  className={`w-full text-left px-3 py-2.5 rounded-xl font-bold text-sm ${
                    isPublicActive("HELP") ? "bg-[#EBF4FA] text-[#0B5D9B]" : "text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  ❓ Help & FAQ
                </button>
                <button
                  type="button"
                  onClick={() => handleNavClick("CONTACT")}
                  className={`w-full text-left px-3 py-2.5 rounded-xl font-bold text-sm ${
                    isPublicActive("CONTACT") ? "bg-[#EBF4FA] text-[#0B5D9B]" : "text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  ✉️ Contact Desk
                </button>
              </div>

              <div className="pt-4 border-t border-slate-200 space-y-3">
                <button
                  type="button"
                  onClick={() => handleNavClick("SIGN_IN")}
                  className="w-full py-2.5 rounded-xl text-sm font-bold text-[#0B5D9B] bg-[#EBF4FA] border border-[#BAE6FD] text-center"
                >
                  Sign In to DigiIn
                </button>
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

      {/* Main Content Area */}
      <main id="main-content" className="flex-1 max-w-7xl w-full mx-auto px-4 md:px-8 py-8" tabIndex={-1}>
        {children}
      </main>

      {/* Public Footer */}
      <GovFooter onNavigate={onViewChange} />
    </div>
  );
};
