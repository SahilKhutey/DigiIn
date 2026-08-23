import React from "react";

export interface SkeletonProps {
  className?: string;
  variant?: "text" | "circular" | "rectangular";
  width?: string;
  height?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className = "",
  variant = "rectangular",
  width,
  height,
}) => {
  const variantStyles = {
    text: "h-4 rounded",
    circular: "rounded-full",
    rectangular: "rounded-lg",
  }[variant];

  return (
    <div
      aria-hidden="true"
      style={{ width, height }}
      className={`bg-slate-200 animate-pulse ${variantStyles} ${className}`}
    />
  );
};
