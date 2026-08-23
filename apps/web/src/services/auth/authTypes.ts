export type AuthState = "AUTH_UNKNOWN" | "SIGNED_OUT" | "ONBOARDING" | "AUTHENTICATED";

export type OtpStatus = "IDLE" | "REQUESTING" | "SENT" | "VERIFYING" | "INVALID" | "EXPIRED";

export interface CitizenProfile {
  mobile: string;
  name: string;
  digiinId: string;
  language: "en" | "hi";
  isFirstTime: boolean;
  ekycVerified: boolean;
  documentsCount: number;
  verifiedCount: number;
  sessionExpiresAt: number;
}

export interface OtpResult {
  success: boolean;
  mobile: string;
  expiresInSeconds: number;
  message?: string;
}

export interface VerifyResult {
  success: boolean;
  profile?: CitizenProfile;
  isFirstTime?: boolean;
  error?: "INVALID_CODE" | "EXPIRED" | "MAX_ATTEMPTS" | "NETWORK_ERROR";
  message?: string;
}
