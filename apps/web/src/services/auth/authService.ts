import { mockAuthBackend } from "./mockAuth";
import { CitizenProfile, OtpResult, VerifyResult } from "./authTypes";

const SESSION_STORAGE_KEY = "digiin_citizen_auth_session";

export const authService = {
  async requestOtp(mobile: string): Promise<OtpResult> {
    return mockAuthBackend.sendOtp(mobile);
  },

  async verifyOtp(mobile: string, code: string): Promise<VerifyResult> {
    const result = await mockAuthBackend.verifyOtp(mobile, code);
    if (result.success && result.profile) {
      this.saveSession(result.profile);
    }
    return result;
  },

  async resendOtp(mobile: string): Promise<OtpResult> {
    return mockAuthBackend.sendOtp(mobile);
  },

  async completeOnboarding(
    mobile: string,
    data: { name: string; language: "en" | "hi" }
  ): Promise<CitizenProfile> {
    const profile = await mockAuthBackend.completeOnboarding(mobile, data);
    this.saveSession(profile);
    return profile;
  },

  saveSession(profile: CitizenProfile): void {
    try {
      localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(profile));
    } catch {
      // Fallback
    }
  },

  getSession(): CitizenProfile | null {
    try {
      const saved = localStorage.getItem(SESSION_STORAGE_KEY);
      if (!saved) return null;
      const profile = JSON.parse(saved) as CitizenProfile;
      if (Date.now() > profile.sessionExpiresAt) {
        this.clearSession();
        return null;
      }
      return profile;
    } catch {
      return null;
    }
  },

  clearSession(): void {
    try {
      localStorage.removeItem(SESSION_STORAGE_KEY);
    } catch {
      // Fallback
    }
  },
};
