import React from "react";

export interface StackProps extends React.HTMLAttributes<HTMLDivElement> {
  gap?: "none" | "xs" | "sm" | "md" | "lg" | "xl" | "2xl";
  direction?: "vertical" | "horizontal";
  align?: "start" | "center" | "end" | "stretch";
  justify?: "start" | "center" | "end" | "between" | "around";
  wrap?: boolean;
  children: React.ReactNode;
}

export const Stack: React.FC<StackProps> = ({
  gap = "md",
  direction = "vertical",
  align = "stretch",
  justify = "start",
  wrap = false,
  className = "",
  children,
  ...props
}) => {
  const gapClasses = {
    none: "gap-0",
    xs: "gap-1", // 4px
    sm: "gap-2", // 8px
    md: "gap-4", // 16px
    lg: "gap-6", // 24px
    xl: "gap-8", // 32px
    "2xl": "gap-12", // 48px
  };

  const alignClasses = {
    start: "items-start",
    center: "items-center",
    end: "items-end",
    stretch: "items-stretch",
  };

  const justifyClasses = {
    start: "justify-start",
    center: "justify-center",
    end: "justify-end",
    between: "justify-between",
    around: "justify-around",
  };

  return (
    <div
      className={`flex ${direction === "vertical" ? "flex-col" : "flex-row"} ${
        gapClasses[gap]
      } ${alignClasses[align]} ${justifyClasses[justify]} ${
        wrap ? "flex-wrap" : "flex-nowrap"
      } ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
