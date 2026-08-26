import React from "react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
  fullWidth?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: "left" | "right";
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "primary",
  size = "md",
  fullWidth = false,
  loading = false,
  icon,
  iconPosition = "left",
  className = "",
  disabled,
  ...props
}) => {
  const baseClasses = "ux4g-btn inline-flex items-center justify-center font-bold transition-all select-none cursor-pointer border active:scale-[0.98] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#0B5D9B] focus-visible:outline-offset-2";
  
  const variantClasses = {
    primary: "bg-[#0B5D9B] hover:bg-[#074B7D] active:bg-[#053659] text-white border-transparent shadow-xs",
    secondary: "bg-[#F3F7FA] hover:bg-[#E2E8F0] active:bg-[#CBD5E1] text-[#092F4F] border-[#CBD5E1]",
    outline: "bg-transparent hover:bg-[#EBF4FA] text-[#0B5D9B] border-[#0B5D9B]",
    danger: "bg-[#991B1B] hover:bg-[#7F1D1D] active:bg-[#571414] text-white border-transparent shadow-xs",
    ghost: "bg-transparent hover:bg-[#F3F7FA] text-[#475569] border-transparent",
  }[variant];

  const sizeClasses = {
    sm: "min-h-[36px] px-3 py-1.5 text-xs rounded-md gap-1.5",
    md: "min-h-[44px] px-4 py-2 text-sm rounded-lg gap-2",
    lg: "min-h-[52px] px-6 py-3 text-base rounded-lg gap-2.5",
  }[size];

  const widthClass = fullWidth ? "w-full" : "";
  const stateClass = disabled || loading ? "opacity-60 cursor-not-allowed pointer-events-none" : "";

  return (
    <button
      className={`${baseClasses} ${variantClasses} ${sizeClasses} ${widthClass} ${stateClass} ${className}`}
      disabled={disabled || loading}
      aria-busy={loading}
      {...props}
    >
      {loading ? (
        <>
          <span
            className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"
            aria-hidden="true"
          />
          <span>{children}</span>
        </>
      ) : (
        <>
          {icon && iconPosition === "left" && <span className="inline-flex shrink-0">{icon}</span>}
          <span>{children}</span>
          {icon && iconPosition === "right" && <span className="inline-flex shrink-0">{icon}</span>}
        </>
      )}
    </button>
  );
};
