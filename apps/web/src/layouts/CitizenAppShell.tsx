import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useLanguage } from "../context/LanguageContext";
import { AppView } from "./GovHeader";

interface CitizenAppShellProps {
  currentView: AppView;
  onViewChange: (view: AppView) => void;
  onOpenScanner?: () => void;
  onOpenEkyc?: () => void;
  children: React.ReactNode;
}

export const CitizenAppShell: React.FC<CitizenAppShellProps> = ({
  currentView,
  onViewChange,
  onOpenScanner,
  onOpenEkyc,
  children,
}) => {
  const { user, logout } = useAuth();
  const { locale, setLocale, t } = useLanguage();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  const primaryNavItems: { id: AppView; label: string; icon: string; badge?: string }[] = [
    { id: "DASHBOARD", label: "Dashboard", icon: "🏠" },
    { id: "IDENTITY", label: "My Identity", icon: "🪪", badge: "DI-7K4M" },
    { id: "WALLET", label: "Documents", icon: "🗂️", badge: "4" },
    { id: "CREDENTIALS", label: "Credentials", icon: "🛡️", badge: "Level 4" },
    { id: "VERIFICATION", label: "Verification", icon: "🔍" },
    { id: "CONSENT", label: "Sharing", icon: "🔐", badge: "Active" },
    { id: "AUDIT_TRAIL", label: "Activity", icon: "📋" },
    { id: "NOTIFICATIONS", label: "Notifications", icon: "🔔", badge: "1" },
  ];

  const secondaryNavItems: { id: AppView; label: string; icon: string }[] = [
    { id: "SUPPORT", label: "Support", icon: "🩺" },
    { id: "SETTINGS", label: "Settings", icon: "⚙️" },
  ];

  const handleNavClick = (view: AppView) => {
    onViewChange(view);
    setIsMobileSidebarOpen(false);
  };

  const getBreadcrumbTitle = (view: AppView): string => {
    switch (view) {
      case "DASHBOARD": return "Dashboard Overview";
      case "IDENTITY": return "My Sovereign Identity Center";
      case "WALLET":
      case "DOCUMENTS": return "Documents & Vault";
      case "CREDENTIALS": return "Verified Credentials Store";
      case "VERIFICATION":
      case "VERIFIER": return "Verification Management";
      case "DOCUMENT_DETAIL": return "Document Details & Version History";
      case "UPLOAD": return "Self-Upload & OCR Pipeline";
      case "SCHOLARSHIP": return "National Merit Scholarship Application";
      case "JOURNEY": return "8-Step Verification Journey";
      case "CONSENT": return "Sharing & Consent Manager";
      case "AUDIT_TRAIL": return "Sovereign Audit Trail";
      case "NOTIFICATIONS": return "System Notifications";
      case "CORRECTIONS": return "Discrepancy Corrections";
      case "SUPPORT": return "Diagnostic Support";
      case "SETTINGS": return "Account Settings";
      case "MOCK_PORTAL": return "Hackathon Sandbox Institutions Portal";
      default: return "Citizen Portal";
    }
  };

  return (
    <div className="min-h-screen flex bg-[#F3F7FA] text-[#092F4F] font-sans antialiased">
      {/* 1. Desktop Left Navigation Sidebar */}
      <aside
        className={`hidden lg:flex flex-col bg-[#092F4F] text-slate-300 border-r border-[#1A3B5C] sticky top-0 h-screen transition-all duration-200 z-40 ${
          isSidebarCollapsed ? "w-20" : "w-64"
        }`}
      >
        {/* Brand Bar */}
        <div className="p-4 border-b border-[#1A3B5C] flex items-center justify-between">
          <div
            className="flex items-center gap-3 cursor-pointer select-none"
            onClick={() => handleNavClick("DASHBOARD")}
          >
            <div className="w-10 h-10 rounded-xl bg-[#0B5D9B] text-white flex items-center justify-center font-extrabold text-xl shadow-xs border border-[#074B7D] shrink-0">
              D
            </div>
            {!isSidebarCollapsed && (
              <div>
                <span className="font-extrabold text-lg text-white tracking-tight">
                  DigiIn
                </span>
                <span className="text-[10px] font-bold ml-2 px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                  Citizen
                </span>
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            className="text-slate-400 hover:text-white p-1 rounded hover:bg-[#102A43] cursor-pointer"
            title={isSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {isSidebarCollapsed ? "→" : "←"}
          </button>
        </div>

        {/* User Identity Pill in Sidebar */}
        {!isSidebarCollapsed && (
          <div className="p-4 mx-3 my-3 bg-[#102A43] rounded-xl border border-slate-700/60">
            <div className="text-xs font-bold text-white flex items-center gap-1.5">
              <span>👤</span>
              <span className="truncate">{user?.name || "Rahul Sharma"}</span>
            </div>
            <div className="text-[11px] font-mono text-cyan-300 mt-1 font-semibold">
              {user?.digiinId || "DI-7K4M-9Q2X-8P6R"}
            </div>
          </div>
        )}

        {/* Navigation Items */}
        <nav className="flex-1 px-3 py-2 space-y-1 overflow-y-auto" aria-label="Citizen Navigation">
          <div className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400 px-3 py-1 mb-1">
            {!isSidebarCollapsed ? "Workspace" : "•••"}
          </div>

          {primaryNavItems.map((item) => {
            const isActive = currentView === item.id || (item.id === "WALLET" && currentView === "DOCUMENTS");
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => handleNavClick(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl font-bold text-xs transition-all cursor-pointer ${
                  isActive
                    ? "bg-[#0B5D9B] text-white shadow-xs"
                    : "text-slate-300 hover:text-white hover:bg-[#102A43]"
                }`}
                title={item.label}
              >
                <span className="text-base shrink-0">{item.icon}</span>
                {!isSidebarCollapsed && (
                  <span className="truncate flex-1 text-left">{item.label}</span>
                )}
                {!isSidebarCollapsed && item.badge && (
                  <span className="text-[10px] font-extrabold px-1.5 py-0.5 rounded-full bg-cyan-900 text-cyan-200 border border-cyan-700">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Bottom Sidebar Tools & Secondary Navigation */}
        <div className="p-3 border-t border-[#1A3B5C] space-y-1">
          {secondaryNavItems.map((item) => {
            const isActive = currentView === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => handleNavClick(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  isActive
                    ? "bg-[#0B5D9B] text-white"
                    : "text-slate-300 hover:text-white hover:bg-[#102A43]"
                }`}
                title={item.label}
              >
                <span>{item.icon}</span>
                {!isSidebarCollapsed && <span>{item.label}</span>}
              </button>
            );
          })}

          {onOpenScanner && (
            <button
              type="button"
              onClick={onOpenScanner}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-bold text-slate-300 hover:text-white hover:bg-[#102A43] cursor-pointer"
            >
              <span>📷</span>
              {!isSidebarCollapsed && <span>Offline Scanner</span>}
            </button>
          )}

          <button
            type="button"
            onClick={() => handleNavClick("LANDING")}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-bold text-slate-400 hover:text-white hover:bg-[#102A43] cursor-pointer"
          >
            <span>🌐</span>
            {!isSidebarCollapsed && <span>Public Website</span>}
          </button>

          <button
            type="button"
            onClick={() => {
              logout();
              onViewChange("SIGN_IN");
            }}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-bold text-red-400 hover:text-red-300 hover:bg-red-950/40 cursor-pointer"
          >
            <span>🚪</span>
            {!isSidebarCollapsed && <span>Sign Out</span>}
          </button>
        </div>
      </aside>

      {/* 2. Main Content Viewport */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Operational Header */}
        <header className="bg-white border-b border-[#CBD5E1] sticky top-0 z-30 px-4 md:px-8 py-3 flex items-center justify-between gap-4 shadow-2xs">
          <div className="flex items-center gap-3">
            {/* Mobile Hamburger Drawer Button */}
            <button
              type="button"
              onClick={() => setIsMobileSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg text-slate-700 hover:bg-slate-100 cursor-pointer"
              aria-label="Open navigation drawer"
            >
              ☰
            </button>

            {/* Breadcrumb Path */}
            <div className="flex items-center gap-2 text-xs">
              <span className="font-semibold text-slate-400">Citizen App</span>
              <span className="text-slate-300">/</span>
              <span className="font-bold text-[#092F4F]">
                {getBreadcrumbTitle(currentView)}
              </span>
            </div>
          </div>

          {/* Right Header Badges & Actions */}
          <div className="flex items-center gap-3">
            {/* Surface Switcher Dropdown */}
            <div className="hidden sm:flex items-center gap-1 bg-[#F1F5F9] px-2.5 py-1 rounded-lg border border-[#CBD5E1] text-xs">
              <span className="text-slate-500 font-medium">Switch Surface:</span>
              <select
                value="CITIZEN"
                onChange={(e) => {
                  const val = e.target.value;
                  if (val === "PUBLIC") onViewChange("LANDING");
                  else if (val === "ZK_STUDIO") onViewChange("ZK_STUDIO");
                  else if (val === "ISSUER") onViewChange("ISSUER_CONSOLE");
                  else if (val === "VERIFIER") onViewChange("VERIFIER_CONSOLE");
                  else if (val === "ADMIN") onViewChange("ADMIN_CONSOLE");
                  else if (val === "MOCK_PORTAL") onViewChange("MOCK_PORTAL");
                }}
                className="bg-transparent text-[#0B5D9B] font-bold border-none cursor-pointer focus:outline-none"
              >
                <option value="CITIZEN">👤 Citizen App</option>
                <option value="MOCK_PORTAL">🧪 Sandbox Institutions</option>
                <option value="PUBLIC">🌐 Public Portal</option>
                <option value="ZK_STUDIO">⚡ ZK Predicate Studio</option>
                <option value="ISSUER">🏛️ Issuer Console</option>
                <option value="VERIFIER">🔍 Verifier Portal</option>
                <option value="ADMIN">⚙️ Admin / Operations</option>
              </select>
            </div>

            {/* Language Toggle */}
            <button
              type="button"
              onClick={() => setLocale(locale === "en" ? "hi" : "en")}
              className="px-2.5 py-1 rounded-lg text-xs font-bold bg-[#F1F5F9] border border-[#CBD5E1] text-[#092F4F] hover:bg-slate-200 cursor-pointer"
            >
              {locale === "en" ? "हिन्दी" : "English"}
            </button>

            {/* User Pill (Click to open Identity Center) */}
            <button
              type="button"
              onClick={() => handleNavClick("IDENTITY")}
              className="flex items-center gap-2 bg-[#EBF4FA] hover:bg-[#D9EEFA] transition-all px-3 py-1 rounded-xl border border-[#BAE6FD] cursor-pointer"
              title="Open DigiIn Identity Center"
            >
              <span className="text-xs font-bold text-[#092F4F]">👤 {user?.name || "Rahul"}</span>
              <span className="text-[10px] font-mono font-bold text-[#0B5D9B] bg-white px-1.5 py-0.2 rounded border border-[#BAE6FD]">
                {user?.digiinId ? user.digiinId.slice(0, 7) + "…" : "DI-7K4M…"}
              </span>
            </button>
          </div>
        </header>

        {/* Main Work Area */}
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 md:px-8 py-6 pb-20 lg:pb-6">
          {children}
        </main>

        {/* Mobile 5-Tab Bottom Navigation Bar (Screen 08 Parity) */}
        <nav
          className="lg:hidden fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-md border-t border-[#CBD5E1] px-2 py-2 flex items-center justify-around z-30 shadow-lg"
          aria-label="Mobile Bottom Navigation"
        >
          <button
            type="button"
            onClick={() => handleNavClick("DASHBOARD")}
            className={`flex flex-col items-center gap-0.5 text-[10px] font-bold transition-all cursor-pointer ${
              currentView === "DASHBOARD" ? "text-[#0B5D9B]" : "text-slate-500 hover:text-slate-800"
            }`}
          >
            <span className="text-lg">🏠</span>
            <span>Home</span>
          </button>
          <button
            type="button"
            onClick={() => handleNavClick("WALLET")}
            className={`flex flex-col items-center gap-0.5 text-[10px] font-bold transition-all cursor-pointer ${
              currentView === "WALLET" || currentView === "DOCUMENTS" ? "text-[#0B5D9B]" : "text-slate-500 hover:text-slate-800"
            }`}
          >
            <span className="text-lg">🗂️</span>
            <span>Wallet</span>
          </button>
          <button
            type="button"
            onClick={() => handleNavClick("SCHOLARSHIP")}
            className={`flex flex-col items-center gap-0.5 text-[10px] font-bold transition-all cursor-pointer ${
              currentView === "SCHOLARSHIP" || currentView === "JOURNEY" ? "text-[#0B5D9B]" : "text-slate-500 hover:text-slate-800"
            }`}
          >
            <span className="text-lg">🛡️</span>
            <span>Verify</span>
          </button>
          <button
            type="button"
            onClick={() => handleNavClick("AUDIT_TRAIL")}
            className={`flex flex-col items-center gap-0.5 text-[10px] font-bold transition-all cursor-pointer ${
              currentView === "AUDIT_TRAIL" ? "text-[#0B5D9B]" : "text-slate-500 hover:text-slate-800"
            }`}
          >
            <span className="text-lg">📋</span>
            <span>Activity</span>
          </button>
          <button
            type="button"
            onClick={() => handleNavClick("SETTINGS")}
            className={`flex flex-col items-center gap-0.5 text-[10px] font-bold transition-all cursor-pointer ${
              currentView === "SETTINGS" ? "text-[#0B5D9B]" : "text-slate-500 hover:text-slate-800"
            }`}
          >
            <span className="text-lg">👤</span>
            <span>Me</span>
          </button>
        </nav>
      </div>

      {/* 3. Mobile Sidebar Drawer */}
      {isMobileSidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex">
          <div className="w-72 bg-[#092F4F] text-white p-5 flex flex-col justify-between shadow-2xl">
            <div className="space-y-6">
              <div className="flex items-center justify-between border-b border-slate-700 pb-4">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-[#0B5D9B] text-white flex items-center justify-center font-bold">
                    D
                  </div>
                  <span className="font-extrabold text-lg">DigiIn Citizen</span>
                </div>
                <button
                  type="button"
                  onClick={() => setIsMobileSidebarOpen(false)}
                  className="text-slate-400 hover:text-white text-xl p-1"
                >
                  ✕
                </button>
              </div>

              <nav className="space-y-1">
                {[...primaryNavItems, ...secondaryNavItems].map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => handleNavClick(item.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl font-bold text-sm text-left ${
                      currentView === item.id ? "bg-[#0B5D9B] text-white" : "text-slate-300 hover:bg-slate-800"
                    }`}
                  >
                    <span>{item.icon}</span>
                    <span>{item.label}</span>
                  </button>
                ))}
              </nav>
            </div>

            <div className="border-t border-slate-700 pt-4 space-y-2">
              <button
                type="button"
                onClick={() => handleNavClick("LANDING")}
                className="w-full py-2 text-xs font-bold text-slate-400 hover:text-white text-left"
              >
                🌐 Go to Public Website
              </button>
              <button
                type="button"
                onClick={() => {
                  logout();
                  setIsMobileSidebarOpen(false);
                  onViewChange("SIGN_IN");
                }}
                className="w-full py-2 text-xs font-bold text-red-400 hover:text-red-300 text-left"
              >
                🚪 Sign Out
              </button>
            </div>
          </div>
          <div className="flex-1" onClick={() => setIsMobileSidebarOpen(false)} />
        </div>
      )}
    </div>
  );
};
