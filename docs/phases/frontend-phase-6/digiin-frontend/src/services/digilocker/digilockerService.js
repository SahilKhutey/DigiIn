const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const demoDocuments = [
  { id: 'doc-10', title: 'Class 10 Certificate', issuer: 'CBSE', purpose: 'Date of birth and eligibility', status: 'verified', required: true },
  { id: 'doc-12', title: 'Class 12 Certificate', issuer: 'CBSE', purpose: 'Eligibility verification (>= 60%)', status: 'verified', required: true }
];

export const digiLockerService = {
  async connect() {
    await delay(500);
    return { connected: true, provider: 'DigiLocker' };
  },
  async getDocuments() {
    await delay(600);
    return demoDocuments;
  }
};
