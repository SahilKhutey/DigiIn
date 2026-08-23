import React from "react";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "elevated" | "bordered" | "highlight";
  padded?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = "default",
  padded = true,
  className = "",
  ...props
}) => {
  const variantClasses = {
    default: "bg-white border border-[#E2E8F0] shadow-sm",
    elevated: "bg-white border border-[#CBD5E1] shadow-md hover:shadow-lg transition-shadow",
    bordered: "bg-white border-2 border-[#0B5D9B]",
    highlight: "bg-[#F3F7FA] border border-[#BAE6FD]",
  }[variant];

  const paddingClass = padded ? "p-5 md:p-6" : "";

  return (
    <div
      className={`rounded-xl overflow-hidden ${variantClasses} ${paddingClass} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  children,
  className = "",
  ...props
}) => (
  <div className={`flex flex-wrap items-start justify-between gap-3 mb-4 pb-3 border-b border-[#E2E8F0] ${className}`} {...props}>
    {children}
  </div>
);

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({
  children,
  className = "",
  ...props
}) => (
  <h3 className={`text-lg md:text-xl font-bold text-[#092F4F] m-0 ${className}`} {...props}>
    {children}
  </h3>
);

export const CardDescription: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({
  children,
  className = "",
  ...props
}) => (
  <p className={`text-sm text-[#475569] mt-1 mb-0 ${className}`} {...props}>
    {children}
  </p>
);

export const CardFooter: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  children,
  className = "",
  ...props
}) => (
  <div className={`flex flex-wrap items-center justify-end gap-3 mt-4 pt-3 border-t border-[#E2E8F0] ${className}`} {...props}>
    {children}
  </div>
);
