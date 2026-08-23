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
  },
  'DIN-PRF-73K1-P9': {
    proofId: 'DIN-PRF-73K1-P9',
    verificationId: 'DIN-VRF-9941A-X1',
    status: 'EXPIRED',
    organisation: 'XYZ Institute',
    purpose: 'Course admission',
    verifiedDocuments: ['Class 12 Certificate'],
    issuedAt: '15 Aug 2026',
    expiresAt: '16 Aug 2026',
    revokedAt: null,
    version: 1
  },
  'DIN-PRF-REV-88': {
    proofId: 'DIN-PRF-REV-88',
    verificationId: 'DIN-VRF-7712A-B9',
    status: 'REVOKED',
    organisation: 'TechCorp India',
    purpose: 'Internship background check',
    verifiedDocuments: ['Degree Certificate'],
    issuedAt: '20 Aug 2026',
    expiresAt: '21 Aug 2026',
    revokedAt: '20 Aug 2026',
    version: 1
  }
};

const auditEvents = [
  { type: 'PROOF_CREATED', label: 'Proof created', proofId: 'DIN-PRF-51Q8-X2', timestamp: '23 Aug 10:31' },
  { type: 'PROOF_SHARED', label: 'Proof shared', proofId: 'DIN-PRF-51Q8-X2', timestamp: '23 Aug 10:32' },
  { type: 'PROOF_VALIDATED', label: 'Proof validated', proofId: 'DIN-PRF-51Q8-X2', timestamp: '23 Aug 10:34' }
];

export const proofMock = {
  async createProof(verificationId = 'DIN-VRF-82A91-K7') {
    await delay(250);
    const existing = Object.values(inMemoryProofs).find(p => p.verificationId === verificationId && p.status === 'ACTIVE');
    if (existing) {
      return existing;
    }

    const proofId = 'DIN-PRF-51Q8-X2';
    const newProof = {
      proofId,
      verificationId,
      status: 'ACTIVE',
      organisation: 'ABC University',
      purpose: 'Admission verification',
      verifiedDocuments: ['Class 10 Certificate', 'Class 12 Certificate'],
      issuedAt: '23 Aug 2026',
      expiresAt: '24 Aug 2026',
      revokedAt: null,
      version: 1
    };
    inMemoryProofs[proofId] = newProof;
    auditEvents.unshift({
      type: 'PROOF_CREATED',
      label: 'Proof created',
      proofId,
      timestamp: '23 Aug 10:31'
    });
    return newProof;
  },

  async getProof(proofId) {
    await delay(200);
    return inMemoryProofs[proofId] || null;
  },

  async getProofHistory() {
    await delay(200);
    return Object.values(inMemoryProofs);
  },

  getShareUrl(proofId = 'DIN-PRF-51Q8-X2') {
    return `${window.location.origin}${window.location.pathname}#/verify-proof?id=${proofId}`;
  },

  async revokeProof(proofId) {
    await delay(300);
    const proof = inMemoryProofs[proofId];
    if (proof && proof.status === 'ACTIVE') {
      proof.status = 'REVOKED';
      proof.revokedAt = '23 Aug 2026';
      auditEvents.unshift({
        type: 'PROOF_REVOKED',
        label: 'Proof revoked',
        proofId,
        timestamp: '23 Aug 10:35'
      });
      return { success: true, proof };
    }
    return { success: false, message: 'Proof could not be revoked.' };
  },

  async validateProof(proofId) {
    await delay(350);
    if (proofId === 'SERVICE_UNAVAILABLE') {
      return {
        status: 'SERVICE_UNAVAILABLE',
        message: "We couldn't reach DigiIn. No conclusion can be made about the verification at this time."
      };
    }

    const proof = inMemoryProofs[proofId];
    if (!proof) {
      return {
        status: 'INVALID',
        message: 'Verification could not be confirmed. This proof is not recognised by DigiIn.'
      };
    }

    if (proof.status === 'EXPIRED') {
      return {
        status: 'EXPIRED',
        proof,
        message: `This proof was valid until ${proof.expiresAt}. A new verification may be required.`
      };
    }

    if (proof.status === 'REVOKED') {
      return {
        status: 'REVOKED',
        proof,
        message: 'This proof was previously valid but is no longer active.'
      };
    }

    auditEvents.unshift({
      type: 'PROOF_VALIDATED',
      label: 'Proof validated',
      proofId,
      timestamp: '23 Aug 10:34'
    });

    return {
      status: 'VALID',
      proof,
      message: 'DigiIn has confirmed this verification proof.'
    };
  },

  getAuditEvents() {
    return auditEvents;
  },

  getQrSvg(proofId = 'DIN-PRF-51Q8-X2') {
    return `
      <svg width="180" height="180" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="DigiIn Verification QR Code">
        <rect width="100" height="100" fill="#FFFFFF"/>
        <!-- Finder Patterns -->
        <rect x="5" y="5" width="26" height="26" fill="#092F4F"/>
        <rect x="8" y="8" width="20" height="20" fill="#FFFFFF"/>
        <rect x="11" y="11" width="14" height="14" fill="#0B5D9B"/>
        
        <rect x="69" y="5" width="26" height="26" fill="#092F4F"/>
        <rect x="72" y="8" width="20" height="20" fill="#FFFFFF"/>
        <rect x="75" y="11" width="14" height="14" fill="#0B5D9B"/>
        
        <rect x="5" y="69" width="26" height="26" fill="#092F4F"/>
        <rect x="8" y="72" width="20" height="20" fill="#FFFFFF"/>
        <rect x="11" y="75" width="14" height="14" fill="#0B5D9B"/>
        
        <!-- Synthetic QR Data Modules -->
        <rect x="36" y="8" width="5" height="5" fill="#092F4F"/>
        <rect x="44" y="8" width="5" height="5" fill="#092F4F"/>
        <rect x="52" y="8" width="5" height="5" fill="#092F4F"/>
        <rect x="36" y="16" width="5" height="5" fill="#0B5D9B"/>
        <rect x="44" y="24" width="5" height="5" fill="#092F4F"/>
        <rect x="52" y="16" width="5" height="5" fill="#092F4F"/>
        
        <rect x="8" y="36" width="5" height="5" fill="#092F4F"/>
        <rect x="16" y="44" width="5" height="5" fill="#0B5D9B"/>
        <rect x="24" y="36" width="5" height="5" fill="#092F4F"/>
        <rect x="8" y="52" width="5" height="5" fill="#092F4F"/>
        
        <circle cx="50" cy="50" r="10" fill="#092F4F"/>
        <text x="50" y="54" font-size="11" font-weight="bold" fill="#FFFFFF" text-anchor="middle">DI</text>
        
        <rect x="68" y="36" width="5" height="5" fill="#092F4F"/>
        <rect x="76" y="44" width="5" height="5" fill="#092F4F"/>
        <rect x="84" y="36" width="5" height="5" fill="#0B5D9B"/>
        
        <rect x="36" y="68" width="5" height="5" fill="#092F4F"/>
        <rect x="44" y="76" width="5" height="5" fill="#092F4F"/>
        <rect x="52" y="68" width="5" height="5" fill="#092F4F"/>
        <rect x="68" y="68" width="5" height="5" fill="#092F4F"/>
        <rect x="76" y="76" width="5" height="5" fill="#0B5D9B"/>
        <rect x="84" y="84" width="5" height="5" fill="#092F4F"/>
      </svg>
    `;
  }
};
