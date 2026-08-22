export type Stage = {
  name: string;
  status: "complete" | "attention" | "blocked" | "not_started";
  message: string;
  owner: string;
  nextAction?: string;
};

export type Recovery = {
  label: string;
  type: string;
  guidance: string;
};

export type Diagnostic = {
  transactionId: string;
  documentLabel: string;
  trustLabel: string;
  overallStatus: "resolved" | "action_required" | "unavailable";
  issueCode: string;
  issuerStatus: string;
  summary: string;
  steps: Stage[];
  recovery: Recovery;
  fallbackAvailable: boolean;
  supportReference: string;
};

export type Scenario = {
  id: string;
  title: string;
  description: string;
};

export type DocumentOption = {
  id: string;
  label: string;
  category: string;
  trustLabel: string;
};

export type VerificationRequirement = {
  credential: string;
  minimumLevel: number;
  attributes: string[];
};

export type VerificationRequest = {
  requestId: string;
  requesterName: string;
  purpose: string;
  audience: string;
  consentText: string;
  status: string;
  expiresAt: string;
  requirements: VerificationRequirement[];
  disclosure: { mode: string };
};

export type VerificationPredicate = {
  attribute: string;
  operator: "EQ" | "GTE" | "LTE" | "IN" | "EXISTS";
  value: unknown;
  label?: string;
};

export type PredicateProofResult = {
  predicateId: string;
  claimName: string;
  expression: string;
  satisfied: boolean;
  proofType: "DERIVED_ZERO_KNOWLEDGE_PREDICATE";
  maskedAttributes: string[];
};

export type SelectiveDisclosurePreference = {
  mode: "PREDICATE_ONLY" | "SELECTIVE_ATTRIBUTES" | "FULL_DOCUMENT";
  selectedAttributes: string[];
  selectedPredicates: string[];
};

export type CredentialResult = {
  credential: string;
  verified: boolean;
  status: string;
  issuer?: string;
  level: number;
  disclosedAttributes: Record<string, string | number | boolean>;
  predicateResults?: PredicateProofResult[];
  maskedAttributes?: string[];
  message: string;
};

export type JwkKey = {
  kty: string;
  kid: string;
  use: string;
  alg: string;
  crv?: string;
  x?: string;
  n?: string;
  e?: string;
};

export type JwksResponse = {
  keys: JwkKey[];
};

export type VerificationResult = {
  verificationId: string;
  status: string;
  audience: string;
  purpose: string;
  disclosureLevel: string;
  results: CredentialResult[];
  predicateProofs?: PredicateProofResult[];
  maskedAttributesSummary?: string[];
  proof: { token: string; algorithm: string; keyId?: string };
  receipt: {
    requesterName: string;
    purpose: string;
    shared: string[];
    documentShared: boolean;
    issuedAt: string;
    expiresAt: string;
  };
};


export type TokenCheck = {
  active: boolean;
  status: string;
  message: string;
  verificationId?: string;
  audience?: string;
  claims?: Record<string, unknown>;
  cryptoVerified?: boolean;
};


export type PlatformEvent = {
  eventId: string;
  type: string;
  aggregateId: string;
  actor: string;
  message: string;
  createdAt: string;
};

export type DocumentVersionRecord = {
  versionId: string;
  versionNumber: number;
  documentId: string;
  parentVersionId?: string | null;
  status: "ACTIVE" | "SUPERSEDED" | "ARCHIVED" | "REVOKED";
  metadata: Record<string, string | number | boolean>;
  changeSummary: string;
  authority: string;
  evidenceReference?: string | null;
  createdAt: string;
  supersededAt?: string | null;
};

export type CorrectionRequestRecord = {
  requestId: string;
  documentId: string;
  subjectId: string;
  field: string;
  currentValue: string;
  proposedValue: string;
  reason: string;
  evidenceDescription?: string;
  evidenceReference?: string;
  status: "PENDING_REVIEW" | "APPROVED" | "REJECTED" | "MORE_INFO_REQUIRED";
  resultingVersion?: number | null;
  reviewerId?: string | null;
  reviewerNote?: string | null;
  createdAt: string;
  decidedAt?: string | null;
};

export type VerifierQueueId = "queue_cbse" | "queue_revenue" | "queue_transport" | "queue_general";

export type VerifierQueueSummary = {
  queueId: VerifierQueueId;
  name: string;
  department: string;
  pendingCount: number;
  verifiedCount: number;
  totalCount: number;
};

export type FieldComparison = {
  field: string;
  label: string;
  citizenValue: string;
  registryValue: string;
  isMatch: boolean;
  matchConfidence: number;
  discrepancyNote?: string;
};

export type EvidenceComparisonDetail = {
  caseId: string;
  documentId: string;
  documentType: string;
  subjectId: string;
  verifierQueue: VerifierQueueId;
  claimedIssuer: string;
  overallMatchScore: number;
  recommendedAction: string;
  citizenClaims: Record<string, unknown>;
  officialRegistryClaims: Record<string, unknown>;
  fieldComparisons: FieldComparison[];
  caseStatus: string;
  createdAt: string;
};

export type GovernmentDecisionPayload = {
  decision: "VERIFY" | "REJECT" | "REQUEST_MORE_EVIDENCE" | "TRANSFER" | "MARK_DUPLICATE";
  verifierId: string;
  note: string;
  transferQueue?: VerifierQueueId | null;
};

