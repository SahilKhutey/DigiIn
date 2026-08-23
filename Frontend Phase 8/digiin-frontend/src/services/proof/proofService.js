import { proofMock } from './proofMock.js';

export const proofService = {
  async getProof(proofId) {
    return proofMock.getProof(proofId);
  },

  async validateProof(proofId) {
    return proofMock.validateProof(proofId);
  }
};
