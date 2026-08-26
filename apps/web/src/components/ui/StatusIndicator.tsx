import React from "react";

export interface StatusIndicatorProps {
  status: "ACTIVE" | "PENDING" | "VERIFIED" | "REJECTED" | "EXPIRED" | "REVOKED" | "OFFLINE" | "LOADING";
  label?: string;
  size?: "sm" | "md";
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  label,
  size = "md",
}) => {
  const configs: Record<string, { dot: string; text: string; bg: string; defaultLabel: string }> = {
    ACTIVE: { dot: "bg-emerald-500", text: "text-emerald-800", bg: "bg-emerald-50 border-emerald-200", defaultLabel: "Active" },
    VERIFIED: { dot: "bg-blue-600", text: "text-blue-900", bg: "bg-blue-50 border-blue-200", defaultLabel: "Verified" },
    PENDING: { dot: "bg-amber-500 animate-pulse", text: "text-amber-900", bg: "bg-amber-50 border-amber-200", defaultLabel: "Pending Review" },
    REJECTED: { dot: "bg-rose-600", text: "text-rose-900", bg: "bg-rose-50 border-rose-200", defaultLabel: "Rejected" },
    EXPIRED: { dot: "bg-slate-500", text: "text-slate-700", bg: "bg-slate-100 border-slate-300", defaultLabel: "Expired" },
    REVOKED: { dot: "bg-red-700", text: "text-red-900", bg: "bg-red-50 border-red-200", defaultLabel: "Revoked" },
    OFFLINE: { dot: "bg-slate-400", text: "text-slate-600", bg: "bg-slate-50 border-slate-200", defaultLabel: "Offline" },
    LOADING: { dot: "bg-indigo-500 animate-ping", text: "text-indigo-900", bg: "bg-indigo-50 border-indigo-200", defaultLabel: "Loading" },
  };

  const config = configs[status] || configs.ACTIVE;

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 font-medium ${
        config.bg
      } ${config.text} ${size === "sm" ? "text-xs" : "text-sm"}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${config.dot}`} />
      {label || config.defaultLabel}
    </span>
  );
};
