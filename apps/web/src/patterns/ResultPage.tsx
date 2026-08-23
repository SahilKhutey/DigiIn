import React from "react";

export interface ResultPageProps {
  statusIcon?: string;
  title: string;
  summary: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
}

export const ResultPage: React.FC<ResultPageProps> = ({
  statusIcon = "✓",
  title,
  summary,
  children,
  actions,
}) => {
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="bg-white border border-[#CBD5E1] rounded-2xl p-6 md:p-8 shadow-sm text-center space-y-6">
        <div className="w-16 h-16 rounded-full bg-[#DFF6E8] text-[#14743F] text-3xl font-extrabold flex items-center justify-center mx-auto shadow-sm" aria-hidden="true">
          {statusIcon}
        </div>

        <div className="space-y-1">
          <h1 className="text-2xl md:text-3xl font-extrabold text-[#092F4F] m-0">
            {title}
          </h1>
          <p className="text-sm text-slate-600 m-0">
            {summary}
          </p>
        </div>

        <div className="text-left">{children}</div>

        {actions && (
          <div className="flex flex-wrap items-center justify-center gap-3 pt-4 border-t border-slate-200">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
};
