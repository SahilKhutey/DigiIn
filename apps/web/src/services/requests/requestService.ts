import { VerificationRequestItem } from "./requestTypes";

const DEMO_REQUESTS: VerificationRequestItem[] = [
  {
    id: "VR-82A91",
    citizenId: "DIN-7K4P-92M8",
    citizenName: "Rahul Sharma",
    purpose: "Admission verification",
    documents: [
      { id: "doc-10", title: "Class 10 Certificate", required: true, reason: "Confirm educational qualification" },
      { id: "doc-12", title: "Class 12 Certificate", required: true, reason: "Confirm eligibility cutoff" }
    ],
    validityHours: 24,
    status: "COMPLETED",
    createdAt: "23 Aug 2026",
    completedAt: "23 Aug 2026",
    expiresAt: "24 Aug 2026",
    consent: {
      granted: true,
      grantedAt: "23 Aug 2026 10:32",
      scope: "2 requested documents"
    },
    verificationResult: {
      status: "VERIFIED",
      verifiedCount: 2,
      totalCount: 2,
      verificationId: "DIN-VRF-82A91-K7",
      proofId: "DIN-PRF-51Q8-X2"
    }
  },
  {
    id: "VR-83B12",
    citizenId: "DIN-19A4-88Z2",
    citizenName: "Priya Verma",
    purpose: "Scholarship verification",
    documents: [
      { id: "doc-12", title: "Class 12 Certificate", required: true, reason: "Merit eligibility" },
      { id: "doc-inc", title: "Income Certificate", required: true, reason: "Means criteria" }
    ],
    validityHours: 24,
    status: "AWAITING_CONSENT",
    createdAt: "23 Aug 2026",
    completedAt: null,
    expiresAt: "24 Aug 2026",
    consent: {
      granted: false,
      grantedAt: null,
      scope: "Pending citizen action"
    },
    verificationResult: null
  }
];

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const requestService = {
  async listRequests(filter: string = "ALL"): Promise<VerificationRequestItem[]> {
    await delay(150);
    if (filter === "PENDING") {
      return DEMO_REQUESTS.filter((r) => r.status === "AWAITING_CONSENT" || r.status === "SENT");
    }
    if (filter === "VERIFIED") {
      return DEMO_REQUESTS.filter((r) => r.status === "COMPLETED");
    }
    if (filter === "EXPIRED") {
      return DEMO_REQUESTS.filter((r) => r.status === "EXPIRED");
    }
    return DEMO_REQUESTS;
  },

  async getRequest(requestId: string): Promise<VerificationRequestItem | null> {
    await delay(150);
    return DEMO_REQUESTS.find((r) => r.id === requestId) || null;
  },

  async createRequest(data: Partial<VerificationRequestItem>): Promise<VerificationRequestItem> {
    await delay(250);
    const newReq: VerificationRequestItem = {
      id: `VR-${Math.floor(10 + Math.random() * 89)}A91`,
      citizenId: data.citizenId || "DIN-7K4P-92M8",
      citizenName: "Citizen (" + (data.citizenId || "DIN-7K4P-92M8") + ")",
      purpose: data.purpose || "Admission verification",
      documents: data.documents || [],
      validityHours: data.validityHours || 24,
      status: "AWAITING_CONSENT",
      createdAt: new Date().toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }),
      expiresAt: new Date(Date.now() + 24 * 3600 * 1000).toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }),
      consent: {
        granted: false,
        scope: "Waiting for citizen"
      }
    };
    DEMO_REQUESTS.unshift(newReq);
    return newReq;
  }
};
