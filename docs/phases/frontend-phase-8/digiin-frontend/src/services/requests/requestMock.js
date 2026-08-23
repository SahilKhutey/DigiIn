const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const inMemoryRequests = [
  {
    id: 'VR-82A91',
    citizenId: 'DIN-7K4P-92M8',
    citizenName: 'Rahul Sharma',
    purpose: 'Admission verification',
    documents: [
      { id: 'doc-10', title: 'Class 10 Certificate', required: true, reason: 'Confirm educational qualification' },
      { id: 'doc-12', title: 'Class 12 Certificate', required: true, reason: 'Confirm eligibility cutoff' }
    ],
    validityHours: 24,
    status: 'COMPLETED',
    createdAt: '23 Aug 2026',
    completedAt: '23 Aug 2026',
    expiresAt: '24 Aug 2026',
    consent: {
      granted: true,
      grantedAt: '23 Aug 2026 10:32',
      scope: '2 requested documents'
    },
    verificationResult: {
      status: 'VERIFIED',
      verifiedCount: 2,
      totalCount: 2,
      verificationId: 'DIN-VRF-82A91-K7',
      proofId: 'DIN-PRF-51Q8-X2'
    }
  },
  {
    id: 'VR-83B12',
    citizenId: 'DIN-19A4-88Z2',
    citizenName: 'Priya Verma',
    purpose: 'Scholarship verification',
    documents: [
      { id: 'doc-12', title: 'Class 12 Certificate', required: true, reason: 'Merit eligibility' },
      { id: 'doc-inc', title: 'Income Certificate', required: true, reason: 'Means criteria' }
    ],
    validityHours: 24,
    status: 'AWAITING_CONSENT',
    createdAt: '23 Aug 2026',
    completedAt: null,
    expiresAt: '24 Aug 2026',
    consent: {
      granted: false,
      grantedAt: null,
      scope: 'Pending citizen action'
    },
    verificationResult: null
  },
  {
    id: 'VR-84C22',
    citizenId: 'DIN-91K2-33M4',
    citizenName: 'Amit Patel',
    purpose: 'Employment verification',
    documents: [
      { id: 'doc-deg', title: 'Degree Certificate', required: true, reason: 'Educational verification' }
    ],
    validityHours: 24,
    status: 'EXPIRED',
    createdAt: '18 Aug 2026',
    completedAt: null,
    expiresAt: '19 Aug 2026',
    consent: {
      granted: false,
      grantedAt: null,
      scope: 'Expired'
    },
    verificationResult: null
  }
];

const auditEvents = [
  { timestamp: '23 Aug 2026 10:34', requestId: 'VR-82A91', event: 'Verification completed • Proof DIN-PRF-51Q8-X2 generated' },
  { timestamp: '23 Aug 2026 10:32', requestId: 'VR-82A91', event: 'Citizen consent received' },
  { timestamp: '23 Aug 2026 10:30', requestId: 'VR-82A91', event: 'Verification request created' },
  { timestamp: '23 Aug 2026 09:15', requestId: 'VR-83B12', event: 'Verification request created' }
];

export const requestMock = {
  async listRequests(filter = 'ALL') {
    await delay(200);
    if (filter === 'PENDING') {
      return inMemoryRequests.filter(r => r.status === 'AWAITING_CONSENT' || r.status === 'SENT' || r.status === 'DOCUMENT_RETRIEVING');
    }
    if (filter === 'VERIFIED') {
      return inMemoryRequests.filter(r => r.status === 'COMPLETED');
    }
    if (filter === 'EXPIRED') {
      return inMemoryRequests.filter(r => r.status === 'EXPIRED');
    }
    if (filter === 'CANCELLED') {
      return inMemoryRequests.filter(r => r.status === 'CANCELLED');
    }
    return inMemoryRequests;
  },

  async getRequest(requestId) {
    await delay(180);
    return inMemoryRequests.find(r => r.id === requestId) || null;
  },

  async createRequest(data) {
    await delay(300);
    const newId = `VR-${Math.floor(10 + Math.random() * 89)}${String.fromCharCode(65 + Math.floor(Math.random() * 26))}${Math.floor(10 + Math.random() * 89)}`;
    const newReq = {
      id: newId,
      citizenId: data.citizenId || 'DIN-7K4P-92M8',
      citizenName: 'Citizen (' + (data.citizenId || 'DIN-7K4P-92M8') + ')',
      purpose: data.purpose || 'Admission verification',
      documents: data.documents || [
        { id: 'doc-10', title: 'Class 10 Certificate', required: true, reason: 'Confirm qualification' },
        { id: 'doc-12', title: 'Class 12 Certificate', required: true, reason: 'Confirm qualification' }
      ],
      validityHours: data.validityHours || 24,
      status: 'AWAITING_CONSENT',
      createdAt: '23 Aug 2026',
      completedAt: null,
      expiresAt: '24 Aug 2026',
      consent: {
        granted: false,
        grantedAt: null,
        scope: 'Waiting for citizen'
      },
      verificationResult: null
    };

    inMemoryRequests.unshift(newReq);
    auditEvents.unshift({
      timestamp: '23 Aug 2026 10:45',
      requestId: newId,
      event: 'Verification request created'
    });

    return newReq;
  },

  async cancelRequest(requestId) {
    await delay(250);
    const req = inMemoryRequests.find(r => r.id === requestId);
    if (req && (req.status === 'AWAITING_CONSENT' || req.status === 'CREATED')) {
      req.status = 'CANCELLED';
      auditEvents.unshift({
        timestamp: '23 Aug 2026 10:46',
        requestId,
        event: 'Verification request cancelled by organisation'
      });
      return { success: true, request: req };
    }
    return { success: false, message: 'Request could not be cancelled' };
  },

  getAuditEvents() {
    return auditEvents;
  }
};
