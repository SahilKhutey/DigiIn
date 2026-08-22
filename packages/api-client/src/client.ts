import type {
  CorrectionRequestCreate,
  CorrectionRequestRecord,
  DirectUploadPayload,
  DomainEvent,
  EkycMatchDemographicsRequest,
  EkycOtpRequest,
  EkycOtpResponse,
  EkycVerifyRequest,
  EkycVerifyResponse,
  EvidenceComparisonDetail,
  GovernmentDecisionPayload,
  JwksResponse,
  PipelineUploadResponse,
  PlatformSnapshot,
  ProofTokenIntrospection,
  RevokeConsentPayload,
  StudentDemoResult,
  SupportSafeSummary,
  VerificationAuthorization,
  VerificationCase,
  VerificationRequestCreate,
  VerificationRequestRecord,
  VerificationResult,
  VerifierQueueSummary,
  WalletDocument,
} from "../../types/src/index";

export interface ApiClientConfig {
  baseUrl?: string;
  getAuthToken?: () => string | null | Promise<string | null>;
}

export class DigiLockerXApiClient {
  private baseUrl: string;
  private getAuthToken?: () => string | null | Promise<string | null>;

  constructor(config: ApiClientConfig = {}) {
    this.baseUrl = config.baseUrl || "http://localhost:8000";
    this.getAuthToken = config.getAuthToken;
  }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (this.getAuthToken) {
      const token = await this.getAuthToken();
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorMessage = `API Error: ${response.status} ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = typeof errorData.detail === "string" ? errorData.detail : JSON.stringify(errorData.detail);
        }
      } catch {
        // Fallback to status text
      }
      throw new Error(errorMessage);
    }

    return response.json();
  }

  // Health
  async getHealth(): Promise<{ status: string; database?: string }> {
    return this.request("/health");
  }

  // Wallet
  async getWalletDocuments(): Promise<WalletDocument[]> {
    return this.request("/api/v1/wallet/documents");
  }

  // Upload Pipeline
  async uploadDocumentPipeline(payload: DirectUploadPayload): Promise<PipelineUploadResponse> {
    return this.request("/api/v1/documents/upload-pipeline", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  // Verification
  async createVerificationRequest(payload: VerificationRequestCreate): Promise<VerificationRequestRecord> {
    return this.request("/api/v1/verification/request", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async getVerificationRequest(requestId: string): Promise<VerificationRequestRecord> {
    return this.request(`/api/v1/verification/request/${encodeURIComponent(requestId)}`);
  }

  async authorizeVerificationRequest(
    requestId: string,
    authorization: VerificationAuthorization
  ): Promise<VerificationResult> {
    return this.request(`/api/v1/verification/request/${encodeURIComponent(requestId)}/authorize`, {
      method: "POST",
      body: JSON.stringify(authorization),
    });
  }

  async getVerificationResult(requestId: string): Promise<VerificationResult> {
    return this.request(`/api/v1/verification/result/${encodeURIComponent(requestId)}`);
  }

  async introspectProofToken(token: string, expectedAudience?: string): Promise<ProofTokenIntrospection> {
    return this.request("/api/v1/verification/introspect", {
      method: "POST",
      body: JSON.stringify({ token, expectedAudience }),
    });
  }

  async getPublicJwks(): Promise<JwksResponse> {
    return this.request("/.well-known/jwks.json");
  }

  // Verifier & Officer Console
  async listVerifierQueues(): Promise<VerifierQueueSummary[]> {
    return this.request("/api/v1/verifier/queues");
  }

  async listVerifierCases(queueId?: string): Promise<VerificationCase[]> {
    const query = queueId ? `?queue=${encodeURIComponent(queueId)}` : "";
    return this.request(`/api/v1/verifier/cases${query}`);
  }

  async getEvidenceComparison(caseId: string): Promise<EvidenceComparisonDetail> {
    return this.request(`/api/v1/verifier/cases/${encodeURIComponent(caseId)}/comparison`);
  }

  async decideVerifierCase(caseId: string, payload: GovernmentDecisionPayload): Promise<VerificationCase> {
    return this.request(`/api/v1/verifier/cases/${encodeURIComponent(caseId)}/decision`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  // Corrections
  async createCorrectionRequest(payload: CorrectionRequestCreate): Promise<CorrectionRequestRecord> {
    return this.request(`/api/v1/documents/${encodeURIComponent(payload.documentId)}/corrections`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async listCorrections(): Promise<CorrectionRequestRecord[]> {
    return this.request("/api/v1/corrections");
  }

  // Consent & Revocation
  async revokeConsent(consentId: string, payload: RevokeConsentPayload): Promise<{ status: string }> {
    return this.request(`/api/v1/consent/${encodeURIComponent(consentId)}/revoke`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  // eKYC Gateway
  async generateEkycOtp(payload: EkycOtpRequest): Promise<EkycOtpResponse> {
    return this.request("/api/v1/ekyc/generate-otp", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async verifyEkycOtp(payload: EkycVerifyRequest): Promise<EkycVerifyResponse> {
    return this.request("/api/v1/ekyc/verify-otp", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  // Platform & Audit
  async getPlatformSnapshot(): Promise<PlatformSnapshot> {
    return this.request("/api/v1/platform/snapshot");
  }

  async runStudentDemo(): Promise<StudentDemoResult> {
    return this.request("/api/v1/platform/demo/student", { method: "POST" });
  }

  async listAuditEvents(): Promise<DomainEvent[]> {
    return this.request("/api/v1/audit/events");
  }
}

export const defaultApiClient = new DigiLockerXApiClient();
