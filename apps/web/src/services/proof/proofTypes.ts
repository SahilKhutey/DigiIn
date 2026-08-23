export interface VerifiableProof {
  proofId: string;
  token: string;
  algorithm: "EdDSA";
  keyId: string;
  issuer: string;
  audience: string;
  purpose: string;
  issuedAt: string;
  expiresAt: string;
  status: "VERIFIED" | "REVOKED" | "EXPIRED";
  verificationLevel: 4;
  disclosedClaims: {
    candidateName: string;
    candidateDob: string;
    classXStatus: string;
    classXiiStatus: string;
    predicateAggregateGte60: boolean;
    zeroKnowledgeMode: boolean;
    rawDocumentsStored: false;
  };
  shareUrl: string;
}

export interface ProofValidationResult {
  isValid: boolean;
  status: "TRUSTED_PROOF_VERIFIED_OFFLINE" | "SIGNATURE_INVALID" | "PROOF_EXPIRED" | "AUDIENCE_MISMATCH";
  proof: VerifiableProof;
  verifiedAt: string;
}
