import React from "react";

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  options: SelectOption[];
  error?: boolean;
  placeholder?: string;
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(({
  options,
  error = false,
  placeholder,
  className = "",
  disabled,
  ...props
}, ref) => {
  return (
    <select
      ref={ref}
      disabled={disabled}
      className={`w-full min-h-[44px] px-3.5 py-2 text-sm text-[#092F4F] bg-white border rounded-lg transition-all appearance-none cursor-pointer ${
        error
          ? "border-[#991B1B] ring-1 ring-[#991B1B]"
          : "border-[#CBD5E1] hover:border-[#94A3B8] focus:border-[#0B5D9B] focus:ring-2 focus:ring-[#0B5D9B]/20"
      } ${disabled ? "bg-slate-100 opacity-60 cursor-not-allowed" : ""} ${className}`}
      {...props}
    >
      {placeholder && <option value="" disabled>{placeholder}</option>}
      {options.map((opt) => (
        <option key={opt.value} value={opt.value} disabled={opt.disabled}>
          {opt.label}
        </option>
      ))}
    </select>
  );
});

Select.displayName = "Select";
