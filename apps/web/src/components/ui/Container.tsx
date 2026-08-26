import React from "react";

export interface ContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: "sm" | "md" | "lg" | "full";
  children: React.ReactNode;
}

export const Container: React.FC<ContainerProps> = ({
  size = "lg",
  className = "",
  children,
  ...props
}) => {
  const sizeClasses = {
    sm: "max-w-[640px]",
    md: "max-w-[900px]",
    lg: "max-w-[1200px]",
    full: "max-w-full",
  };

  return (
    <div
      className={`w-full mx-auto px-4 sm:px-6 lg:px-8 ${sizeClasses[size]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
