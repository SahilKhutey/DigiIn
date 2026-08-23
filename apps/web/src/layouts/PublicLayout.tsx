import React from "react";
import { GovHeader, AppView } from "./GovHeader";
import { GovFooter } from "./GovFooter";

export interface PublicLayoutProps {
  currentView: AppView;
  onViewChange: (view: AppView) => void;
  children: React.ReactNode;
}

export const PublicLayout: React.FC<PublicLayoutProps> = ({
  currentView,
  onViewChange,
  children,
}) => {
  return (
    <div className="min-h-screen flex flex-col bg-[#F3F7FA] text-[#092F4F]">
      <GovHeader currentView={currentView} onViewChange={onViewChange} />
      <main id="main-content" className="flex-1 max-w-7xl w-full mx-auto px-4 md:px-8 py-8" tabIndex={-1}>
        {children}
      </main>
      <GovFooter />
    </div>
  );
};
