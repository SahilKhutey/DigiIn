import { verificationMock } from './verificationMock.js';

export const verificationService = {
  async runVerification(documents, scenario, onProgress) {
    return verificationMock.runPipeline(documents, scenario, onProgress);
  }
};
