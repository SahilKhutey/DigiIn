const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const demoDocuments = [
  { id: 'doc-10', title: 'Class 10 Certificate', issuer: 'CBSE', purpose: 'Eligibility verification' },
  { id: 'doc-12', title: 'Class 12 Certificate', issuer: 'CBSE', purpose: 'Eligibility verification' }
];

export const digiLockerService = {
  async connect() {
    await delay(900);
    return { connected: true, provider: 'DigiLocker' };
  },
  async authenticate() {
    await delay(900);
    return { authenticated: true, provider: 'DigiLocker' };
  },
  async getConsentRequest(requestId) {
    await delay(300);
    return { requestId, status: 'required', expiresInHours: 24 };
  },
  async getDocuments() {
    await delay(1200);
    return demoDocuments;
  },
  async disconnect() {
    await delay(150);
    return { connected: false };
  }
};

export const mockDigiLocker = digiLockerService;
