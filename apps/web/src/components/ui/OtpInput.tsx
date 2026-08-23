import React, { useRef, useEffect } from "react";

export interface OtpInputProps {
  length?: number;
  value: string;
  onChange: (otp: string) => void;
  disabled?: boolean;
  error?: string;
  label?: string;
  helperText?: string;
}

export const OtpInput: React.FC<OtpInputProps> = ({
  length = 6,
  value,
  onChange,
  disabled = false,
  error,
  label = "Enter 6-digit verification code",
  helperText = "Sent to your Aadhaar-linked mobile number",
}) => {
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Split value into array of single chars
  const otpArray = Array.from({ length }, (_, i) => value[i] || "");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>, index: number) => {
    const val = e.target.value;
    // Extract last entered digit
    const digit = val.slice(-1);

    if (!/^\d*$/.test(digit)) return;

    const newOtp = [...otpArray];
    newOtp[index] = digit;
    const combined = newOtp.join("");
    onChange(combined);

    // Auto-advance to next input if digit entered
    if (digit && index < length - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, index: number) => {
    if (e.key === "Backspace") {
      if (!otpArray[index] && index > 0) {
        inputRefs.current[index - 1]?.focus();
      }
    } else if (e.key === "ArrowLeft" && index > 0) {
      inputRefs.current[index - 1]?.focus();
    } else if (e.key === "ArrowRight" && index < length - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, length);
    if (pastedData) {
      onChange(pastedData);
      const nextFocus = Math.min(pastedData.length, length - 1);
      inputRefs.current[nextFocus]?.focus();
    }
  };

  return (
    <div className="ux4g-otp-group space-y-2">
      {label && (
        <label className="block text-sm font-bold text-[#092F4F]" id="otp-label">
          {label}
        </label>
      )}
      <div
        className="flex items-center gap-2 md:gap-3"
        role="group"
        aria-labelledby="otp-label"
        onPaste={handlePaste}
      >
        {Array.from({ length }).map((_, idx) => (
          <input
            key={idx}
            ref={(el) => {
              inputRefs.current[idx] = el;
            }}
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            maxLength={1}
            value={otpArray[idx]}
            onChange={(e) => handleChange(e, idx)}
            onKeyDown={(e) => handleKeyDown(e, idx)}
            disabled={disabled}
            aria-label={`Digit ${idx + 1} of ${length}`}
            className={`w-11 h-13 md:w-13 md:h-15 text-center text-xl font-bold rounded-lg border-2 bg-white text-[#092F4F] transition-all
              ${error ? "border-[#991B1B] bg-[#FEE2E2]/20" : "border-[#CBD5E1] hover:border-[#94A3B8]"}
              focus:border-[#0B5D9B] focus:ring-2 focus:ring-[#0B5D9B]/30 focus:outline-none`}
          />
        ))}
      </div>
      {error ? (
        <p className="text-xs font-semibold text-[#991B1B] flex items-center gap-1 mt-1" role="alert">
          <span aria-hidden="true">✕</span> {error}
        </p>
      ) : helperText ? (
        <p className="text-xs text-slate-500 mt-1">{helperText}</p>
      ) : null}
    </div>
  );
};
