import React from "react";

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: boolean;
}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(({
  error = false,
  className = "",
  disabled,
  rows = 4,
  ...props
}, ref) => {
  return (
    <textarea
      ref={ref}
      rows={rows}
      disabled={disabled}
      className={`w-full px-3.5 py-2.5 text-sm text-[#092F4F] placeholder-slate-400 bg-white border rounded-lg transition-all ${
        error
          ? "border-[#991B1B] ring-1 ring-[#991B1B]"
          : "border-[#CBD5E1] hover:border-[#94A3B8] focus:border-[#0B5D9B] focus:ring-2 focus:ring-[#0B5D9B]/20"
      } ${disabled ? "bg-slate-100 opacity-60 cursor-not-allowed" : ""} ${className}`}
      {...props}
    />
  );
});

Textarea.displayName = "Textarea";
