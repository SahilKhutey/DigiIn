export type VerificationStatus =
  | "VERIFIED"
  | "NOT_VERIFIED"
  | "PENDING"
  | "EXPIRED"
  | "REVOKED"
  | "NOT_FOUND"
  | "ISSUER_UNAVAILABLE"
  | "IDENTITY_MISMATCH"
  | "INSUFFICIENT_EVIDENCE"
  | "PARTIAL";

export type DisclosureMode = "MINIMUM" | "ATTRIBUTE" | "DOCUMENT_REQUIRED";

export type FeatureFlag = {
  key: string;
  enabled: boolean;
  description: string;
};

export type DomainEvent = {
  eventId: string;
  type: string;
  aggregateId: string;
  actor: string;
  message: string;
  createdAt: string;
};

export type UploadedDocument = {
  documentId: string;
  ownerSubjectId: string;
  documentType: string;
  source: "CITIZEN_UPLOAD" | "GOVERNMENT_ISSUED" | "LEGACY_RECORD";
  filename: string;
  status: "UPLOADED" | "CLASSIFIED" | "PENDING_VERIFICATION" | "VERIFIED" | "REJECTED";
  authenticity: "UNKNOWN" | "VERIFIED" | "REJECTED";
  verificationLevel: number;
  extractedMetadata: Record<string, unknown>;
  createdAt: string;
};

export type VerificationCase = {
  caseId: string;
  documentId: string;
  claimedIssuer: string;
  status: "NEW" | "OCR_COMPLETE" | "ISSUER_MATCHED" | "UNDER_REVIEW" | "VERIFIED" | "REJECTED" | "NEEDS_EVIDENCE";
  automatedMatchScore: number;
  recommendedAction: string;
  verifierQueue: string;
  createdAt: string;
  decidedAt?: string | null;
};

export type CredentialProofResult = {
  credential: string;
  verified: boolean;
  status: VerificationStatus;
  issuer?: string | null;
  level: number;
  disclosedAttributes: Record<string, unknown>;
  message: string;
};

export type VerificationResult = {
  verificationId: string;
  requestId: string;
  status: VerificationStatus;
  subjectId: string;
  audience: string;
  purpose: string;
  disclosureLevel: "BOOLEAN" | "ATTRIBUTE" | "DOCUMENT";
  results: CredentialProofResult[];
  proof: {
    type: "signed_verification_token";
    token: string;
    algorithm: "HS256";
  };
  receipt: {
    verificationId: string;
    requesterName: string;
    purpose: string;
    status: VerificationStatus;
    shared: string[];
    documentShared: boolean;
    issuedAt: string;
    expiresAt: string;
  };
  issuedAt: string;
  expiresAt: string;
};

export type StudentDemoResult = {
  document: UploadedDocument;
  verificationCase: VerificationCase;
  transaction: {
    transactionId: string;
    actor: string;
    purpose: string;
    requestedCredentials: string[];
    currentStage: string;
    state: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";
    createdAt: string;
    completedAt?: string | null;
    failureReason?: string | null;
  };
  proofResult: VerificationResult;
  events: DomainEvent[];
};
