import { CitizenProfile, DemoPersona, OtpResult, VerifyResult } from "./authTypes";

const OTP_TTL_SECONDS = 60;

export const DEMO_PERSONAS: DemoPersona[] = [
  {
    id: "rahul-citizen",
    name: "Rahul Sharma",
    role: "CITIZEN",
    digiinId: "DIN-DEMO-001",
    organization: "Sovereign Citizen (Holder)",
    avatarBadge: "👤",
    mobile: "9876543210",
    description: "Student applicant for National Merit Scholarship with 4 verified credentials",
  },
  {
    id: "priya-citizen",
    name: "Priya Verma",
    role: "CITIZEN",
    digiinId: "DIN-DEMO-002",
    organization: "Sovereign Citizen (Holder)",
    avatarBadge: "👤",
    mobile: "9876500000",
    description: "Citizen applicant for PM-Kisan Agricultural Domicile subsidy",
  },
  {
    id: "du-verifier",
    name: "Delhi University Admission Office",
    role: "VERIFIER",
    digiinId: "ORG-DEMO-001",
    organization: "University Scholarship Service",
    avatarBadge: "🏢",
    mobile: "9876511111",
    description: "Institutional relying party verifying selective claims & proofs",
  },
  {
    id: "cbse-issuer",
    name: "CBSE Demo Authority",
    role: "ISSUER",
    digiinId: "ISS-DEMO-CBSE",
    organization: "Central Board of Secondary Education",
    avatarBadge: "🏛️",
    mobile: "9876522222",
    description: "Authoritative academic board credential issuer",
  },
  {
    id: "admin-root",
    name: "DigiIn Administrator",
    role: "ADMIN",
    digiinId: "ADMIN-DEMO-01",
    organization: "Root Trust & Observability Infrastructure",
    avatarBadge: "🛡️",
    mobile: "9876599999",
    description: "Platform operator managing trust registry, health & audit logs",
  },
];

interface ActiveOtpSession {
  mobile: string;
  code: string;
  createdAt: number;
  attempts: number;
}

let activeSession: ActiveOtpSession | null = null;


const EXISTING_CITIZENS: Record<string, Partial<CitizenProfile>> = {
  "9876543210": {
    name: "Rahul Sharma",
    digiinId: "DIN-84K2-19Q7",
    language: "en",
    isFirstTime: false,
    ekycVerified: true,
    documentsCount: 12,
    verifiedCount: 9,
  },
  "9876500000": {
    name: "Priya Patel",
    digiinId: "DIN-3N8V-55B1",
    language: "hi",
    isFirstTime: false,
    ekycVerified: true,
    documentsCount: 8,
    verifiedCount: 7,
  },
};

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const mockAuthBackend = {
  async sendOtp(mobile: string): Promise<OtpResult> {
    await delay(350);

    // Standard demo code is 123456
    activeSession = {
      mobile,
      code: "123456",
      createdAt: Date.now(),
      attempts: 0,
    };

    return {
      success: true,
      mobile,
      expiresInSeconds: OTP_TTL_SECONDS,
      message: `OTP dispatched to +91 ${mobile}`,
    };
  },

  async verifyOtp(mobile: string, code: string): Promise<VerifyResult> {
    await delay(400);

    if (!activeSession || activeSession.mobile !== mobile) {
      // Allow seamless demo verification if direct code entered
      if (code === "123456") {
        const isExisting = mobile in EXISTING_CITIZENS;
        const profileData = EXISTING_CITIZENS[mobile] || {
          name: "Rahul Sharma",
          digiinId: "DIN-7K4P-92M8",
          language: "en",
          isFirstTime: !isExisting,
          ekycVerified: true,
          documentsCount: 12,
          verifiedCount: 9,
        };

        const profile: CitizenProfile = {
          mobile,
          name: profileData.name || "Citizen User",
          digiinId: profileData.digiinId || "DIN-7K4P-92M8",
          language: (profileData.language as "en" | "hi") || "en",
          isFirstTime: profileData.isFirstTime ?? !isExisting,
          ekycVerified: profileData.ekycVerified ?? true,
          documentsCount: profileData.documentsCount ?? 12,
          verifiedCount: profileData.verifiedCount ?? 9,
          sessionExpiresAt: Date.now() + 3600 * 1000,
        };

        return { success: true, profile, isFirstTime: profile.isFirstTime };
      }

      return {
        success: false,
        error: "EXPIRED",
        message: "This OTP has expired. Request a new OTP to continue.",
      };
    }

    const elapsedSeconds = (Date.now() - activeSession.createdAt) / 1000;
    if (elapsedSeconds > OTP_TTL_SECONDS) {
      activeSession = null;
      return {
        success: false,
        error: "EXPIRED",
        message: "This OTP has expired. Request a new OTP to continue.",
      };
    }

    activeSession.attempts += 1;
    if (activeSession.attempts > 4) {
      activeSession = null;
      return {
        success: false,
        error: "MAX_ATTEMPTS",
        message: "Too many failed attempts. Please request a new OTP.",
      };
    }

    if (code !== activeSession.code && code !== "123456") {
      return {
        success: false,
        error: "INVALID_CODE",
        message: "We couldn't verify that code. Check the OTP and try again.",
      };
    }

    // OTP Verified Successfully
    const isExisting = mobile in EXISTING_CITIZENS;
    const profileData = EXISTING_CITIZENS[mobile] || {
      name: "Rahul Sharma",
      digiinId: "DIN-7K4P-92M8",
      language: "en",
      isFirstTime: !isExisting,
      ekycVerified: true,
      documentsCount: 12,
      verifiedCount: 9,
    };

    const profile: CitizenProfile = {
      mobile,
      name: profileData.name || "Citizen User",
      digiinId: profileData.digiinId || "DIN-7K4P-92M8",
      language: (profileData.language as "en" | "hi") || "en",
      isFirstTime: profileData.isFirstTime ?? !isExisting,
      ekycVerified: profileData.ekycVerified ?? true,
      documentsCount: profileData.documentsCount ?? 12,
      verifiedCount: profileData.verifiedCount ?? 9,
      sessionExpiresAt: Date.now() + 3600 * 1000,
    };

    activeSession = null;
    return { success: true, profile, isFirstTime: profile.isFirstTime };
  },

  async completeOnboarding(
    mobile: string,
    data: { name: string; language: "en" | "hi" }
  ): Promise<CitizenProfile> {
    await delay(300);

    const profile: CitizenProfile = {
      mobile,
      name: data.name,
      digiinId: "DIN-7K4P-92M8",
      language: data.language,
      isFirstTime: false,
      ekycVerified: true,
      documentsCount: 12,
      verifiedCount: 9,
      sessionExpiresAt: Date.now() + 3600 * 1000,
    };

    // Save to existing citizens registry
    EXISTING_CITIZENS[mobile] = profile;
    return profile;
  },

  async loginAsPersona(personaId: string): Promise<CitizenProfile> {
    await delay(150);
    const persona = DEMO_PERSONAS.find((p) => p.id === personaId) || DEMO_PERSONAS[0];
    const profile: CitizenProfile = {
      mobile: persona.mobile,
      name: persona.name,
      digiinId: persona.digiinId,
      role: persona.role,
      language: "en",
      isFirstTime: false,
      ekycVerified: true,
      documentsCount: 12,
      verifiedCount: 9,
      sessionExpiresAt: Date.now() + 86400 * 1000,
    };
    return profile;
  },
};

