import React from "react";
import { GovHeader, AppView } from "./GovHeader";
import { GovFooter } from "./GovFooter";

interface AppShellProps {
  currentView: AppView;
  onViewChange: (view: AppView) => void;
  onOpenScanner?: () => void;
  onOpenEkyc?: () => void;
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({
  currentView,
  onViewChange,
  onOpenScanner,
  onOpenEkyc,
  children,
}) => {
  return (
    <div className="min-h-screen flex flex-col bg-[#F3F7FA] text-[#092F4F] font-sans antialiased">
      {/* Skip to Main Content Link for Keyboard Accessibility (WCAG 2.1 AA) */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-[#0B5D9B] focus:text-white focus:font-bold focus:rounded-md focus:shadow-lg"
      >
        Skip to main content
      </a>

      {/* Official Government Header */}
      <GovHeader
        currentView={currentView}
        onViewChange={onViewChange}
        onOpenScanner={onOpenScanner}
        onOpenEkyc={onOpenEkyc}
      />

      {/* Main Content Area */}
      <main id="main-content" className="flex-1 max-w-7xl w-full mx-auto px-4 md:px-8 py-8" tabIndex={-1}>
        {children}
      </main>

      {/* Official Government Footer */}
      <GovFooter onNavigate={onViewChange} />
    </div>
  );
};
