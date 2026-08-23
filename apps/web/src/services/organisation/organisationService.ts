import { proofService } from "../proof/proofService";
import { OrganisationVerificationResponse } from "./organisationTypes";

export const organisationService = {
  async verifyProof(proofId: string): Promise<OrganisationVerificationResponse> {
    return proofService.validateProof(proofId);
  },
};
