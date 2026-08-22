import type {
  ConsentRecord,
  CorrectionRequestRecord,
  Diagnostic,
  DirectUploadPayload,
  DocumentOption,
  EvidenceComparisonDetail,
  GovernmentDecisionPayload,
  JwksResponse,
  PipelineUploadResponse,
  PlatformEvent,
  PlatformSnapshot,
  Scenario,
  SelectiveDisclosurePreference,
  StudentDemo,
  SupportSafeSummary,
  TokenCheck,
  VerificationCase,
  VerificationRequest,
  VerificationResult,
  VerifierQueueId,
  VerifierQueueSummary,
  WalletDocument,
} from "../types";



const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

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

