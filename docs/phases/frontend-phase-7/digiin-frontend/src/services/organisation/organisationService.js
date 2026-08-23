import { proofService } from '../proof/proofService.js';

export const organisationService = {
  async verifyProof(proofId) {
    return proofService.validateProof(proofId);
  }
};
