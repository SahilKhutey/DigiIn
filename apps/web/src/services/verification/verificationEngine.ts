import {
  VerificationProgressEvent,
  VerificationResultPayload,
} from "./verificationTypes";
import { WalletDocument } from "../../types";

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const DEMO_PROOF_TOKEN =
  "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCIsImtpZCI6ImRpZ2lpbi1lZDI1NTE5LWtleS0yMDI2In0.eyJpc3MiOiJEaWdpTG9ja2VyIFggU292ZXJlaWduIFZlcmlmaWNhdGlvbiBHYXRld2F5Iiwic3ViIjoic3Vial9yYWh1bF9zaGFybWFfOTkiLCJhdWQiOiJERUxISV9VTklWRVJTSVRZX0FETUlTU0lPTiIsInB1cnBvc2UiOiJBRE1JU1NJT05fVkVSSUZJQ0FUSU9OIiwic3RhdHVzIjoiVkVSSUZJRUQiLCJ2ZXJpZmljYXRpb25fbGV2ZWwiOjQsInByZWRpY2F0ZXMiOlt7ImNsYWltIjoiQ0xBU1NfWElJIiwiZXhwcmVzc2lvbiI6InBlcmNlbnRhZ2UgPj0gNjAuMCIsInNhdGlzZmllZCI6dHJ1ZX1dLCJyYXdfZmlsZV90cmFuc2ZlcnJlZCI6ZmFsc2V9.I2Rsq4XWAj_PHuvIdDzr8A4uArG8YPVYKJTWLAYYFa-wsLmNCorUPNceBDEJ8f03H9QVvUF60Xok4pZTouJFCw";

