export type VerificationStage =
  | "INITIALIZING"
  | "INTEGRITY_CHECK"
  | "ISSUER_MATCH"
  | "DETAIL_CHECK"
  | "PROOF_MINTING"
  | "COMPLETE"
  | "FAILED";

export type VerificationOutcome = "VERIFIED" | "PARTIALLY_VERIFIED" | "FAILED";

export interface VerificationCheck {
  type: string;
  label: string;
  status: "passed" | "failed" | "warning" | "pending";
  message: string;
}

export interface DocumentVerificationItem {
  documentId: string;
  title: string;
  issuer: string;
  level: number;
  integrityValid: boolean;
  issuerSignatureValid: boolean;
  predicatesSatisfied: boolean;
  predicateExpression?: string;
  status: "verified" | "failed" | "pending" | "partial";
  verifiedAt?: string;
  checks: VerificationCheck[];
  claims: Record<string, string | number | boolean>;
}

export interface VerificationProgressEvent {
  stage: VerificationStage;
  percent: number;
  title: string;
  message: string;
}

export interface VerificationResultPayload {
  verificationId: string;
  status: VerificationOutcome;
  outcomeMessage: string;
  requesterName: string;
  purpose: string;
  issuedAt: string;
  expiresAt: string;
  documents: DocumentVerificationItem[];
  proofToken: string;
  keyId: string;
  algorithm: "EdDSA";
  disclosedClaims: Record<string, unknown>;
}
