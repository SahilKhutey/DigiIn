import React from "react";

export interface RadioOption {
  value: string;
  label: string;
  description?: string;
  disabled?: boolean;
}

export interface RadioGroupProps {
  name: string;
  options: RadioOption[];
  selectedValue: string;
  onChange: (value: string) => void;
  className?: string;
  error?: string;
}

export const RadioGroup: React.FC<RadioGroupProps> = ({
  name,
  options,
  selectedValue,
  onChange,
  className = "",
  error,
}) => {
  return (
    <div className={`space-y-3 ${className}`} role="radiogroup">
      {options.map((opt) => {
        const optionId = `${name}-${opt.value}`;
        const isSelected = selectedValue === opt.value;

        return (
          <label
            key={opt.value}
            htmlFor={optionId}
            className={`flex items-start gap-3 p-3.5 rounded-xl border transition-all cursor-pointer select-none ${
              isSelected
                ? "bg-[#EBF4FA] border-[#0B5D9B] ring-1 ring-[#0B5D9B]"
                : "bg-white border-[#CBD5E1] hover:border-[#94A3B8]"
            } ${opt.disabled ? "opacity-60 cursor-not-allowed" : ""}`}
          >
            <input
              type="radio"
              id={optionId}
              name={name}
              value={opt.value}
              checked={isSelected}
              disabled={opt.disabled}
              onChange={() => onChange(opt.value)}
              className="w-4 h-4 mt-0.5 accent-[#0B5D9B] cursor-pointer"
            />
            <div className="flex-1">
              <span className={`text-sm font-bold block ${isSelected ? "text-[#0B5D9B]" : "text-[#092F4F]"}`}>
                {opt.label}
              </span>
              {opt.description && (
                <p className="text-xs text-slate-500 mt-0.5 mb-0 leading-relaxed">
                  {opt.description}
                </p>
              )}
            </div>
          </label>
        );
      })}
      {error && <p className="text-xs text-[#991B1B] font-semibold">{error}</p>}
    </div>
  );
};
