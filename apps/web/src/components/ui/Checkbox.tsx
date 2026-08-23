import React from "react";

export interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: React.ReactNode;
  description?: string;
  error?: string;
}

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(({
  label,
  description,
  error,
  id,
  className = "",
  disabled,
  ...props
}, ref) => {
  const inputId = id || `cb-${Math.random().toString(36).substring(2, 9)}`;

  return (
    <div className={`space-y-1 ${className}`}>
      <label htmlFor={inputId} className={`flex items-start gap-3 cursor-pointer select-none ${disabled ? "opacity-60 cursor-not-allowed" : ""}`}>
        <input
          ref={ref}
          type="checkbox"
          id={inputId}
          disabled={disabled}
          className="w-5 h-5 mt-0.5 rounded border-[#CBD5E1] text-[#0B5D9B] accent-[#0B5D9B] focus:ring-2 focus:ring-[#0B5D9B]/30 cursor-pointer disabled:cursor-not-allowed"
          {...props}
        />
        <div className="flex-1">
          <span className="text-sm font-semibold text-[#092F4F] block">{label}</span>
          {description && <p className="text-xs text-slate-500 mt-0.5 mb-0">{description}</p>}
        </div>
      </label>
      {error && <p className="text-xs text-[#991B1B] font-semibold pl-8 m-0">{error}</p>}
    </div>
  );
});

Checkbox.displayName = "Checkbox";
