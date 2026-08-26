import React from "react";

export interface SectionProps extends React.HTMLAttributes<HTMLElement> {
  label?: string;
  title?: string;
  description?: string;
  align?: "left" | "center";
  children: React.ReactNode;
}

export const Section: React.FC<SectionProps> = ({
  label,
  title,
  description,
  align = "left",
  className = "",
  children,
  ...props
}) => {
  return (
    <section className={`space-y-8 py-4 ${className}`} {...props}>
      {(label || title || description) && (
        <div
          className={`space-y-1.5 ${
            align === "center" ? "text-center max-w-xl mx-auto" : "max-w-3xl"
          }`}
        >
          {label && (
            <span className="text-xs uppercase font-extrabold tracking-wider text-[#0B5D9B] block">
              {label}
            </span>
          )}
          {title && (
            <h2 className="text-2xl sm:text-3xl font-extrabold text-[#092F4F] m-0">
              {title}
            </h2>
          )}
          {description && (
            <p className="text-xs sm:text-sm text-slate-600 m-0">
              {description}
            </p>
          )}
        </div>
      )}
      {children}
    </section>
  );
};
