import React from "react";

export interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon: React.ReactNode;
  label: string;
  variant?: "primary" | "secondary" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
}

export const IconButton: React.FC<IconButtonProps> = ({
  icon,
  label,
  variant = "ghost",
  size = "md",
  className = "",
  ...props
}) => {
  const variantStyles = {
    primary: "bg-[#0B5D9B] text-white hover:bg-[#074B7D]",
    secondary: "bg-[#F1F5F9] text-[#092F4F] hover:bg-[#E2E8F0]",
    outline: "border border-[#CBD5E1] text-[#092F4F] hover:bg-[#F8FAFC]",
    ghost: "text-[#475569] hover:text-[#092F4F] hover:bg-[#F1F5F9]",
  }[variant];

  const sizeStyles = {
    sm: "w-8 h-8 text-xs",
    md: "w-10 h-10 text-sm",
    lg: "w-12 h-12 text-base",
  }[size];

  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      className={`inline-flex items-center justify-center rounded-lg transition-all cursor-pointer focus-visible:outline focus-visible:outline-3 focus-visible:outline-offset-2 ${variantStyles} ${sizeStyles} ${className}`}
      {...props}
    >
      {icon}
    </button>
  );
};
