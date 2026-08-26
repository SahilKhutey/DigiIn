import React from "react";
import { Link } from "../components/ui/Link";

export interface FormPageProps {
  title: string;
  description?: string;
  backHref?: string;
  backLabel?: string;
  onBack?: () => void;
  children: React.ReactNode;
}

export const FormPage: React.FC<FormPageProps> = ({
  title,
  description,
  backHref = "#/",
  backLabel = "Back",
  onBack,
  children,
}) => {
  return (
    <div className="max-w-xl mx-auto space-y-6">
      {onBack ? (
        <button
          type="button"
          onClick={onBack}
          className="inline-flex items-center gap-1 text-[#0B5D9B] font-bold hover:underline cursor-pointer bg-transparent border-none p-0 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2"
        >
          ← {backLabel}
        </button>
      ) : (
        <Link href={backHref} variant="standalone">
          ← {backLabel}
        </Link>
      )}

      <div className="space-y-1">
        <h1 className="text-2xl md:text-3xl font-extrabold text-[#092F4F] m-0">
          {title}
        </h1>
        {description && (
          <p className="text-sm text-slate-600 m-0">
            {description}
          </p>
        )}
      </div>

      <div className="bg-white border border-[#CBD5E1] rounded-2xl p-6 md:p-8 shadow-sm">
        {children}
      </div>
    </div>
  );
};