export const verificationEngine = {
  async executePipeline(
    documents: WalletDocument[],
    options?: { zkpMode?: boolean; scenario?: "success" | "partial" | "mismatch" },
    onProgress?: (e: VerificationProgressEvent) => void
  ): Promise<VerificationResultPayload> {
    const scenario = options?.scenario || "success";

    onProgress?.({
      stage: "INITIALIZING",
      percent: 20,
      title: "1. Documents Received",
      message: "2 retrieved digital credentials loaded into secure verification memory.",
    });
    await delay(400);

    onProgress?.({
      stage: "INTEGRITY_CHECK",
      percent: 40,
      title: "2. Checking Document Integrity",
      message: "Validating SHA-256 integrity digests across 2 retrieved digital certificates…",
    });
    await delay(450);

    onProgress?.({
      stage: "ISSUER_MATCH",
      percent: 60,
      title: "3. Matching Issuing Authority Keys",
      message: "Resolving cryptographic public keys for Central Board of Secondary Education…",
    });
    await delay(450);

    if (scenario === "mismatch") {
      onProgress?.({
        stage: "FAILED",
        percent: 80,
        title: "4. Demographics Discrepancy Detected",
        message: "Candidate name on record differs from application entry.",
      });
      await delay(300);

      return {
        verificationId: "DIN-VRF-FAIL-901",
        status: "FAILED",
        outcomeMessage: "Candidate name on record differs from application entry.",
        requesterName: "ABC University",
        purpose: "Admission verification",
        issuedAt: new Date().toISOString(),
        expiresAt: new Date(Date.now() + 24 * 3600 * 1000).toISOString(),
        proofToken: "",
        keyId: "digiin-ed25519-key-2026",
        algorithm: "EdDSA",
        disclosedClaims: {},
        documents: documents.map((d) => ({
          documentId: d.documentId,
          title: d.title,
          issuer: d.issuer,
          level: d.verificationLevel,
          integrityValid: true,
          issuerSignatureValid: true,
          predicatesSatisfied: false,
          status: "failed",
          verifiedAt: "23 Aug 2026",
          checks: [
            { type: "integrity", label: "Document integrity", status: "passed", message: "Digital seal and structure are valid." },
            { type: "authority", label: "Issuing authority", status: "passed", message: "CBSE public key resolved." },
            { type: "candidate", label: "Candidate details", status: "failed", message: "Name on record differs from application." },
          ],
          claims: {},
        })),
      };
    }

    onProgress?.({
      stage: "DETAIL_CHECK",
      percent: 80,
      title: "4. Checking Document Details & Predicates",
      message: "Evaluating passing year (2025) and aggregate criteria (>= 60.0%)…",
    });
    await delay(450);

    onProgress?.({
      stage: "PROOF_MINTING",
      percent: 100,
      title: "5. Minting Signed Verifiable Proof Receipt",
      message: "Generating RFC 7515/7519 Ed25519 cryptographic token proof DIN-VRF-82A91-K7…",
    });
    await delay(350);

    const isPartial = scenario === "partial";
    return {
      verificationId: "DIN-VRF-82A91-K7",
      status: isPartial ? "PARTIALLY_VERIFIED" : "VERIFIED",
      outcomeMessage: isPartial
        ? "1 of 2 credentials verified at issuing authority."
        : "All 2 credentials cryptographically verified at issuing authority.",
      requesterName: "ABC University",
      purpose: "Undergraduate admission verification",
      issuedAt: new Date().toISOString(),
      expiresAt: new Date(Date.now() + 24 * 3600 * 1000).toISOString(),
      proofToken: DEMO_PROOF_TOKEN,
      keyId: "digiin-ed25519-key-2026",
      algorithm: "EdDSA",
      disclosedClaims: {
        candidate_name: "Rahul Sharma",
        class_x_status: isPartial ? "UNAVAILABLE" : "PASSED (2023)",
        class_xii_status: "PASSED (2025)",
        aggregate_predicate: "percentage >= 60.0% -> SATISFIED (TRUE)",
        zero_knowledge_mode: options?.zkpMode ?? true,
        raw_documents_stored: false,
      },
      documents: [
        {
          documentId: "doc-10",
          title: "Class 10 Certificate",
          issuer: "Central Board of Secondary Education",
          level: 4,
          integrityValid: true,
          issuerSignatureValid: true,
          predicatesSatisfied: !isPartial,
          status: isPartial ? "partial" : "verified",
          verifiedAt: "23 Aug 2026",
          checks: [
            { type: "integrity", label: "Document integrity", status: "passed", message: "Document structure and verification information are valid." },
            { type: "authority", label: "Issuing authority", status: isPartial ? "warning" : "passed", message: isPartial ? "Issuing authority could not be reached." : "CBSE public signing key confirmed." },
            { type: "cert_no", label: "Certificate number", status: isPartial ? "warning" : "passed", message: "CBSE-X-2023-9941 matched." },
            { type: "candidate", label: "Candidate details", status: "passed", message: "Name and date of birth match 100%." },
            { type: "year", label: "Issue year", status: "passed", message: "Year 2023 confirmed." },
          ],
          claims: { dob: "2007-06-15", rollNumber: "CBSE-X-2023-9941" },
        },
        {
          documentId: "doc-12",
          title: "Class 12 Certificate",
          issuer: "Central Board of Secondary Education",
          level: 4,
          integrityValid: true,
          issuerSignatureValid: true,
          predicatesSatisfied: true,
          predicateExpression: "percentage >= 60.0",
          status: "verified",
          verifiedAt: "23 Aug 2026",
          checks: [
            { type: "integrity", label: "Document integrity", status: "passed", message: "Document structure and verification information are valid." },
            { type: "authority", label: "Issuing authority", status: "passed", message: "CBSE public signing key confirmed." },
            { type: "cert_no", label: "Certificate number", status: "passed", message: "CBSE-XII-2025-8812 matched." },
            { type: "candidate", label: "Candidate details", status: "passed", message: "Name match 100%." },
            { type: "year", label: "Issue year", status: "passed", message: "Year 2025 confirmed." },
            { type: "predicate", label: "Eligibility predicate", status: "passed", message: "Aggregate percentage >= 60.0% satisfied (84.5%)." },
          ],
          claims: { passingYear: 2025, percentage: 84.5, stream: "Science" },
        },
      ],
    };
  },
};
