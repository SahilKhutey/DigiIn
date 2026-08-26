import React, { useState } from "react";
import { FormPage } from "../../patterns/FormPage";
import { Button } from "../../components/ui/Button";
import { Alert } from "../../components/ui/Alert";
import { useAuth } from "../../context/AuthContext";
import { DEMO_PERSONAS } from "../../services/auth/mockAuth";

interface SignInViewProps {
  onOtpSent: () => void;
  onQuickLogin?: () => void;
  onNavigateHelp?: () => void;
  onNavigatePrivacy?: () => void;
}

export const SignInView: React.FC<SignInViewProps> = ({
  onOtpSent,
  onQuickLogin,
  onNavigateHelp,
  onNavigatePrivacy,
}) => {
  const { sendOtp, loginAsPersona } = useAuth();
  const [mobile, setMobile] = useState("9876543210");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [personaLoading, setPersonaLoading] = useState<string | null>(null);

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

  const handlePersonaClick = async (personaId: string) => {
    setPersonaLoading(personaId);
    setError("");
    try {
      await loginAsPersona(personaId);
      if (onQuickLogin) {
        onQuickLogin();
      } else {
        onOtpSent();
      }
    } catch {
      setError("Failed to sign in as persona. Please try again.");
    } finally {
      setPersonaLoading(null);
    }
  };

  return (
    <FormPage
      title="Sign in to DigiIn"
      description="Select a Demo Persona for 1-click evaluation or enter your mobile number."
      backHref="#/"
      backLabel="Back to Home"
    >
      <div className="space-y-6">
        {/* Sandbox Notice Banner */}
        <div className="bg-amber-50 border border-amber-300 rounded-xl p-3 text-xs text-amber-900 font-semibold flex items-center gap-2">
          <span>🧪</span>
          <span>
            <strong>HACKATHON SANDBOX:</strong> No external SMS/Aadhaar OTP required. Use 1-Click Demo Personas below for deterministic evaluation.
          </span>
        </div>

        {/* 1-Click Demo Personas */}
        <div className="space-y-3">
          <div className="text-xs font-extrabold uppercase tracking-wider text-[#0B5D9B]">
            ⚡ 1-Click Demo Personas
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {DEMO_PERSONAS.map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => handlePersonaClick(p.id)}
                disabled={!!personaLoading}
                className="flex items-start gap-2.5 p-3 rounded-xl border border-[#CBD5E1] bg-white hover:bg-[#EBF4FA] hover:border-[#0B5D9B] text-left transition-all cursor-pointer shadow-2xs group disabled:opacity-50"
              >
                <span className="text-2xl">{p.avatarBadge}</span>
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-bold text-[#092F4F] group-hover:text-[#0B5D9B] truncate">
                    {p.name}
                  </div>
                  <div className="text-[10px] font-semibold text-slate-500 truncate">
                    {p.role} • {p.digiinId}
                  </div>
                  <div className="text-[10px] text-slate-400 truncate mt-0.5">
                    {p.organization}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-3 my-4">
          <div className="flex-1 border-t border-slate-200" />
          <span className="text-[11px] font-bold text-slate-400 uppercase">Or via Mobile OTP</span>
          <div className="flex-1 border-t border-slate-200" />
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <Alert type="error" title="Invalid mobile number">
              {error}
            </Alert>
          )}

          <div className="space-y-2">
            <label htmlFor="mobile-input" className="block text-xs font-bold text-[#092F4F]">
              Mobile number
            </label>
            <div className="flex items-center rounded-xl border border-[#CBD5E1] bg-white overflow-hidden focus-within:border-[#0B5D9B] focus-within:ring-2 focus-within:ring-[#0B5D9B]/20 transition-all">
              <span className="px-3.5 py-2.5 bg-[#F8FAFC] border-r border-[#CBD5E1] font-bold text-xs text-[#092F4F] select-none">
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
                className="w-full px-3.5 py-2.5 text-sm font-semibold text-[#092F4F] bg-transparent border-0 focus:outline-none"
                required
              />
            </div>
            <p className="text-[11px] text-slate-500 m-0">
              Demo code for all numbers: <code>123456</code>
            </p>
          </div>

          <Button
            variant="primary"
            size="md"
            type="submit"
            fullWidth
            disabled={loading || !!personaLoading}
          >
            {loading ? "Requesting OTP..." : "Continue with Mobile →"}
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
      </div>
    </FormPage>
  );
};

