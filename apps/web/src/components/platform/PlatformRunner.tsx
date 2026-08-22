import type { PlatformSnapshot, StudentDemo } from "../../types";
import { SnapshotMetrics } from "./SnapshotMetrics";

type PlatformRunnerProps = {
  snapshot: PlatformSnapshot | null;
  studentDemo: StudentDemo | null;
  onRunDemo: () => void;
};

export function PlatformRunner({
  snapshot,
  studentDemo,
  onRunDemo,
}: PlatformRunnerProps) {
  return (
    <section className="card platform-card" aria-labelledby="platform-title">
      <div className="card-heading">
        <div>
          <p className="eyebrow">RUNNABLE PRODUCT PLATFORM</p>
          <h2 id="platform-title">Student document to verified proof</h2>
        </div>
        <span className="badge resolved">vertical slice</span>
      </div>
      <p className="summary">
        This demo runs the canonical MVP path through API, domain state, transaction, mock
        government review, audit events, and proof generation.
      </p>

      <button type="button" onClick={onRunDemo}>
        Run student vertical slice
      </button>

      <SnapshotMetrics snapshot={snapshot} />

      {studentDemo && (
        <section className="result-panel" aria-label="Student demo result">
          <div className="stage-title">
            <h3>
              {studentDemo.document.documentType} credential (v
              {studentDemo.document.currentVersion})
            </h3>
            <span>{studentDemo.document.status}</span>
          </div>
          <div className="health-grid">
            <p>
              <strong>Document ID</strong>
              <span>{studentDemo.document.documentId}</span>
            </p>
            <p>
              <strong>Verifier</strong>
              <span>{studentDemo.verificationCase.claimedIssuer}</span>
            </p>
            <p>
              <strong>Proof Status</strong>
              <span>{studentDemo.proofResult.status}</span>
            </p>
          </div>
          <ol className="proof-results" aria-label="Domain audit events">
            {studentDemo.events.map((event) => (
              <li key={event.eventId} className="complete">
                <strong>{event.type}</strong>
                <span>{event.message}</span>
              </li>
            ))}
          </ol>
        </section>
      )}
    </section>
  );
}
