import React from "react";

export interface SplitProps extends React.HTMLAttributes<HTMLDivElement> {
  left: React.ReactNode;
  right: React.ReactNode;
  ratio?: "1:1" | "2:1" | "1:2";
  align?: "start" | "center" | "end";
}

export const Split: React.FC<SplitProps> = ({
  left,
  right,
  ratio = "1:1",
  align = "center",
  className = "",
  ...props
}) => {
  const ratioClasses = {
    "1:1": "lg:grid-cols-2",
    "2:1": "lg:grid-cols-12 [&>*:first-child]:lg:col-span-8 [&>*:last-child]:lg:col-span-4",
    "1:2": "lg:grid-cols-12 [&>*:first-child]:lg:col-span-4 [&>*:last-child]:lg:col-span-8",
  };

  const alignClasses = {
    start: "items-start",
    center: "items-center",
    end: "items-end",
  };

  return (
    <div
      className={`grid grid-cols-1 ${ratioClasses[ratio]} ${alignClasses[align]} gap-8 lg:gap-12 ${className}`}
      {...props}
    >
      <div>{left}</div>
      <div>{right}</div>
    </div>
  );
};
