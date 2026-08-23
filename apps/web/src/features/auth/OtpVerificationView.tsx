import React, { useState, useEffect, useRef } from "react";
import { FormPage } from "../../patterns/FormPage";
import { Button } from "../../components/ui/Button";
import { Alert } from "../../components/ui/Alert";
import { useAuth } from "../../context/AuthContext";

interface OtpVerificationViewProps {
  onSuccess: (isFirstTime?: boolean) => void;
  onBackToMobile: () => void;
}

export const OtpVerificationView: React.FC<OtpVerificationViewProps> = ({
  onSuccess,
  onBackToMobile,
}) => {
  const { pendingMobile, verifyOtp, resendOtp, otpStatus, otpError, clearOtpError } = useAuth();
  const [digits, setDigits] = useState<string[]>(["", "", "", "", "", ""]);
  const [timerSeconds, setTimerSeconds] = useState(30);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // 30s Countdown timer
  useEffect(() => {
    if (timerSeconds <= 0) return;
    const interval = setInterval(() => {
      setTimerSeconds((prev) => prev - 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [timerSeconds]);

  // Focus first input on mount
  useEffect(() => {
    inputRefs.current[0]?.focus();
  }, []);

  const formatTimer = (sec: number) => {
    const mm = String(Math.floor(sec / 60)).padStart(2, "0");
    const ss = String(sec % 60).padStart(2, "0");
    return `${mm}:${ss}`;
  };

  const handleDigitChange = (index: number, value: string) => {
    clearOtpError();
    const cleanVal = value.replace(/\D/g, "");
    if (!cleanVal) {
      const newDigits = [...digits];
      newDigits[index] = "";
      setDigits(newDigits);
      return;
    }

    const char = cleanVal[cleanVal.length - 1];
    const newDigits = [...digits];
    newDigits[index] = char;
    setDigits(newDigits);

    // Auto-advance to next field
    if (index < 5 && char) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !digits[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    if (!pasted) return;

    const newDigits = [...digits];
    for (let i = 0; i < 6; i++) {
      newDigits[i] = pasted[i] || "";
    }
    setDigits(newDigits);

    const nextIndex = Math.min(pasted.length, 5);
    inputRefs.current[nextIndex]?.focus();
  };

  const fullCode = digits.join("");
  const isComplete = fullCode.length === 6;

  const handleVerify = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!isComplete) return;

    const result = await verifyOtp(fullCode);
    if (result.success) {
      onSuccess(result.isFirstTime);
    }
  };

  const handleResend = async () => {
    const ok = await resendOtp();
    if (ok) {
      setTimerSeconds(30);
      setDigits(["", "", "", "", "", ""]);
      inputRefs.current[0]?.focus();
    }
  };

  // Masked mobile display: +91 XXXXX 43210
  const maskedMobile = pendingMobile.length === 10
    ? `+91 XXXXX ${pendingMobile.slice(5)}`
    : `+91 ${pendingMobile}`;

  return (
    <FormPage
      title="Verify your mobile number"
      description={`OTP sent to ${maskedMobile}`}
      backHref="#/sign-in"
      backLabel="Back"
    >
      <form onSubmit={handleVerify} className="space-y-6">
        {/* Error States */}
        {otpStatus === "EXPIRED" ? (
          <div className="p-4 bg-[#FFF0CC] border border-[#FDE68A] rounded-xl text-xs text-[#744B00] space-y-2">
            <strong className="block font-bold">This OTP has expired.</strong>
            <p className="m-0">Request a new OTP to continue authentication.</p>
            <Button
              variant="secondary"
              size="sm"
              type="button"
              onClick={handleResend}
            >
              Send new OTP
            </Button>
          </div>
        ) : otpError ? (
          <Alert type="error" title="We couldn't verify that code">
            {otpError}
          </Alert>
        ) : null}

        {/* 6-Digit Individual Input Boxes */}
        <div className="space-y-2">
          <div className="flex justify-center gap-2 md:gap-3" onPaste={handlePaste}>
            {digits.map((digit, idx) => (
              <input
                key={idx}
                ref={(el) => { inputRefs.current[idx] = el; }}
                type="text"
                inputMode="numeric"
                pattern="[0-9]*"
                maxLength={1}
                value={digit}
                onChange={(e) => handleDigitChange(idx, e.target.value)}
                onKeyDown={(e) => handleKeyDown(idx, e)}
                className="w-11 h-14 md:w-12 md:h-16 text-center text-xl md:text-2xl font-mono font-extrabold text-[#092F4F] bg-white border-2 border-[#CBD5E1] rounded-xl focus:border-[#0B5D9B] focus:ring-3 focus:ring-[#0B5D9B]/20 transition-all outline-none"
                aria-label={`Digit ${idx + 1} of verification code`}
                required
              />
            ))}
          </div>
          <div className="text-center text-[11px] text-slate-400 font-mono">
            Demo test code: 123456
          </div>
        </div>

        {/* Resend Timer Widget */}
        <div className="text-center text-xs text-slate-600 space-y-1">
          <div>Didn't receive the code?</div>
          {timerSeconds > 0 ? (
            <div className="font-bold text-[#0B5D9B]">
              Resend in {formatTimer(timerSeconds)}
            </div>
          ) : (
            <button
              type="button"
              onClick={handleResend}
              className="text-[#0B5D9B] font-bold hover:underline cursor-pointer"
            >
              Resend OTP
            </button>
          )}
        </div>

        <Button
          variant="primary"
          size="lg"
          type="submit"
          fullWidth
          disabled={!isComplete || otpStatus === "VERIFYING"}
        >
          {otpStatus === "VERIFYING" ? "Verifying..." : "Verify →"}
        </Button>
      </form>
    </FormPage>
  );
};
