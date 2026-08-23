import React from "react";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
  prefixElement?: React.ReactNode;
  suffixElement?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(({
  error = false,
  prefixElement,
  suffixElement,
  className = "",
  disabled,
  ...props
}, ref) => {
  return (
    <div className={`relative flex items-center rounded-lg border bg-white transition-all ${
      error
        ? "border-[#991B1B] ring-1 ring-[#991B1B]"
        : "border-[#CBD5E1] hover:border-[#94A3B8] focus-within:border-[#0B5D9B] focus-within:ring-2 focus-within:ring-[#0B5D9B]/20"
    } ${disabled ? "bg-slate-100 opacity-60 cursor-not-allowed" : ""} ${className}`}>
      {prefixElement && <div className="pl-3 text-slate-500 text-sm">{prefixElement}</div>}
      <input
        ref={ref}
        disabled={disabled}
        className="w-full min-h-[44px] px-3.5 py-2 text-sm text-[#092F4F] placeholder-slate-400 bg-transparent border-0 rounded-lg focus:outline-none disabled:cursor-not-allowed"
        {...props}
      />
      {suffixElement && <div className="pr-3 text-slate-500 text-sm">{suffixElement}</div>}
    </div>
  );
});

Input.displayName = "Input";
