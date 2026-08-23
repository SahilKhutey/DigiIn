import React from "react";

export interface LinkProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  variant?: "default" | "subtle" | "standalone";
  external?: boolean;
}

export const Link: React.FC<LinkProps> = ({
  children,
  variant = "default",
  external = false,
  className = "",
  ...props
}) => {
  const variantStyles = {
    default: "text-[#0B5D9B] hover:text-[#074B7D] underline font-semibold",
    subtle: "text-[#475569] hover:text-[#092F4F] no-underline hover:underline",
    standalone: "inline-flex items-center gap-1 text-[#0B5D9B] font-bold hover:underline",
  }[variant];

  return (
    <a
      className={`${variantStyles} transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ${className}`}
      {...(external ? { target: "_blank", rel: "noopener noreferrer" } : {})}
      {...props}
    >
      {children}
      {external && <span className="text-xs" aria-hidden="true"> ↗</span>}
    </a>
  );
};
