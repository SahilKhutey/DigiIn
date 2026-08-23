const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const inMemoryProofs = {
  'DIN-PRF-51Q8-X2': {
    proofId: 'DIN-PRF-51Q8-X2',
    verificationId: 'DIN-VRF-82A91-K7',
    status: 'ACTIVE',
    organisation: 'ABC University',
    purpose: 'Admission verification',
    verifiedDocuments: ['Class 10 Certificate', 'Class 12 Certificate'],
    issuedAt: '23 Aug 2026',
    expiresAt: '24 Aug 2026',
    revokedAt: null,
    version: 1
  }
};

export const proofMock = {
  async getProof(proofId) {
    await delay(200);
    return inMemoryProofs[proofId] || null;
  },

  async validateProof(proofId) {
    await delay(300);
    const proof = inMemoryProofs[proofId];
    if (!proof) {
      return {
        status: 'INVALID',
        message: 'Verification could not be confirmed. This proof is not recognised by DigiIn.'
      };
    }
    return {
      status: 'VALID',
      proof,
      message: 'DigiIn has confirmed this verification proof.'
    };
  }
};
