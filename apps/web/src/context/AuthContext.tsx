import React, { createContext, useContext, useState, useEffect } from "react";
import { authService } from "../services/auth/authService";
import { AuthState, OtpStatus, CitizenProfile } from "../services/auth/authTypes";

interface AuthContextType {
  authState: AuthState;
  isAuthenticated: boolean;
  otpStatus: OtpStatus;
  user: CitizenProfile | null;
  pendingMobile: string;
  isFirstTime: boolean;
  otpError: string | null;

  setPendingMobile: (mobile: string) => void;
  sendOtp: (mobile: string) => Promise<boolean>;
  verifyOtp: (code: string) => Promise<{ success: boolean; isFirstTime?: boolean; error?: string }>;
  resendOtp: () => Promise<boolean>;
  loginAsPersona: (personaId: string) => Promise<void>;
  completeOnboarding: (name: string, language: "en" | "hi") => Promise<void>;
  logout: () => void;
  clearOtpError: () => void;
}


const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [authState, setAuthState] = useState<AuthState>("AUTH_UNKNOWN");
  const [otpStatus, setOtpStatus] = useState<OtpStatus>("IDLE");
  const [user, setUser] = useState<CitizenProfile | null>(null);
  const [pendingMobile, setPendingMobile] = useState<string>("9876543210");
  const [isFirstTime, setIsFirstTime] = useState<boolean>(false);
  const [otpError, setOtpError] = useState<string | null>(null);

  useEffect(() => {
    // Check initial active session
    const existing = authService.getSession();
    if (existing) {
      setUser(existing);
      setAuthState("AUTHENTICATED");
    } else {
      setAuthState("SIGNED_OUT");
    }
  }, []);

  const sendOtp = async (mobile: string): Promise<boolean> => {
    setPendingMobile(mobile);
    setOtpStatus("REQUESTING");
    setOtpError(null);

    const result = await authService.requestOtp(mobile);
    if (result.success) {
      setOtpStatus("SENT");
      return true;
    }

    setOtpStatus("IDLE");
    setOtpError(result.message || "Failed to dispatch OTP. Please try again.");
    return false;
  };

  const verifyOtp = async (
    code: string
  ): Promise<{ success: boolean; isFirstTime?: boolean; error?: string }> => {
    setOtpStatus("VERIFYING");
    setOtpError(null);

    const result = await authService.verifyOtp(pendingMobile, code);
    if (result.success && result.profile) {
      setUser(result.profile);
      setIsFirstTime(!!result.isFirstTime);

      if (result.isFirstTime) {
        setAuthState("ONBOARDING");
      } else {
        setAuthState("AUTHENTICATED");
      }

      setOtpStatus("IDLE");
      return { success: true, isFirstTime: result.isFirstTime };
    }

    if (result.error === "EXPIRED") {
      setOtpStatus("EXPIRED");
    } else {
      setOtpStatus("INVALID");
    }

    const msg = result.message || "We couldn't verify that code. Check the OTP and try again.";
    setOtpError(msg);
    return { success: false, error: msg };
  };

  const resendOtp = async (): Promise<boolean> => {
    setOtpStatus("REQUESTING");
    setOtpError(null);
    const result = await authService.resendOtp(pendingMobile);
    if (result.success) {
      setOtpStatus("SENT");
      return true;
    }
    setOtpError("Could not resend OTP. Please try again.");
    return false;
  };

  const loginAsPersona = async (personaId: string) => {
    const profile = await authService.loginAsPersona(personaId);
    setUser(profile);
    setPendingMobile(profile.mobile);
    setIsFirstTime(false);
    setAuthState("AUTHENTICATED");
    setOtpStatus("IDLE");
    setOtpError(null);
  };

  const completeOnboarding = async (name: string, language: "en" | "hi") => {
    const profile = await authService.completeOnboarding(pendingMobile, { name, language });
    setUser(profile);
    setIsFirstTime(false);
    setAuthState("AUTHENTICATED");
  };

  const logout = () => {
    authService.clearSession();
    setUser(null);
    setAuthState("SIGNED_OUT");
    setOtpStatus("IDLE");
    setOtpError(null);
  };

  const clearOtpError = () => {
    setOtpError(null);
  };

  return (
    <AuthContext.Provider
      value={{
        authState,
        isAuthenticated: !!user && authState === "AUTHENTICATED",
        otpStatus,
        user,

        pendingMobile,
        isFirstTime,
        otpError,
        setPendingMobile,
        sendOtp,
        verifyOtp,
        resendOtp,
        loginAsPersona,
        completeOnboarding,
        logout,
        clearOtpError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );

};

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
