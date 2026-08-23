import React from "react";

export interface PanelProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "subtle" | "brand";
}

export const Panel: React.FC<PanelProps> = ({
  children,
  variant = "default",
  className = "",
  ...props
}) => {
  const variantStyles = {
    default: "bg-white border border-[#CBD5E1]",
    subtle: "bg-[#F8FAFC] border border-[#E2E8F0]",
    brand: "bg-[#EBF4FA] border border-[#BAE6FD]",
  }[variant];

  return (
    <div className={`p-4 md:p-6 rounded-xl ${variantStyles} ${className}`} {...props}>
      {children}
    </div>
  );
};
