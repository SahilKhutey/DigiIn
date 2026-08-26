import React from "react";

export interface SwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  description?: string;
  disabled?: boolean;
  id?: string;
}

export const Switch: React.FC<SwitchProps> = ({
  checked,
  onChange,
  label,
  description,
  disabled = false,
  id,
}) => {
  const switchId = id || `switch-${Math.random().toString(36).substring(2, 9)}`;

  return (
    <div className="flex items-start gap-3">
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        id={switchId}
        disabled={disabled}
        onClick={() => !disabled && onChange(!checked)}
        className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-[#0B5D9B] focus:ring-offset-2 ${
          checked ? "bg-[#0B5D9B]" : "bg-slate-300"
        } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
      >
        <span
          className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out ${
            checked ? "translate-x-5" : "translate-x-0"
          }`}
        />
      </button>
      {(label || description) && (
        <div className="flex flex-col">
          {label && (
            <label htmlFor={switchId} className="text-sm font-semibold text-slate-800 cursor-pointer">
              {label}
            </label>
          )}
          {description && <span className="text-xs text-slate-500">{description}</span>}
        </div>
      )}
    </div>
  );
};
