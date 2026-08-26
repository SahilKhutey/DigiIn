import React from "react";
import { Container } from "./Container";

export interface PageProps {
  size?: "sm" | "md" | "lg" | "full";
  className?: string;
  children: React.ReactNode;
}

export interface PageHeaderProps {
  title: string;
  description?: string;
  eyebrow?: string;
  backHref?: string;
  onBack?: () => void;
  actions?: React.ReactNode;
  className?: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  description,
  eyebrow,
  backHref,
  onBack,
  actions,
  className = "",
}) => {
  return (
    <div className={`space-y-3 pb-6 border-b border-slate-200 ${className}`}>
      {(backHref || onBack) && (
        <div>
          <button
            type="button"
            onClick={onBack}
            className="inline-flex items-center gap-1.5 text-xs font-bold text-[#0B5D9B] hover:underline cursor-pointer"
          >
            ← Back
          </button>
        </div>
      )}

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          {eyebrow && (
            <span className="text-xs uppercase font-extrabold tracking-wider text-[#0B5D9B] block">
              {eyebrow}
            </span>
          )}
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#092F4F] m-0">
            {title}
          </h1>
          {description && (
            <p className="text-xs sm:text-sm text-slate-500 m-0">
              {description}
            </p>
          )}
        </div>

        {actions && <div className="flex items-center gap-3 shrink-0">{actions}</div>}
      </div>
    </div>
  );
};

export const Page: React.FC<PageProps> = ({
  size = "lg",
  className = "",
  children,
}) => {
  return (
    <div className="min-h-screen py-6">
      <Container size={size} className={`space-y-8 ${className}`}>
        {children}
      </Container>
    </div>
  );
};
