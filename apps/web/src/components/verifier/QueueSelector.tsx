import type { VerifierQueueId, VerifierQueueSummary } from "../../types";

type QueueSelectorProps = {
  queues: VerifierQueueSummary[];
  selectedQueue: VerifierQueueId | "ALL";
  onSelectQueue: (queueId: VerifierQueueId | "ALL") => void;
};

export function QueueSelector({
  queues,
  selectedQueue,
  onSelectQueue,
}: QueueSelectorProps) {
  const totalPending = queues.reduce((sum, q) => sum + q.pendingCount, 0);

  return (
    <div className="verifier-queue-selector" role="tablist" aria-label="Department Verifier Queues">
      <button
        type="button"
        className={`queue-tab ${selectedQueue === "ALL" ? "active" : ""}`}
        onClick={() => onSelectQueue("ALL")}
        role="tab"
        aria-selected={selectedQueue === "ALL"}
      >
        <span className="queue-title">All Departments</span>
        <span className="queue-badge pending-badge">{totalPending} pending</span>
      </button>

      {queues.map((q) => (
        <button
          key={q.queueId}
          type="button"
          className={`queue-tab ${selectedQueue === q.queueId ? "active" : ""}`}
          onClick={() => onSelectQueue(q.queueId)}
          role="tab"
          aria-selected={selectedQueue === q.queueId}
        >
          <span className="queue-title">{q.name}</span>
          <span className="queue-dept">{q.department}</span>
          <div className="queue-meta-row">
            <span className="queue-badge pending-badge">{q.pendingCount} pending</span>
            <span className="queue-badge verified-badge">{q.verifiedCount} verified</span>
          </div>
        </button>
      ))}
    </div>
  );
}
