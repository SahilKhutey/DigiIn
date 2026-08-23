import React from "react";
import { Breadcrumb, BreadcrumbItem } from "../components/ui/Breadcrumb";

export interface ServicePageProps {
  title: string;
  description?: string;
  breadcrumbs?: BreadcrumbItem[];
  actions?: React.ReactNode;
  children: React.ReactNode;
}

export const ServicePage: React.FC<ServicePageProps> = ({
  title,
  description,
  breadcrumbs,
  actions,
  children,
}) => {
  return (
    <div className="space-y-6">
      {breadcrumbs && <Breadcrumb items={breadcrumbs} />}

      <div className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-200 pb-5">
        <div className="space-y-1">
          <h1 className="text-2xl md:text-3xl font-extrabold text-[#092F4F] m-0">
            {title}
          </h1>
          {description && (
            <p className="text-sm text-slate-600 max-w-3xl m-0 leading-relaxed">
              {description}
            </p>
          )}
        </div>
        {actions && <div className="flex items-center gap-3">{actions}</div>}
      </div>

      <div>{children}</div>
    </div>
  );
};
