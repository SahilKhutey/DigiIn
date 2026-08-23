import {
  VerificationRequestContext,
  RequestedDocument,
  RetrievalProgressStep,
  ConsentOption,
} from "./digilockerTypes";
import { WalletDocument } from "../../types";

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const DEMO_REQUEST_CONTEXT: VerificationRequestContext = {
  requestId: "req_abc_univ_2026",
  organizationName: "ABC University",
  organizationCategory: "Central Higher Education Institution",
  purpose: "Undergraduate Admission Eligibility Verification (AY 2026-27)",
  validityHours: 24,
  createdAt: new Date().toISOString(),
  requestedDocuments: [
    {
      id: "doc-10",
      title: "Class 10 Certificate",
      issuer: "Central Board of Secondary Education (CBSE)",
      purpose: "Date of birth and secondary passing status",
      requiredAttributes: ["Candidate Name", "Date of Birth", "Passing Year", "Roll Number"],
      isAvailableInVault: true,
      status: "verified",
    },
    {
      id: "doc-12",
      title: "Class 12 Certificate",
      issuer: "Central Board of Secondary Education (CBSE)",
      purpose: "Higher secondary eligibility and minimum 60.0% aggregate criteria",
      requiredAttributes: ["Passing Year", "Aggregate Percentage >= 60.0%", "Stream"],
      isAvailableInVault: true,
      status: "verified",
    },
  ],
};

const RETRIEVED_WALLET_DOCUMENTS: WalletDocument[] = [
  {
    documentId: "doc-10",
    title: "Class 10 Secondary School Certificate",
    documentType: "CLASS_X_CERTIFICATE",
    source: "GOVERNMENT_ISSUED",
    authenticity: "VERIFIED",
    validityStatus: "ACTIVE",
    verificationLevel: 4,
    verificationMethod: "DIGILOCKER_ISSUER_INTEGRATION",
    currentVersion: 1,
    issuer: "Central Board of Secondary Education",
    validUntil: null,
    extractedMetadata: {
      candidateName: "Rahul Sharma",
      dob: "2007-06-15",
      rollNo: "CBSE-X-2023-9941",
      passingYear: 2023,
    },
    createdAt: "2023-05-20T00:00:00Z",
  },
  {
    documentId: "doc-12",
    title: "Class 12 Senior School Certificate",
    documentType: "CLASS_XII_CERTIFICATE",
    source: "GOVERNMENT_ISSUED",
    authenticity: "VERIFIED",
    validityStatus: "ACTIVE",
    verificationLevel: 4,
    verificationMethod: "DIGILOCKER_ISSUER_INTEGRATION",
    currentVersion: 1,
    issuer: "Central Board of Secondary Education",
    validUntil: null,
    extractedMetadata: {
      candidateName: "Rahul Sharma",
      passingYear: 2025,
      percentage: 84.5,
      stream: "Science",
    },
    createdAt: "2025-05-15T00:00:00Z",
  },
];

export const digiLockerService = {
  async connect(): Promise<{ connected: boolean; provider: string }> {
    await delay(600);
    return { connected: true, provider: "DigiLocker" };
  },

  async getRequestContext(requestId: string): Promise<VerificationRequestContext> {
    await delay(200);
    return { ...DEMO_REQUEST_CONTEXT, requestId };
  },

  async authorizeConsent(
    requestId: string,
    options: ConsentOption
  ): Promise<{ authorized: boolean; consentId: string; validityExpiresAt: string }> {
    await delay(400);
    const expiresAt = new Date(Date.now() + options.durationHours * 3600 * 1000).toISOString();
    return {
      authorized: true,
      consentId: `cns_${Date.now().toString(36)}`,
      validityExpiresAt: expiresAt,
    };
  },

  async retrieveDocuments(
    requestId: string,
    onProgress?: (p: RetrievalProgressStep) => void
  ): Promise<WalletDocument[]> {
    onProgress?.({
      step: "CONNECTING",
      percent: 25,
      message: "Establishing secure TLS session with DigiLocker gateway...",
    });
    await delay(500);

    onProgress?.({
      step: "AUTHENTICATING",
      percent: 50,
      message: "Authenticating sovereign citizen consent token...",
    });
    await delay(500);

    onProgress?.({
      step: "FETCHING_CBSE",
      percent: 75,
      message: "Querying Central Board of Secondary Education source registry...",
    });
    await delay(600);

    onProgress?.({
      step: "COMPLETE",
      percent: 100,
      message: "2 of 2 certified credentials retrieved and validated at source.",
    });
    await delay(300);

    return RETRIEVED_WALLET_DOCUMENTS;
  },

  async disconnect(): Promise<{ connected: boolean }> {
    await delay(150);
    return { connected: false };
  },
};
