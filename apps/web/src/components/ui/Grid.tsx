import React from "react";

export interface GridProps extends React.HTMLAttributes<HTMLDivElement> {
  cols?: 1 | 2 | 3 | 4 | 6 | 12;
  gap?: "xs" | "sm" | "md" | "lg" | "xl";
  children: React.ReactNode;
}

export const Grid: React.FC<GridProps> = ({
  cols = 1,
  gap = "md",
  className = "",
  children,
  ...props
}) => {
  const colClasses = {
    1: "grid-cols-1",
    2: "grid-cols-1 md:grid-cols-2",
    3: "grid-cols-1 md:grid-cols-3",
    4: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-4",
    6: "grid-cols-2 sm:grid-cols-3 lg:grid-cols-6",
    12: "grid-cols-12",
  };

  const gapClasses = {
    xs: "gap-2",
    sm: "gap-3",
    md: "gap-5",
    lg: "gap-8",
    xl: "gap-12",
  };

  return (
    <div
      className={`grid ${colClasses[cols]} ${gapClasses[gap]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
