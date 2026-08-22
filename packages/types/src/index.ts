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

export type DocumentVersionStatus = "ACTIVE" | "SUPERSEDED" | "ARCHIVED" | "REVOKED";

export type DocumentVersionRecord = {
  versionId: string;
  versionNumber: number;
  documentId: string;
  parentVersionId?: string | null;
  status: DocumentVersionStatus;
  metadata: Record<string, unknown>;
  changeSummary: string;
  authority: string;
  evidenceReference?: string | null;
  createdAt: string;
  supersededAt?: string | null;
};

export type DocumentSource = "GOVERNMENT_ISSUED" | "CITIZEN_UPLOAD" | "LEGACY_RECORD";
export type AuthenticityStatus = "VERIFIED" | "UNKNOWN" | "REJECTED";
export type ValidityStatus = "ACTIVE" | "EXPIRED" | "REVOKED" | "SUPERSEDED";

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

export type PipelineUploadResponse = {
  document: UploadedDocument;
  classification: DocumentClassificationResult;
  verificationCase: VerificationCase;
  walletDocument: WalletDocument;
  message: string;
};

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



export type UploadedDocument = {
  documentId: string;
  ownerSubjectId: string;
  documentType: string;
  source: DocumentSource;
  filename: string;
  status: "UPLOADED" | "CLASSIFIED" | "PENDING_VERIFICATION" | "VERIFIED" | "REJECTED";
  authenticity: AuthenticityStatus;
  verificationLevel: number;
  currentVersion: number;
  extractedMetadata: Record<string, unknown>;
  createdAt: string;
};


export type CorrectionStatus = "PENDING_REVIEW" | "APPROVED" | "REJECTED" | "MORE_INFO_REQUIRED";

export type CorrectionDecisionType = "APPROVE" | "REJECT" | "REQUEST_EVIDENCE";

export type CorrectionRequestCreate = {
  documentId: string;
  field: string;
  currentValue: string;
  proposedValue: string;
  reason: string;
  evidenceDescription?: string;
  evidenceReference?: string;
};

export type CorrectionReviewDecision = {
  decision: CorrectionDecisionType;
  reviewerId: string;
  note: string;
  correctedFields?: Record<string, unknown>;
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
  status: CorrectionStatus;
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

export type VerificationAuthorization = {
  allow: boolean;
  subjectId: string;
  customDisclosure?: SelectiveDisclosurePreference;
};

export type CredentialProofResult = {
  credential: string;
  verified: boolean;
  status: VerificationStatus;
  issuer?: string | null;
  level: number;
  disclosedAttributes: Record<string, unknown>;
  predicateResults?: PredicateProofResult[];
  maskedAttributes?: string[];
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
  predicateProofs?: PredicateProofResult[];
  maskedAttributesSummary?: string[];
  proof: {
    type: "signed_verification_token";
    token: string;
    algorithm: "EdDSA" | "RS256" | "HS256";
    keyId?: string;
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

export type PlatformSnapshot = {
  featureFlags: FeatureFlag[];
  mockIntegrations: {
    integrationId: string;
    name: string;
    status: string;
    supportedCredentials: string[];
  }[];
  documents: UploadedDocument[];
  versions: DocumentVersionRecord[];
  verificationCases: VerificationCase[];
  corrections: CorrectionRequestRecord[];
  transactions: {
    transactionId: string;
    actor: string;
    purpose: string;
    requestedCredentials: string[];
    currentStage: string;
    state: string;
    createdAt: string;
  }[];
  events: DomainEvent[];
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
  disclosureLevel: "BOOLEAN" | "ATTRIBUTE" | "DOCUMENT";
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


