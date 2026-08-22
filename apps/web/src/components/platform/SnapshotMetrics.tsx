import type { PlatformSnapshot } from "../../types";

type SnapshotMetricsProps = {
  snapshot: PlatformSnapshot | null;
};

export function SnapshotMetrics({ snapshot }: SnapshotMetricsProps) {
  if (!snapshot) return null;

  return (
    <div className="platform-grid" aria-label="Platform state counters">
      <p>
        <strong>Feature flags</strong>
        <span>{snapshot.featureFlags.filter((f) => f.enabled).length} enabled</span>
      </p>
      <p>
        <strong>Documents</strong>
        <span>{snapshot.documents.length}</span>
      </p>
      <p>
        <strong>Versions tracked</strong>
        <span>{snapshot.versions.length}</span>
      </p>
      <p>
        <strong>Correction cases</strong>
        <span>{snapshot.corrections.length}</span>
      </p>
    </div>
  );
}
