import { useState } from "react";
import type {
  EvidenceComparisonDetail,
  GovernmentDecisionPayload,
  VerifierQueueId,
} from "../../types";

type OfficerDecisionPanelProps = {
  comparison: EvidenceComparisonDetail | null;
  onSubmitDecision: (payload: GovernmentDecisionPayload) => void;
  submitting: boolean;
};

export function OfficerDecisionPanel({
  comparison,
  onSubmitDecision,
  submitting,
}: OfficerDecisionPanelProps) {
  const [verifierId, setVerifierId] = useState("officer_cbse_senior_evaluator_04");
  const [note, setNote] = useState(
    "Corroborated identity attributes and roll number against secondary gazette registry."
  );
  const [transferQueue, setTransferQueue] = useState<VerifierQueueId>("queue_revenue");

  if (!comparison) return null;

  const isDecided =
    comparison.caseStatus === "VERIFIED" || comparison.caseStatus === "REJECTED";

  return (
    <section className="officer-decision-panel" aria-label="Government officer decision panel">
      <div className="panel-heading">
        <p className="eyebrow">AUTHORITATIVE OFFICER DETERMINATION</p>
        <h4>Binding Review Decision for Case #{comparison.caseId.slice(-8)}</h4>
      </div>

      {isDecided ? (
        <div className="decision-notice-box">
          <p>
            This case has already been decided with status:{" "}
            <strong>{comparison.caseStatus}</strong>.
          </p>
        </div>
      ) : (
        <div className="decision-form">
          <div className="form-grid">
            <label>
              Reviewing Officer ID / Signature
              <input
                type="text"
                value={verifierId}
                onChange={(e) => setVerifierId(e.target.value)}
                placeholder="e.g. officer_cbse_04"
              />
            </label>

            <label>
              Transfer Target Queue (if transferring)
              <select
                value={transferQueue}
                onChange={(e) => setTransferQueue(e.target.value as VerifierQueueId)}
              >
                <option value="queue_cbse">CBSE Education Board Queue</option>
                <option value="queue_revenue">State Land & Revenue Archives</option>
                <option value="queue_transport">Transport Authority (MoRTH)</option>
                <option value="queue_general">General DPI Review Queue</option>
              </select>
            </label>
          </div>

          <label style={{ display: "grid", gap: "6px", marginTop: "12px" }}>
            Officer Decision Justification Note (Required for Audit Trail)
            <input
              type="text"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="State reason for verification, transfer or rejection..."
            />
          </label>

          <div className="decision-actions-row">
            <button
              type="button"
              className="btn-verify"
              disabled={submitting}
              onClick={() =>
                onSubmitDecision({
                  decision: "VERIFY",
                  verifierId,
                  note,
                })
              }
            >
              Approve & Verify (Issue Level 4)
            </button>

            <button
              type="button"
              className="btn-evidence"
              disabled={submitting}
              onClick={() =>
                onSubmitDecision({
                  decision: "REQUEST_MORE_EVIDENCE",
                  verifierId,
                  note,
                })
              }
            >
              Request More Evidence
            </button>

            <button
              type="button"
              className="btn-transfer"
              disabled={submitting}
              onClick={() =>
                onSubmitDecision({
                  decision: "TRANSFER",
                  verifierId,
                  note,
                  transferQueue,
                })
              }
            >
              Transfer Queue
            </button>

            <button
              type="button"
              className="btn-reject"
              disabled={submitting}
              onClick={() =>
                onSubmitDecision({
                  decision: "REJECT",
                  verifierId,
                  note,
                })
              }
            >
              Reject Case
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
