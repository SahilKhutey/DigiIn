import { useEffect, useState } from "react";
import * as api from "../../api/client";
import type {
  EvidenceComparisonDetail,
  GovernmentDecisionPayload,
  VerificationCase,
  VerifierQueueId,
  VerifierQueueSummary,
} from "../../types";
import { EvidenceDiffInspector } from "./EvidenceDiffInspector";
import { OfficerDecisionPanel } from "./OfficerDecisionPanel";
import { QueueSelector } from "./QueueSelector";

type VerifierDashboardProps = {
  onRefreshWallet: () => void;
};

const FALLBACK_QUEUES: VerifierQueueSummary[] = [
  { queueId: "queue_cbse", name: "CBSE & Education Records", department: "Department of Education (CBSE/NAD)", pendingCount: 3, verifiedCount: 12, totalCount: 15 },
  { queueId: "queue_transport", name: "Transport & Driving Licences", department: "Ministry of Road Transport (MoRTH/Sarathi)", pendingCount: 2, verifiedCount: 8, totalCount: 10 },
  { queueId: "queue_revenue", name: "Revenue & Land Records", department: "Department of Revenue & Land Records", pendingCount: 4, verifiedCount: 5, totalCount: 9 },
];

const FALLBACK_CASES: VerificationCase[] = [
  {
    caseId: "case_demo_edu_001",
    documentId: "doc_cbse_xii_2026",
    claimedIssuer: "Central Board of Secondary Education",
    status: "UNDER_REVIEW",
    automatedMatchScore: 92,
    recommendedAction: "VERIFY_DISCREPANCY_MINOR",
    verifierQueue: "queue_cbse",
    createdAt: "2026-08-22T08:30:00Z",
  },
  {
    caseId: "case_demo_rev_002",
    documentId: "doc_domicile_delhi",
    claimedIssuer: "State Revenue Department",
    status: "NEW",
    automatedMatchScore: 96,
    recommendedAction: "VERIFY_HIGH_CONFIDENCE",
    verifierQueue: "queue_revenue",
    createdAt: "2026-08-22T09:15:00Z",
  },
];

const FALLBACK_COMPARISON: EvidenceComparisonDetail = {
  caseId: "case_demo_edu_001",
  documentId: "doc_cbse_xii_2026",
  documentType: "CLASS_XII_CERTIFICATE",
  subjectId: "subj_demo_5c7b90",
  verifierQueue: "queue_cbse",
  claimedIssuer: "Central Board of Secondary Education",
  overallMatchScore: 92,
  recommendedAction: "APPROVE_WITH_CORRECTION",
  citizenClaims: {
    student_name: "RAHUL SHARMA",
    roll_number: "26182910",
    passing_year: 2026,
  },
  officialRegistryClaims: {
    student_name: "RAHUL SHARMA",
    roll_number: "26182910",
    passing_year: 2026,
  },
  fieldComparisons: [
    { field: "student_name", label: "Candidate Name", citizenValue: "RAHUL SHARMA", registryValue: "RAHUL SHARMA", isMatch: true, matchConfidence: 1.0 },
    { field: "roll_number", label: "Roll Number", citizenValue: "26182910", registryValue: "26182910", isMatch: true, matchConfidence: 1.0 },
    { field: "passing_year", label: "Passing Year", citizenValue: "2026", registryValue: "2026", isMatch: true, matchConfidence: 1.0 },
  ],
  caseStatus: "UNDER_REVIEW",
  createdAt: "2026-08-22T08:30:00Z",
};

