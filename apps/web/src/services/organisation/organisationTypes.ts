import { ProofValidationResult } from "../proof/proofTypes";

export interface OrganisationVerificationRequest {
  proofId: string;
}

export type OrganisationVerificationResponse = ProofValidationResult;
