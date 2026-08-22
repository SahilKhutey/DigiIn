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

export function VerifierDashboard({ onRefreshWallet }: VerifierDashboardProps) {
  const [queues, setQueues] = useState<VerifierQueueSummary[]>([]);
  const [selectedQueue, setSelectedQueue] = useState<VerifierQueueId | "ALL">("ALL");
  const [cases, setCases] = useState<VerificationCase[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState<string>("");
  const [comparison, setComparison] = useState<EvidenceComparisonDetail | null>(null);
  const [loadingDiff, setLoadingDiff] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [actionNotice, setActionNotice] = useState("");

  const refreshQueuesAndCases = () => {
    api.fetchVerifierQueues().then(setQueues).catch(() => undefined);
    const qParam = selectedQueue === "ALL" ? undefined : selectedQueue;
    api
      .fetchVerifierCases(qParam)
      .then((caseList) => {
        setCases(caseList);
        if (caseList.length > 0 && !selectedCaseId) {
          setSelectedCaseId(caseList[0].caseId);
        }
      })
      .catch(() => undefined);
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
          setComparison(null);
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
        setActionNotice("Failed to submit officer decision.");
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
