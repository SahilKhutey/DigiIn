import React, { useState } from "react";
import { FormPage } from "../../patterns/FormPage";
import { Button } from "../../components/ui/Button";
import { Alert } from "../../components/ui/Alert";
import { useAuth } from "../../context/AuthContext";

interface SignInViewProps {
  onOtpSent: () => void;
  onNavigateHelp?: () => void;
  onNavigatePrivacy?: () => void;
}

export const SignInView: React.FC<SignInViewProps> = ({
  onOtpSent,
  onNavigateHelp,
  onNavigatePrivacy,
}) => {
  const { sendOtp } = useAuth();
  const [mobile, setMobile] = useState("9876543210");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanMobile = mobile.replace(/\D/g, "");
    if (cleanMobile.length !== 10) {
      setError("Enter a valid 10-digit mobile number.");
      return;
    }

    setError("");
    setLoading(true);
    const ok = await sendOtp(cleanMobile);
    setLoading(false);

    if (ok) {
      onOtpSent();
    } else {
      setError("Could not request OTP. Please try again.");
    }
  };

  return (
    <FormPage
      title="Sign in to DigiIn"
      description="Enter your registered mobile number to continue."
      backHref="#/"
      backLabel="Back to Home"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <Alert type="error" title="Invalid mobile number">
            {error}
          </Alert>
        )}

        <div className="space-y-2">
          <label htmlFor="mobile-input" className="block text-sm font-bold text-[#092F4F]">
            Mobile number
          </label>
          <div className="flex items-center rounded-xl border border-[#CBD5E1] bg-white overflow-hidden focus-within:border-[#0B5D9B] focus-within:ring-2 focus-within:ring-[#0B5D9B]/20 transition-all">
            <span className="px-3.5 py-3 bg-[#F8FAFC] border-r border-[#CBD5E1] font-bold text-sm text-[#092F4F] select-none">
              +91
            </span>
            <input
              id="mobile-input"
              type="tel"
              maxLength={10}
              placeholder="98765 43210"
              value={mobile}
              onChange={(e) => {
                setError("");
                setMobile(e.target.value);
              }}
              className="w-full px-3.5 py-3 text-base font-semibold text-[#092F4F] bg-transparent border-0 focus:outline-none"
              required
              autoFocus
            />
          </div>
          <p className="text-xs text-slate-500 m-0">
            We'll use this to verify your identity.
          </p>
        </div>

        <Button
          variant="primary"
          size="lg"
          type="submit"
          fullWidth
          disabled={loading}
        >
          {loading ? "Requesting OTP..." : "Continue →"}
        </Button>

        <div className="flex items-center justify-center gap-3 text-xs text-slate-500 pt-2 border-t border-slate-200">
          <button
            type="button"
            onClick={onNavigatePrivacy}
            className="text-slate-500 hover:text-[#0B5D9B] hover:underline cursor-pointer"
          >
            Privacy
          </button>
          <span>•</span>
          <button
            type="button"
            onClick={onNavigateHelp}
            className="text-slate-500 hover:text-[#0B5D9B] hover:underline cursor-pointer"
          >
            Help
          </button>
        </div>
      </form>
    </FormPage>
  );
};
