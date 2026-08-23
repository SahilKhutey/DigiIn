import React from "react";

export type BadgeVariant =
  | "success"
  | "warning"
  | "danger"
  | "info"
  | "neutral"
  | "primary";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  size?: "sm" | "md" | "lg";
  icon?: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "neutral",
  size = "md",
  icon,
  className = "",
  ...props
}) => {
  const variantStyles: Record<BadgeVariant, { bg: string; text: string; border: string; defaultIcon: string }> = {
    success: {
      bg: "bg-[#DFF6E8]",
      text: "text-[#14743F]",
      border: "border-[#86EFAC]",
      defaultIcon: "✓",
    },
    warning: {
      bg: "bg-[#FFF0CC]",
      text: "text-[#744B00]",
      border: "border-[#FDE68A]",
      defaultIcon: "◷",
    },
    danger: {
      bg: "bg-[#FEE2E2]",
      text: "text-[#991B1B]",
      border: "border-[#FCA5A5]",
      defaultIcon: "✕",
    },
    info: {
      bg: "bg-[#E6F4F8]",
      text: "text-[#0A6990]",
      border: "border-[#BAE6FD]",
      defaultIcon: "ℹ",
    },
    neutral: {
      bg: "bg-[#F1F5F9]",
      text: "text-[#475569]",
      border: "border-[#CBD5E1]",
      defaultIcon: "•",
    },
    primary: {
      bg: "bg-[#EBF4FA]",
      text: "text-[#0B5D9B]",
      border: "border-[#BAE6FD]",
      defaultIcon: "★",
    },
  };

  const style = variantStyles[variant];

  const sizeStyles = {
    sm: "px-2 py-0.5 text-xs gap-1",
    md: "px-2.5 py-1 text-xs font-semibold gap-1.5",
    lg: "px-3.5 py-1.5 text-sm font-semibold gap-2",
  }[size];

  return (
    <span
      className={`inline-flex items-center rounded-full border font-medium select-none ${style.bg} ${style.text} ${style.border} ${sizeStyles} ${className}`}
      role="status"
      {...props}
    >
      <span className="font-bold shrink-0" aria-hidden="true">
        {icon || style.defaultIcon}
      </span>
      <span>{children}</span>
    </span>
  );
};
