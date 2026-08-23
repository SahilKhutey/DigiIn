import React from "react";
import { Badge } from "./Badge";

export type VerificationStatusType =
  | "REQUESTED"
  | "PENDING"
  | "RETRIEVING"
  | "VERIFYING"
  | "VERIFIED"
  | "PARTIALLY_VERIFIED"
  | "FAILED"
  | "EXPIRED"
  | "REVOKED";

export interface VerificationStatusProps {
  status: VerificationStatusType;
  showDescription?: boolean;
  className?: string;
}

export const VerificationStatus: React.FC<VerificationStatusProps> = ({
  status,
  showDescription = false,
  className = "",
}) => {
  const statusConfig: Record<
    VerificationStatusType,
    { label: string; variant: "success" | "warning" | "danger" | "info" | "neutral"; desc: string; icon: string }
  > = {
    REQUESTED: {
      label: "Requested",
      variant: "info",
      desc: "Verification inquiry received from accredited organization.",
      icon: "📋",
    },
    PENDING: {
      label: "Pending Consent",
      variant: "warning",
      desc: "Awaiting citizen review and authorization.",
      icon: "◷",
    },
    RETRIEVING: {
      label: "Retrieving Records",
      variant: "info",
      desc: "Fetching certified claims from government issuers.",
      icon: "⬇",
    },
    VERIFYING: {
      label: "Verification in Progress",
      variant: "info",
      desc: "Matching claims against official source registries.",
      icon: "◷",
    },
    VERIFIED: {
      label: "Verified at Source",
      variant: "success",
      desc: "Document details matched with 100% mathematical integrity.",
      icon: "✓",
    },
    PARTIALLY_VERIFIED: {
      label: "Partially Verified",
      variant: "warning",
      desc: "Some requested documents were verified; others require attention.",
      icon: "⚠",
    },
    FAILED: {
      label: "Verification Failed",
      variant: "danger",
      desc: "Document details did not match official records.",
      icon: "✕",
    },
    EXPIRED: {
      label: "Session Expired",
      variant: "neutral",
      desc: "Verification token exceeded its validity duration.",
      icon: "⌛",
    },
    REVOKED: {
      label: "Consent Revoked",
      variant: "danger",
      desc: "Citizen revoked sharing permission.",
      icon: "⊘",
    },
  };

  const config = statusConfig[status] || statusConfig.REQUESTED;

  return (
    <div className={`space-y-1 ${className}`}>
      <Badge variant={config.variant} icon={config.icon} size="md">
        {config.label}
      </Badge>
      {showDescription && (
        <p className="text-xs text-slate-500 mt-0.5 mb-0">
          {config.desc}
        </p>
      )}
    </div>
  );
};
