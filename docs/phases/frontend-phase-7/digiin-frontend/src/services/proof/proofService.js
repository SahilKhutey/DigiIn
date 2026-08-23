import { proofMock } from './proofMock.js';

export const proofService = {
  async createProof(verificationId) {
    return proofMock.createProof(verificationId);
  },

  async getProof(proofId) {
    return proofMock.getProof(proofId);
  },

  async getProofHistory() {
    return proofMock.getProofHistory();
  },

  getShareUrl(proofId) {
    return proofMock.getShareUrl(proofId);
  },

  async revokeProof(proofId) {
    return proofMock.revokeProof(proofId);
  },

  async validateProof(proofId) {
    return proofMock.validateProof(proofId);
  },

  getAuditEvents() {
    return proofMock.getAuditEvents();
  },

  getQrSvg(proofId) {
    return proofMock.getQrSvg(proofId);
  }
};
