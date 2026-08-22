import type { CorrectionRequestRecord } from "../../types";

type OfficerQueueProps = {
  documentId: string;
  corrections: CorrectionRequestRecord[];
  onDecide: (requestId: string, decision: "APPROVE" | "REJECT") => void;
};

export function OfficerQueue({
  documentId,
  corrections,
  onDecide,
}: OfficerQueueProps) {
  if (corrections.length === 0) return null;

  return (
    <section className="consent-panel" style={{ marginTop: "24px" }} aria-label="Officer review queue">
      <p className="eyebrow">OFFICER REVIEW QUEUE</p>
      <h3>Pending Correction Cases for {documentId}</h3>
      <ul className="requirement-list">
        {corrections.map((c) => (
          <li
            key={c.requestId}
            style={{
              borderLeft:
                c.status === "APPROVED"
                  ? "4px solid #197345"
                  : c.status === "REJECTED"
                  ? "4px solid #c93b27"
                  : "4px solid #f59e0b",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <strong>
                Case #{c.requestId.slice(-6)} • Field: <code>{c.field}</code>
              </strong>
              <span
                className={`badge ${
                  c.status === "APPROVED"
                    ? "active"
                    : c.status === "REJECTED"
                    ? "unavailable"
                    : "pending"
                }`}
              >
                {c.status}
              </span>
            </div>
            <p style={{ margin: "6px 0", color: "#244a65" }}>
              Correction: <s>{c.currentValue}</s> &rarr; <strong>{c.proposedValue}</strong>
            </p>
            <p style={{ margin: "2px 0", fontSize: ".85rem", color: "#5c7385" }}>
              Reason: {c.reason} | Evidence: {c.evidenceDescription ?? "Primary Gazette"}
            </p>
            {c.reviewerNote && (
              <p style={{ margin: "4px 0 0", fontSize: ".85rem", color: "#1e3a8a" }}>
                Officer Decision Note: {c.reviewerNote} ({c.reviewerId})
              </p>
            )}
            {c.status === "PENDING_REVIEW" && (
              <div style={{ marginTop: "8px" }}>
                <button type="button" onClick={() => onDecide(c.requestId, "APPROVE")}>
                  Approve (Issue Next Version)
                </button>
                <button
                  className="danger"
                  type="button"
                  onClick={() => onDecide(c.requestId, "REJECT")}
                >
                  Reject correction
                </button>
              </div>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