export type VerificationCase = {
  caseId: string;
  documentId: string;
  claimedIssuer: string;
  status: "NEW" | "OCR_COMPLETE" | "ISSUER_MATCHED" | "UNDER_REVIEW" | "VERIFIED" | "REJECTED" | "NEEDS_EVIDENCE";
  automatedMatchScore: number;
  recommendedAction: string;
  verifierQueue: VerifierQueueId;
  createdAt: string;
  decidedAt?: string | null;
  decision?: {
    decision: string;
    verifierId: string;
    note: string;
    transferQueue?: string | null;
  } | null;
};


export type PlatformSnapshot = {
  featureFlags: { key: string; enabled: boolean; description: string }[];
  mockIntegrations: {
    integrationId: string;
    name: string;
    status: string;
    supportedCredentials: string[];
  }[];
  documents: {
    documentId: string;
    documentType: string;
    status: string;
    currentVersion: number;
    extractedMetadata: Record<string, unknown>;
  }[];
  versions: DocumentVersionRecord[];
  verificationCases: unknown[];
  corrections: CorrectionRequestRecord[];
  transactions: unknown[];
  events: PlatformEvent[];
};

export type StudentDemo = {
  document: {
    documentId: string;
    documentType: string;
    status: string;
    authenticity: string;
    verificationLevel: number;
    currentVersion: number;
  };
  verificationCase: {
    caseId: string;
    status: string;
    claimedIssuer: string;
    automatedMatchScore: number;
  };
  transaction: {
    transactionId: string;
    currentStage: string;
    state: string;
  };
  proofResult: VerificationResult;
  events: PlatformEvent[];
};

export type DocumentClassificationResult = {
  documentId: string;
  documentType: string;
  confidenceScore: number;
  extractedFields: Record<string, unknown>;
  detectedIssuer: string;
  suggestedQueue: VerifierQueueId;
  classificationNotes: string[];
  sha256: string;
  fileSizeKb: number;
};

export type DirectUploadPayload = {
  ownerSubjectId?: string;
  filename: string;
  documentTypeHint?: string;
  simulatedContent?: string;
};

export type DocumentSource = "GOVERNMENT_ISSUED" | "CITIZEN_UPLOAD" | "LEGACY_RECORD";
export type AuthenticityStatus = "VERIFIED" | "UNKNOWN" | "REJECTED";
export type ValidityStatus = "ACTIVE" | "EXPIRED" | "REVOKED" | "SUPERSEDED";

export type WalletDocument = {
  documentId: string;
  title: string;
  documentType: string;
  source: DocumentSource;
  authenticity: AuthenticityStatus;
  validityStatus: ValidityStatus;
  verificationLevel: number;
  verificationMethod: string;
  currentVersion: number;
  issuer: string;
  validUntil?: string | null;
  extractedMetadata: Record<string, unknown>;
  createdAt: string;
};

export type PipelineUploadResponse = {
  document: {
    documentId: string;
    documentType: string;
    status: string;
    authenticity: string;
    verificationLevel: number;
    currentVersion: number;
  };
  classification: DocumentClassificationResult;
  verificationCase: VerificationCase;
  walletDocument: WalletDocument;
  message: string;
};

export type SupportSafeSummary = {
  supportCode: string;
  timestamp: string;
  scenarioId: string;
  failureStage: string;
  diagnosticTitle: string;
  plainLanguageExplanation: string;
  affectedAuthority: string;
  issuerStatus: string;
  correlationId: string;
  guidanceForCitizen: string[];
  guidanceForDeskOfficer: string[];
  securityNotice: string;
  qrDigest: string;
};

export type ConsentRecord = {
  consentId: string;
  verificationId: string;
  requestId: string;
  subjectId: string;
  requesterName: string;
  clientId: string;
  purpose: string;
  audience: string;
  disclosureLevel: string;
  credentialsVerified: string[];
  predicateCount: number;
  maskedAttributesCount: number;
  status: "ACTIVE" | "REVOKED" | "EXPIRED";
  issuedAt: string;
  expiresAt: string;
  revokedAt?: string | null;
  revocationReason?: string | null;
};

export type RevokeConsentPayload = {
  reason: string;
};

export type EkycOtpRequest = {
  aadhaarRef: string;
  purpose?: string;
};

export type EkycOtpResponse = {
  txnId: string;
  maskedMobile: string;
  expiresInSeconds: number;
  demoOtpHint: string;
  message: string;
};

export type EkycVerifyRequest = {
  txnId: string;
  otp: string;
  documentId?: string;
};

export type EkycIdentitySnapshot = {
  name: string;
  dob: string;
  gender: string;
  maskedAadhaar: string;
  state: string;
  district: string;
  pincode: string;
};

export type EkycMatchResult = {
  nameMatch: boolean;
  dobMatch: boolean;
  stateMatch: boolean;
  score: number;
  verdict: "EXACT_MATCH" | "HIGH_CONFIDENCE_MATCH" | "PARTIAL_MATCH" | "MISMATCH";
  claimedValues: Record<string, string>;
  officialValues: Record<string, string>;
  notes: string[];
};

export type EkycVerifyResponse = {
  txnId: string;
  status: "VERIFIED" | "FAILED" | "EXPIRED";
  identitySnapshot: EkycIdentitySnapshot;
  matchResult: EkycMatchResult;
  elevatedDocumentLevel?: number;
  ekycProofToken: string;
  keyId: string;
  algorithm: "EdDSA";
  verifiedAt: string;
  message: string;
};

export type EkycMatchDemographicsRequest = {
  claimedName: string;
  claimedDob?: string;
  claimedState?: string;
  aadhaarRef: string;
};








