export interface RequestedDocument {
  id: string;
  title: string;
  issuer: string;
  purpose: string;
  requiredAttributes: string[];
  isAvailableInVault: boolean;
  status: "verified" | "pending" | "retrieving";
}

export interface VerificationRequestContext {
  requestId: string;
  organizationName: string;
  organizationCategory: string;
  purpose: string;
  requestedDocuments: RequestedDocument[];
  validityHours: number;
  createdAt: string;
}

export interface RetrievalProgressStep {
  step: "CONNECTING" | "AUTHENTICATING" | "FETCHING_CBSE" | "FETCHING_UIDAI" | "COMPLETE";
  percent: number;
  message: string;
}

export interface ConsentOption {
  zkpMode: boolean;
  durationHours: number;
  allowAuditLog: boolean;
}
