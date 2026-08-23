import React from "react";

export interface FormFieldProps {
  label: string;
  htmlFor: string;
  required?: boolean;
  hint?: string;
  error?: string;
  help?: string;
  children: React.ReactNode;
  className?: string;
}

export const FormField: React.FC<FormFieldProps> = ({
  label,
  htmlFor,
  required = false,
  hint,
  error,
  help,
  children,
  className = "",
}) => {
  const hintId = hint ? `${htmlFor}-hint` : undefined;
  const errorId = error ? `${htmlFor}-error` : undefined;
  const helpId = help ? `${htmlFor}-help` : undefined;

  const describedBy = [hintId, errorId, helpId].filter(Boolean).join(" ") || undefined;

  return (
    <div className={`space-y-1.5 ${className}`}>
      <div className="flex items-center justify-between">
        <label htmlFor={htmlFor} className="block text-sm font-bold text-[#092F4F]">
          {label} {required && <span className="text-[#991B1B]" aria-hidden="true">*</span>}
        </label>
        {required && <span className="text-[11px] text-slate-500 font-semibold">Required</span>}
      </div>

      {hint && (
        <p id={hintId} className="text-xs text-slate-500 m-0">
          {hint}
        </p>
      )}

      {/* Render children and pass down aria-describedby if needed */}
      <div>
        {children}
      </div>

      {error && (
        <p id={errorId} className="text-xs font-bold text-[#991B1B] flex items-center gap-1 mt-1 m-0" role="alert">
          <span aria-hidden="true">✕</span> {error}
        </p>
      )}

      {help && !error && (
        <p id={helpId} className="text-xs text-slate-500 mt-1 m-0">
          {help}
        </p>
      )}
    </div>
  );
};
