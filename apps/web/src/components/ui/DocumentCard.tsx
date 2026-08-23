import React from "react";
import { Badge } from "./Badge";
import { Button } from "./Button";

export interface DocumentCardProps {
  title: string;
  issuer: string;
  issueDate: string;
  status?: "VERIFIED" | "PENDING" | "REJECTED" | "NOT_FOUND";
  trustLevel?: number;
  onViewDetails?: () => void;
  className?: string;
}

export const DocumentCard: React.FC<DocumentCardProps> = ({
  title,
  issuer,
  issueDate,
  status = "VERIFIED",
  trustLevel = 4,
  onViewDetails,
  className = "",
}) => {
  const getBadgeVariant = () => {
    switch (status) {
      case "VERIFIED":
        return "success";
      case "PENDING":
        return "warning";
      case "REJECTED":
      case "NOT_FOUND":
        return "danger";
      default:
        return "neutral";
    }
  };

  return (
    <div className={`flex flex-wrap items-center justify-between p-4 bg-white border border-[#CBD5E1] rounded-xl hover:border-[#94A3B8] transition-all gap-4 ${className}`}>
      <div className="space-y-1">
        <div className="flex items-center gap-2 flex-wrap">
          <strong className="text-base text-[#092F4F] font-bold">{title}</strong>
          <Badge variant="primary" size="sm">Level {trustLevel} • Gov Verified</Badge>
        </div>
        <div className="text-xs text-slate-500 flex items-center gap-2">
          <span>Issued by: <strong className="text-slate-700">{issuer}</strong></span>
          <span>•</span>
          <span>Date: <strong className="text-slate-700">{issueDate}</strong></span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Badge variant={getBadgeVariant()} size="md">
          {status.replace(/_/g, " ")}
        </Badge>
        {onViewDetails && (
          <Button variant="outline" size="sm" onClick={onViewDetails}>
            View Details
          </Button>
        )}
      </div>
    </div>
  );
};
