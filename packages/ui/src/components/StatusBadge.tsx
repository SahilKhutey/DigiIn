import React from "react";
import type { VerificationStatus, AuthenticityStatus } from "../../types/src/index";

export interface StatusBadgeProps {
  status: VerificationStatus | AuthenticityStatus | string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = "md",
  className = "",
}) => {
  const getStatusStyles = () => {
    switch (status) {
      case "VERIFIED":
        return "bg-emerald-50 text-emerald-700 border-emerald-200";
      case "PENDING":
      case "REQUIRES_REVIEW":
        return "bg-amber-50 text-amber-700 border-amber-200";
      case "REJECTED":
      case "IDENTITY_MISMATCH":
      case "REVOKED":
        return "bg-rose-50 text-rose-700 border-rose-200";
      case "EXPIRED":
      case "NOT_FOUND":
      case "ISSUER_UNAVAILABLE":
        return "bg-slate-100 text-slate-700 border-slate-300";
      default:
        return "bg-blue-50 text-blue-700 border-blue-200";
    }
  };

  const sizeStyles = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-2.5 py-1 text-xs font-semibold",
    lg: "px-3 py-1.5 text-sm font-semibold",
  }[size];

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border ${getStatusStyles()} ${sizeStyles} ${className}`}
      role="status"
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" aria-hidden="true" />
      {status.replace(/_/g, " ")}
    </span>
  );
};
