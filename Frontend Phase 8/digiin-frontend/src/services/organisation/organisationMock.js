const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const currentOrg = {
  id: 'ORG-84K2-19Q7',
  name: 'ABC University',
  type: 'Educational institution',
  verified: true,
  email: 'verifier@abcuniversity.example',
  status: 'Active',
  users: 5,
  createdAt: '2026-01-15',
  stats: {
    totalRequests: 18,
    verified: 11,
    pending: 4,
    expired: 3
  }
};

let isAuthenticated = true; // demo mode default

export const organisationMock = {
  async signIn(orgId, email, password) {
    await delay(350);
    isAuthenticated = true;
    return { success: true, organisation: currentOrg };
  },

  async signOut() {
    await delay(150);
    isAuthenticated = false;
    return { success: true };
  },

  async getOrganisation() {
    await delay(150);
    return currentOrg;
  },

  async getRequestStats() {
    await delay(150);
    return currentOrg.stats;
  },

  isAuthenticated() {
    return isAuthenticated;
  }
};
