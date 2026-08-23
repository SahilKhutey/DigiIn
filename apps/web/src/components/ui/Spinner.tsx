import React from "react";

export interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  label?: string;
  className?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({
  size = "md",
  label = "Loading content...",
  className = "",
}) => {
  const sizeStyles = {
    sm: "w-4 h-4 border-2",
    md: "w-8 h-8 border-3",
    lg: "w-12 h-12 border-4",
  }[size];

  return (
    <div className={`inline-flex flex-col items-center justify-center gap-2 ${className}`} role="status">
      <div
        className={`${sizeStyles} border-[#0B5D9B] border-t-transparent rounded-full animate-spin`}
        aria-hidden="true"
      />
      <span className="sr-only">{label}</span>
    </div>
  );
};
