import React from "react";

export type AlertType = "info" | "success" | "warning" | "error";

export interface AlertProps {
  type?: AlertType;
  title?: string;
  children: React.ReactNode;
  action?: {
    label: string;
    onClick: () => void;
  };
  onClose?: () => void;
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({
  type = "info",
  title,
  children,
  action,
  onClose,
  className = "",
}) => {
  const typeConfig: Record<
    AlertType,
    { bg: string; border: string; text: string; icon: string; defaultTitle: string }
  > = {
    info: {
      bg: "bg-[#E6F4F8]",
      border: "border-l-4 border-l-[#0B5D9B] border-[#BAE6FD]",
      text: "text-[#0A6990]",
      icon: "ℹ️",
      defaultTitle: "Information",
    },
    success: {
      bg: "bg-[#DFF6E8]",
      border: "border-l-4 border-l-[#14743F] border-[#86EFAC]",
      text: "text-[#14743F]",
      icon: "✓",
      defaultTitle: "Success",
    },
    warning: {
      bg: "bg-[#FFF0CC]",
      border: "border-l-4 border-l-[#744B00] border-[#FDE68A]",
      text: "text-[#744B00]",
      icon: "⚠️",
      defaultTitle: "Attention Required",
    },
    error: {
      bg: "bg-[#FEE2E2]",
      border: "border-l-4 border-l-[#991B1B] border-[#FCA5A5]",
      text: "text-[#991B1B]",
      icon: "✕",
      defaultTitle: "Action Failed",
    },
  };

  const config = typeConfig[type];

  return (
    <div
      role={type === "error" ? "alert" : "status"}
      aria-live={type === "error" ? "assertive" : "polite"}
      className={`rounded-lg border p-4 ${config.bg} ${config.border} ${className}`}
    >
      <div className="flex items-start gap-3">
        <span className="text-lg shrink-0 select-none mt-0.5" aria-hidden="true">
          {config.icon}
        </span>
        <div className="flex-1">
          <h4 className={`font-bold text-sm md:text-base m-0 ${config.text}`}>
            {title || config.defaultTitle}
          </h4>
          <div className="text-sm text-[#334155] mt-1 leading-relaxed">{children}</div>
          {action && (
            <div className="mt-3">
              <button
                type="button"
                onClick={action.onClick}
                className="text-xs font-bold px-3 py-1.5 rounded bg-white border border-current shadow-sm hover:bg-slate-50 transition-colors"
              >
                {action.label}
              </button>
            </div>
          )}
        </div>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            aria-label="Dismiss message"
            className="text-slate-400 hover:text-slate-700 font-bold p-1 rounded leading-none"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
};
