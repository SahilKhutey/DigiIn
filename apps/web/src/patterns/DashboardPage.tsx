import React from "react";

export interface DashboardPageProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
  metrics?: React.ReactNode;
  children: React.ReactNode;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  title,
  subtitle,
  actions,
  metrics,
  children,
}) => {
  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl md:text-3xl font-extrabold text-[#092F4F] m-0">
            {title}
          </h1>
          {subtitle && (
            <p className="text-sm text-slate-600 m-0">
              {subtitle}
            </p>
          )}
        </div>
        {actions && <div className="flex items-center gap-3">{actions}</div>}
      </div>

      {metrics && <div>{metrics}</div>}

      <div className="space-y-8">{children}</div>
    </div>
  );
};
