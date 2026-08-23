export type RequestStatus =
  | "CREATED"
  | "SENT"
  | "AWAITING_CONSENT"
  | "CONSENT_GRANTED"
  | "DOCUMENT_RETRIEVING"
  | "VERIFYING"
  | "COMPLETED"
  | "DECLINED"
  | "EXPIRED"
  | "CANCELLED";

export interface VerificationRequestDocument {
  id: string;
  title: string;
  required: boolean;
  reason: string;
}

export interface VerificationRequestItem {
  id: string;
  citizenId: string;
  citizenName: string;
  purpose: string;
  documents: VerificationRequestDocument[];
  validityHours: number;
  status: RequestStatus;
  createdAt: string;
  completedAt?: string | null;
  expiresAt: string;
  consent: {
    granted: boolean;
    grantedAt?: string | null;
    scope: string;
  };
  verificationResult?: {
    status: string;
    verifiedCount: number;
    totalCount: number;
    verificationId: string;
    proofId: string;
  } | null;
}
