import type {
  ConsentRecord,
  ConsentSubmitResponse,
  CorrectionRequestRecord,
  Diagnostic,
  DirectUploadPayload,
  DocumentOption,
  EkycMatchDemographicsRequest,
  EkycMatchResult,
  EkycOtpResponse,
  EkycVerifyResponse,
  EvidenceComparisonDetail,
  GovernmentDecisionPayload,
  JwksResponse,
  LabTestResult,
  PipelineUploadResponse,
  PlatformEvent,
  PlatformSnapshot,
  Scenario,
  ScholarshipApplicationResponse,
  SelectiveDisclosurePreference,
  SharingReviewResponse,
  StudentDemo,
  SupportSafeSummary,
  TokenCheck,
  VerificationCase,
  VerificationRequest,
  VerificationResult,
  VerifierQueueId,
  VerifierQueueSummary,
  WalletDocument,
  FederatedIssuer,
  FederatedCredential,
  RevocationRecord,
  RevocationRegistryResponse,
} from "../types";




const rawBase = import.meta.env.VITE_API_BASE_URL ?? import.meta.env.VITE_API_URL ?? "http://localhost:8000";
export const API_BASE = String(rawBase).replace(/\/+$/, "");

export async function fetchJwks(): Promise<JwksResponse> {
  const res = await fetch(`${API_BASE}/.well-known/jwks.json`);
  if (!res.ok) throw new Error("Failed to fetch public JWKS keys");
  return res.json();
}

export async function fetchSupportSummary(
  scenarioId: string
): Promise<SupportSafeSummary> {
  const res = await fetch(`${API_BASE}/api/v1/transactions/${scenarioId}/support-summary`);
  if (!res.ok) throw new Error("Failed to fetch support summary");
  return res.json();
}



