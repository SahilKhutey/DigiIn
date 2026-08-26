import React from "react";

export interface TrustBadgeProps {
  level: number;
  label?: string;
  size?: "sm" | "md" | "lg";
}

export const TrustBadge: React.FC<TrustBadgeProps> = ({
  level,
  label,
  size = "md",
}) => {
  const levelDetails: Record<number, { title: string; bg: string; text: string; icon: string; border: string }> = {
    0: { title: "Level 0: Uploaded", bg: "bg-slate-100", text: "text-slate-700", icon: "📁", border: "border-slate-300" },
    1: { title: "Level 1: OCR Extracted", bg: "bg-blue-50", text: "text-blue-700", icon: "⚡", border: "border-blue-200" },
    2: { title: "Level 2: Identity Matched", bg: "bg-indigo-50", text: "text-indigo-700", icon: "👤", border: "border-indigo-200" },
    3: { title: "Level 3: Issuer Matched", bg: "bg-purple-50", text: "text-purple-700", icon: "🏛️", border: "border-purple-200" },
    4: { title: "Level 4: Government Verified", bg: "bg-emerald-50", text: "text-emerald-800", icon: "✓", border: "border-emerald-200" },
    5: { title: "Level 5: Cryptographically Signed", bg: "bg-amber-50", text: "text-amber-900", icon: "🛡️", border: "border-amber-300" },
  };

  const current = levelDetails[level] || levelDetails[0];

  const sizeClasses = {
    sm: "px-2 py-0.5 text-xs font-semibold gap-1",
    md: "px-2.5 py-1 text-xs font-bold gap-1.5",
    lg: "px-3.5 py-1.5 text-sm font-bold gap-2",
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border shadow-2xs transition-all ${
        current.bg
      } ${current.text} ${current.border} ${sizeClasses[size]}`}
      title={`Discrete Trust Signal ${current.title}`}
    >
      <span aria-hidden="true">{current.icon}</span>
      <span>{label || current.title}</span>
    </span>
  );
};
