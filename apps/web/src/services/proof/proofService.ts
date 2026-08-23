import { VerifiableProof, ProofValidationResult } from "./proofTypes";

const DEMO_TOKEN =
  "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCIsImtpZCI6ImRpZ2lpbi1lZDI1NTE5LWtleS0yMDI2In0.eyJpc3MiOiJEaWdpTG9ja2VyIFggU292ZXJlaWduIFZlcmlmaWNhdGlvbiBHYXRld2F5Iiwic3ViIjoic3Vial9yYWh1bF9zaGFybWFfOTkiLCJhdWQiOiJERUxISV9VTklWRVJTSVRZX0FETUlTU0lPTiIsInB1cnBvc2UiOiJBRE1JU1NJT05fVkVSSUZJQ0FUSU9OIiwic3RhdHVzIjoiVkVSSUZJRUQiLCJ2ZXJpZmljYXRpb25fbGV2ZWwiOjQsInByZWRpY2F0ZXMiOlt7ImNsYWltIjoiQ0xBU1NfWElJIiwiZXhwcmVzc2lvbiI6InBlcmNlbnRhZ2UgPj0gNjAuMCIsInNhdGlzZmllZCI6dHJ1ZX1dLCJyYXdfZmlsZV90cmFuc2ZlcnJlZCI6ZmFsc2V9.I2Rsq4XWAj_PHuvIdDzr8A4uArG8YPVYKJTWLAYYFa-wsLmNCorUPNceBDEJ8f03H9QVvUF60Xok4pZTouJFCw";

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const proofService = {
  async getProof(proofId: string = "DIN-VRF-82A91-K7"): Promise<VerifiableProof> {
    await delay(200);
    return {
      proofId,
      token: DEMO_TOKEN,
      algorithm: "EdDSA",
      keyId: "digiin-ed25519-key-2026",
      issuer: "DigiLocker X Sovereign Gateway",
      audience: "ABC University (Undergraduate Admission AY 2026-27)",
      purpose: "Admission verification",
      issuedAt: new Date().toISOString(),
      expiresAt: new Date(Date.now() + 24 * 3600 * 1000).toISOString(),
      status: "VERIFIED",
      verificationLevel: 4,
      disclosedClaims: {
        candidateName: "Rahul Sharma",
        candidateDob: "2007-06-15",
        classXStatus: "PASSED (CBSE 2023)",
        classXiiStatus: "PASSED (CBSE 2025)",
        predicateAggregateGte60: true,
        zeroKnowledgeMode: true,
        rawDocumentsStored: false,
      },
      shareUrl: `https://digiin.gov.in/verify/proof/${proofId}`,
    };
  },

  async validateProof(proofIdOrToken: string): Promise<ProofValidationResult> {
    await delay(350);
    const proof = await this.getProof(proofIdOrToken);
    return {
      isValid: true,
      status: "TRUSTED_PROOF_VERIFIED_OFFLINE",
      proof,
      verifiedAt: new Date().toISOString(),
    };
  },
};
