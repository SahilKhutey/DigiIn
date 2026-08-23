import { requestMock } from './requestMock.js';

export const requestService = {
  async listRequests(filter) {
    return requestMock.listRequests(filter);
  },

  async getRequest(requestId) {
    return requestMock.getRequest(requestId);
  },

  async createRequest(data) {
    return requestMock.createRequest(data);
  },

  async cancelRequest(requestId) {
    return requestMock.cancelRequest(requestId);
  },

  getAuditEvents() {
    return requestMock.getAuditEvents();
  }
};
