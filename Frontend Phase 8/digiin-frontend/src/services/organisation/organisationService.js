import { organisationMock } from './organisationMock.js';

export const organisationService = {
  async signIn(orgId, email, password) {
    return organisationMock.signIn(orgId, email, password);
  },

  async signOut() {
    return organisationMock.signOut();
  },

  async getOrganisation() {
    return organisationMock.getOrganisation();
  },

  async getRequestStats() {
    return organisationMock.getRequestStats();
  },

  isAuthenticated() {
    return organisationMock.isAuthenticated();
  }
};