export async function uploadDocumentPipeline(
  payload: DirectUploadPayload
): Promise<PipelineUploadResponse> {
  const res = await fetch(`${API_BASE}/api/v1/documents/upload-pipeline`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to execute document upload and OCR pipeline");
  return res.json();
}


export async function fetchVerifierQueues(): Promise<VerifierQueueSummary[]> {
  const res = await fetch(`${API_BASE}/api/v1/verifier/queues`);
  if (!res.ok) throw new Error("Failed to fetch verifier queues");
  return res.json();
}

export async function fetchVerifierCases(
  queueId?: VerifierQueueId,
  status?: string
): Promise<VerificationCase[]> {
  const params = new URLSearchParams();
  if (queueId) params.append("queue_id", queueId);
  if (status) params.append("status", status);
  const query = params.toString() ? `?${params.toString()}` : "";
  const res = await fetch(`${API_BASE}/api/v1/verifier/cases${query}`);
  if (!res.ok) throw new Error("Failed to fetch verifier cases");
  return res.json();
}

export async function fetchCaseComparison(
  caseId: string
): Promise<EvidenceComparisonDetail> {
  const res = await fetch(`${API_BASE}/api/v1/verifier/cases/${caseId}/comparison`);
  if (!res.ok) throw new Error("Failed to fetch evidence comparison");
  return res.json();
}

export async function submitVerifierDecision(
  caseId: string,
  payload: GovernmentDecisionPayload
): Promise<VerificationCase> {
  const res = await fetch(`${API_BASE}/api/v1/verifier/cases/${caseId}/decision`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to submit verifier decision");
  return res.json();
}


export async function fetchWalletDocuments(
  subjectId: string = "subj_demo_5c7b90"
): Promise<WalletDocument[]> {
  const res = await fetch(`${API_BASE}/api/v1/wallet/documents?subject_id=${subjectId}`);
  if (!res.ok) throw new Error("Failed to fetch wallet documents");
  return res.json();
}


export async function fetchScenarios(): Promise<Scenario[]> {
  const res = await fetch(`${API_BASE}/api/v1/scenarios`);
  if (!res.ok) throw new Error("Failed to fetch scenarios");
  return res.json();
}

export async function fetchDocuments(): Promise<DocumentOption[]> {
  const res = await fetch(`${API_BASE}/api/v1/documents`);
  if (!res.ok) throw new Error("Failed to fetch documents");
  return res.json();
}

export async function fetchDiagnosis(scenarioId: string): Promise<Diagnostic> {
  const res = await fetch(`${API_BASE}/api/v1/transactions/${scenarioId}/diagnosis`);
  if (!res.ok) throw new Error("Failed to fetch diagnosis");
  return res.json();
}

export async function retryTransaction(scenarioId: string): Promise<Diagnostic> {
  const res = await fetch(`${API_BASE}/api/v1/transactions/${scenarioId}/retry`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to retry transaction");
  return res.json();
}

export async function createExamProofRequest(): Promise<VerificationRequest> {
  const res = await fetch(`${API_BASE}/api/v1/verification/request/demo-exam`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to create proof request");
  return res.json();
}

export async function authorizeVerificationRequest(
  requestId: string,
  allow: boolean = true,
  customDisclosure?: SelectiveDisclosurePreference
): Promise<VerificationResult> {
  const res = await fetch(`${API_BASE}/api/v1/verification/request/${requestId}/authorize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      allow,
      subjectId: "subj_demo_5c7b90",
      customDisclosure,
    }),
  });
  if (!res.ok) throw new Error("Failed to authorize verification");
  return res.json();
}


export async function introspectProofToken(
  token: string,
  audience: string
): Promise<TokenCheck> {
  const res = await fetch(`${API_BASE}/api/v1/verification/introspect`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, audience }),
  });
  if (!res.ok) throw new Error("Failed to introspect proof token");
  return res.json();
}

export async function fetchPlatformSnapshot(): Promise<PlatformSnapshot> {
  const res = await fetch(`${API_BASE}/api/v1/platform/snapshot`);
  if (!res.ok) throw new Error("Failed to fetch platform snapshot");
  return res.json();
}

export async function runStudentDemo(): Promise<StudentDemo> {
  const res = await fetch(`${API_BASE}/api/v1/platform/demo/student`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to run student demo");
  return res.json();
}

export async function submitCorrectionRequest(
  documentId: string,
  data: {
    field: string;
    currentValue: string;
    proposedValue: string;
    reason: string;
    evidenceDescription?: string;
    evidenceReference?: string;
  }
): Promise<CorrectionRequestRecord> {
  const res = await fetch(`${API_BASE}/api/v1/documents/${documentId}/corrections`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to submit correction request");
  return res.json();
}

export async function decideCorrectionRequest(
  requestId: string,
  decision: "APPROVE" | "REJECT",
  reviewerId: string = "officer_cbse_senior_evaluator",
  note?: string
): Promise<CorrectionRequestRecord> {
  const res = await fetch(`${API_BASE}/api/v1/corrections/${requestId}/decision`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      decision,
      reviewerId,
      note:
        note ??
        (decision === "APPROVE"
          ? "Discrepancy verified against secondary gazette and identity records."
          : "Evidence insufficient for requested modification."),
    }),
  });
  if (!res.ok) throw new Error("Failed to record correction decision");
  return res.json();
}

export async function fetchConsents(
  subjectId: string = "subj_demo_5c7b90"
): Promise<ConsentRecord[]> {
  const res = await fetch(`${API_BASE}/api/v1/consent?subject_id=${encodeURIComponent(subjectId)}`);
  if (!res.ok) throw new Error("Failed to fetch consent records");
  return res.json();
}

export async function revokeConsent(
  verificationId: string,
  reason: string = "Citizen revoked credential verification access."
): Promise<ConsentRecord> {
  const res = await fetch(`${API_BASE}/api/v1/consent/${verificationId}/revoke`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason }),
  });
  if (!res.ok) throw new Error("Failed to revoke consent authorization");
  return res.json();
}

export async function fetchAuditEvents(
  eventType?: string,
  aggregateId?: string
): Promise<PlatformEvent[]> {
  const params = new URLSearchParams();
  if (eventType) params.append("event_type", eventType);
  if (aggregateId) params.append("aggregate_id", aggregateId);
  const query = params.toString() ? `?${params.toString()}` : "";
  const res = await fetch(`${API_BASE}/api/v1/audit/events${query}`);
  if (!res.ok) throw new Error("Failed to fetch audit events");
  return res.json();
}

export async function generateEkycOtp(
  aadhaarRef: string,
  purpose: string = "Citizen Identity Verification"
): Promise<EkycOtpResponse> {
  const res = await fetch(`${API_BASE}/api/v1/ekyc/generate-otp`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ aadhaarRef, purpose }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to generate eKYC OTP");
  }
  return res.json();
}

export async function verifyEkycOtp(
  txnId: string,
  otp: string,
  documentId?: string
): Promise<EkycVerifyResponse> {
  const res = await fetch(`${API_BASE}/api/v1/ekyc/verify-otp`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ txnId, otp, documentId }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to verify eKYC OTP");
  }
  return res.json();
}

export async function matchEkycDemographics(
  payload: EkycMatchDemographicsRequest
): Promise<EkycMatchResult> {
  const res = await fetch(`${API_BASE}/api/v1/ekyc/match-demographics`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to perform demographic match");
  }
  return res.json();
}

// ── Scholarship Journey API ───────────────────────────────────────────────────

export async function startScholarshipApplication(
  citizenId: string,
  citizenName: string
): Promise<ScholarshipApplicationResponse> {
  const res = await fetch(`${API_BASE}/api/v1/public-service/scholarship/apply`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ citizen_account_id: citizenId, citizen_name: citizenName }),
  });
  if (!res.ok) throw new Error("Failed to start scholarship application");
  return res.json();
}

export async function getSharingReview(appId: string): Promise<SharingReviewResponse> {
  const res = await fetch(`${API_BASE}/api/v1/public-service/scholarship/${appId}/sharing-review`);
  if (!res.ok) throw new Error("Failed to fetch sharing review");
  return res.json();
}

export async function submitScholarshipConsent(
  appId: string,
  citizenId: string
): Promise<ConsentSubmitResponse> {
  const res = await fetch(`${API_BASE}/api/v1/public-service/scholarship/${appId}/consent-and-submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ citizen_account_id: citizenId, consent_granted: true }),
  });
  if (!res.ok) throw new Error("Failed to submit scholarship consent");
  return res.json();
}

// ── Verification Lab API ──────────────────────────────────────────────────────

export async function getVerificationLabResults(): Promise<{ tests: LabTestResult[] }> {
  const res = await fetch(`${API_BASE}/api/v1/public-service/verification-lab`);
  if (!res.ok) throw new Error("Failed to fetch verification lab results");
  return res.json();
}

export async function resetDemoEnvironment(): Promise<{
  status: string;
  message: string;
  citizen_account_id: string;
  application_id: string;
  proof_id: string;
  credentials_count: number;
}> {
  const res = await fetch(`${API_BASE}/api/v1/public-service/demo/reset`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to reset demo environment");
  return res.json();
}

// ── Federated Issuer & Dynamic Revocation API ──────────────────────────────────

export async function fetchFederatedIssuers(): Promise<{
  status: string;
  total_issuers: number;
  issuers: FederatedIssuer[];
  trust_framework: string;
}> {
  const res = await fetch(`${API_BASE}/api/v1/federation/issuers`);
  if (!res.ok) throw new Error("Failed to fetch federated issuers");
  return res.json();
}

export async function fetchFederatedCredentials(
  accountId?: string,
  issuerId?: string
): Promise<{
  status: string;
  total: number;
  credentials: FederatedCredential[];
}> {
  const params = new URLSearchParams();
  if (accountId) params.set("account_id", accountId);
  if (issuerId) params.set("issuer_id", issuerId);
  const query = params.toString() ? `?${params.toString()}` : "";
  const res = await fetch(`${API_BASE}/api/v1/federation/credentials${query}`);
  if (!res.ok) throw new Error("Failed to fetch credentials");
  return res.json();
}

export async function issueFederatedCredential(payload: {
  issuer_id: string;
  citizen_account_id: string;
  credential_type: string;
  title: string;
  claims: Record<string, unknown>;
  validity_days?: number;
}): Promise<{
  status: string;
  message: string;
  credential: {
    credential_id: string;
    account_id: string;
    issuer_id: string;
    issuer_name: string;
    credential_type: string;
    title: string;
    issued_at: string;
    expires_at: string;
    claim_digest: string;
    digital_signature: string;
    public_key_id: string;
    status: string;
    claims: Record<string, unknown>;
  };
}> {
  const res = await fetch(`${API_BASE}/api/v1/federation/issue-credential`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to issue federated credential");
  return res.json();
}

export async function revokeFederatedCredential(payload: {
  credential_id: string;
  issuer_id: string;
  reason: string;
  reason_description?: string;
  operator_id?: string;
}): Promise<{
  status: string;
  message: string;
  revocation_record: RevocationRecord;
}> {
  const res = await fetch(`${API_BASE}/api/v1/federation/revoke-credential`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to revoke credential");
  return res.json();
}

export async function fetchRevocationRegistry(): Promise<RevocationRegistryResponse> {
  const res = await fetch(`${API_BASE}/api/v1/federation/revocation-registry`);
  if (!res.ok) throw new Error("Failed to fetch revocation registry");
  return res.json();
}

export async function checkCredentialRevocationStatus(
  credentialId: string
): Promise<{
  status: string;
  is_valid: boolean;
  credential_id: string;
  revocation_details: RevocationRecord | null;
}> {
  const res = await fetch(`${API_BASE}/api/v1/federation/status/${credentialId}`);
  if (!res.ok) throw new Error("Failed to check revocation status");
  return res.json();
}





