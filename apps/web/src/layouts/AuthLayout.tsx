import React from "react";
import { GovHeader, AppView } from "./GovHeader";
import { GovFooter } from "./GovFooter";

export interface AuthLayoutProps {
  currentView: AppView;
  onViewChange: (view: AppView) => void;
  children: React.ReactNode;
}

export const AuthLayout: React.FC<AuthLayoutProps> = ({
  currentView,
  onViewChange,
  children,
}) => {
  return (
    <div className="min-h-screen flex flex-col bg-[#F3F7FA] text-[#092F4F]">
      <GovHeader currentView={currentView} onViewChange={onViewChange} />
      <main id="main-content" className="flex-1 max-w-lg w-full mx-auto px-4 py-12 flex flex-col justify-center" tabIndex={-1}>
        {children}
      </main>
      <GovFooter />
    </div>
  );
};
