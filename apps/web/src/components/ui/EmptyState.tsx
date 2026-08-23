import React from "react";
import { Button } from "./Button";

export interface EmptyStateProps {
  title: string;
  description: string;
  icon?: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon = "📂",
  actionLabel,
  onAction,
  className = "",
}) => {
  return (
    <div className={`p-8 md:p-12 text-center bg-white border border-dashed border-[#CBD5E1] rounded-2xl space-y-4 ${className}`}>
      <div className="text-4xl mx-auto" aria-hidden="true">
        {icon}
      </div>
      <div className="space-y-1">
        <h3 className="text-lg font-bold text-[#092F4F] m-0">{title}</h3>
        <p className="text-xs text-slate-500 max-w-sm mx-auto m-0 leading-relaxed">
          {description}
        </p>
      </div>
      {actionLabel && onAction && (
        <div className="pt-2">
          <Button variant="primary" size="sm" onClick={onAction}>
            {actionLabel}
          </Button>
        </div>
      )}
    </div>
  );
};
