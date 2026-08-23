const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const demoDocuments = [
  { id: 'doc-10', title: 'Class 10 Certificate', issuer: 'CBSE', purpose: 'Date of birth and eligibility', status: 'verified', required: true },
  { id: 'doc-12', title: 'Class 12 Certificate', issuer: 'CBSE', purpose: 'Eligibility verification (>= 60%)', status: 'verified', required: true }
];

export const digiLockerService = {
  connectionState: 'NOT_CONNECTED',

  async connect() {
    this.connectionState = 'CONNECTING';
    await delay(700);
    this.connectionState = 'CONNECTED';
    return { connected: true, provider: 'DigiLocker' };
  },

  async authenticate() {
    this.connectionState = 'AUTHENTICATING';
    await delay(800);
    this.connectionState = 'AUTHENTICATED';
    return { authenticated: true, provider: 'DigiLocker', sessionToken: 'mock_dl_session' };
  },

  async getConsentRequest(requestId) {
    await delay(300);
    return {
      requestId: requestId || 'VR-82A91',
      organisation: 'ABC University',
      purpose: 'Admission verification',
      documents: demoDocuments,
      expiresInHours: 24,
      createdAt: new Date().toISOString()
    };
  },

  async authorizeConsent(requestId, options = {}) {
    await delay(400);
    return {
      success: true,
      consentId: `CNS-${Date.now().toString(36).toUpperCase()}`,
      validUntil: new Date(Date.now() + (options.durationHours || 24) * 3600 * 1000).toISOString(),
      zkpMode: options.zkpMode ?? true
    };
  },

  async getDocuments(scenario = 'success') {
    await delay(1100);
    if (scenario === 'partial') {
      return [demoDocuments[1]]; // Only class 12
    }
    if (scenario === 'failure') {
      throw new Error('DigiLocker source registry currently unavailable. Please retry.');
    }
    return demoDocuments;
  },

  async disconnect() {
    await delay(150);
    this.connectionState = 'NOT_CONNECTED';
    return { connected: false };
  }
};

export const mockDigiLocker = digiLockerService;