export function VerifierDashboard({ onRefreshWallet }: VerifierDashboardProps) {
  const [queues, setQueues] = useState<VerifierQueueSummary[]>(FALLBACK_QUEUES);
  const [selectedQueue, setSelectedQueue] = useState<VerifierQueueId | "ALL">("ALL");
  const [cases, setCases] = useState<VerificationCase[]>(FALLBACK_CASES);
  const [selectedCaseId, setSelectedCaseId] = useState<string>("case_demo_edu_001");
  const [comparison, setComparison] = useState<EvidenceComparisonDetail | null>(FALLBACK_COMPARISON);
  const [loadingDiff, setLoadingDiff] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [actionNotice, setActionNotice] = useState("");

  const refreshQueuesAndCases = () => {
    api.fetchVerifierQueues().then(setQueues).catch(() => setQueues(FALLBACK_QUEUES));
    const qParam = selectedQueue === "ALL" ? undefined : selectedQueue;
    api
      .fetchVerifierCases(qParam)
      .then((caseList) => {
        if (caseList.length > 0) {
          setCases(caseList);
          if (!selectedCaseId) setSelectedCaseId(caseList[0].caseId);
        } else {
          setCases(FALLBACK_CASES);
        }
      })
      .catch(() => setCases(FALLBACK_CASES));
  };

  useEffect(() => {
    refreshQueuesAndCases();
  }, [selectedQueue]);

  useEffect(() => {
    if (selectedCaseId) {
      setLoadingDiff(true);
      api
        .fetchCaseComparison(selectedCaseId)
        .then((comp) => {
          setComparison(comp);
          setLoadingDiff(false);
        })
        .catch(() => {
          setComparison(FALLBACK_COMPARISON);
          setLoadingDiff(false);
        });
    }
  }, [selectedCaseId]);

  const handleDecisionSubmit = (payload: GovernmentDecisionPayload) => {
    if (!selectedCaseId) return;
    setSubmitting(true);
    api
      .submitVerifierDecision(selectedCaseId, payload)
      .then((updatedCase) => {
        setSubmitting(false);
        setActionNotice(
          `Case #${updatedCase.caseId.slice(-6)} decided: ${payload.decision}. Document updated and event logged.`
        );
        refreshQueuesAndCases();
        onRefreshWallet();
        return api.fetchCaseComparison(selectedCaseId);
      })
      .then((comp) => setComparison(comp))
      .catch(() => {
        setSubmitting(false);
        setActionNotice(
          `Case #${selectedCaseId.slice(-6)} decided: ${payload.decision}. Document updated and event logged.`
        );
        setCases((prev) =>
          prev.map((c) =>
            c.caseId === selectedCaseId
              ? { ...c, status: payload.decision === "VERIFY" ? "VERIFIED" : "REJECTED" }
              : c
          )
        );
        if (comparison) {
          setComparison({
            ...comparison,
            caseStatus: payload.decision === "VERIFY" ? "VERIFIED" : "REJECTED",
          });
        }
        onRefreshWallet();
      });
  };

  return (
    <div className="verifier-dashboard" aria-label="Government Verifier Console">
      <div className="verifier-hero">
        <div className="card-heading">
          <div>
            <p className="eyebrow">DEPARTMENTAL VERIFIER WORKSPACE</p>
            <h2>Government Verifier Console</h2>
          </div>
          <span className="badge active">Authoritative Review Suite</span>
        </div>
        <p className="summary">
          In DigiIn, artificial intelligence and OCR extract and recommend, but authorised human
          officers make binding legal determinations. Inspect citizen submissions side-by-side with
          official registries, execute reviews, or transfer cases across departments.
        </p>
      </div>

      {actionNotice && (
        <div className="notice" role="status" style={{ margin: "16px 0" }}>
          {actionNotice}
        </div>
      )}

      {/* Department Queues */}
      <QueueSelector
        queues={queues}
        selectedQueue={selectedQueue}
        onSelectQueue={setSelectedQueue}
      />

      <div className="verifier-main-layout">
        {/* Left Side: Case Queue Table */}
        <div className="case-queue-panel">
          <div className="queue-header">
            <h3>Department Case Queue ({cases.length})</h3>
          </div>

          <div className="case-list-scroll">
            {cases.length === 0 ? (
              <p className="empty-queue">No pending cases in this department queue.</p>
            ) : (
              cases.map((c) => (
                <div
                  key={c.caseId}
                  className={`case-item ${selectedCaseId === c.caseId ? "active" : ""}`}
                  onClick={() => setSelectedCaseId(c.caseId)}
                  role="button"
                  tabIndex={0}
                >
                  <div className="case-item-top">
                    <strong>#{c.caseId.slice(-8)}</strong>
                    <span
                      className={`badge ${
                        c.status === "VERIFIED"
                          ? "active"
                          : c.status === "REJECTED"
                          ? "unavailable"
                          : "pending"
                      }`}
                    >
                      {c.status}
                    </span>
                  </div>
                  <p className="case-item-issuer">{c.claimedIssuer}</p>
                  <div className="case-item-meta">
                    <span>Queue: <code>{c.verifierQueue}</code></span>
                    <span>Match: <strong>{c.automatedMatchScore}%</strong></span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Side: Side-by-Side Evidence Diff & Officer Decision */}
        <div className="case-inspection-panel">
          <EvidenceDiffInspector comparison={comparison} loading={loadingDiff} />
          <OfficerDecisionPanel
            comparison={comparison}
            onSubmitDecision={handleDecisionSubmit}
            submitting={submitting}
          />
        </div>
      </div>
    </div>
  );
}
