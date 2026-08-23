import React from "react";

export interface DividerProps extends React.HTMLAttributes<HTMLHRElement> {
  label?: string;
  spacing?: "sm" | "md" | "lg";
}

export const Divider: React.FC<DividerProps> = ({
  label,
  spacing = "md",
  className = "",
  ...props
}) => {
  const marginStyles = {
    sm: "my-2",
    md: "my-4",
    lg: "my-6",
  }[spacing];

  if (label) {
    return (
      <div className={`flex items-center gap-3 ${marginStyles} ${className}`}>
        <div className="flex-1 h-px bg-[#E2E8F0]" />
        <span className="text-xs uppercase font-bold text-slate-400 tracking-wider">
          {label}
        </span>
        <div className="flex-1 h-px bg-[#E2E8F0]" />
      </div>
    );
  }

  return <hr className={`border-0 border-t border-[#E2E8F0] ${marginStyles} ${className}`} {...props} />;
};
