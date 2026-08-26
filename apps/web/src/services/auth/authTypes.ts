export type AuthState = "AUTH_UNKNOWN" | "SIGNED_OUT" | "ONBOARDING" | "AUTHENTICATED";

export type OtpStatus = "IDLE" | "REQUESTING" | "SENT" | "VERIFYING" | "INVALID" | "EXPIRED";

export type UserRole = "CITIZEN" | "ISSUER" | "VERIFIER" | "ADMIN";

export interface CitizenProfile {
  mobile: string;
  name: string;
  digiinId: string;
  role?: UserRole;
  language: "en" | "hi";
  isFirstTime: boolean;
  ekycVerified: boolean;
  documentsCount: number;
  verifiedCount: number;
  sessionExpiresAt: number;
}

export interface DemoPersona {
  id: string;
  name: string;
  role: UserRole;
  digiinId: string;
  organization: string;
  avatarBadge: string;
  mobile: string;
  description: string;
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
