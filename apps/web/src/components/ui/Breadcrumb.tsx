import React from "react";

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[];
  className?: string;
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({
  items,
  className = "",
}) => {
  return (
    <nav aria-label="Breadcrumb" className={`text-xs text-slate-500 flex items-center gap-1.5 ${className}`}>
      <ol className="flex items-center gap-1.5 list-none p-0 m-0">
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          return (
            <li key={index} className="flex items-center gap-1.5">
              {item.href && !isLast ? (
                <a href={item.href} className="text-[#0B5D9B] hover:underline font-semibold">
                  {item.label}
                </a>
              ) : (
                <span className="font-bold text-[#092F4F]" aria-current={isLast ? "page" : undefined}>
                  {item.label}
                </span>
              )}
              {!isLast && <span className="text-slate-400" aria-hidden="true">/</span>}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};
