import type { DocumentVersionRecord } from "../../types";

type VersionChainProps = {
  versions: DocumentVersionRecord[];
};

export function VersionChain({ versions }: VersionChainProps) {
  return (
    <div style={{ marginTop: "24px" }}>
      <p className="eyebrow">IMMUTABLE VERSION CHAIN</p>
      <h3>
        Document Version History ({versions.length}{" "}
        {versions.length === 1 ? "version" : "versions"})
      </h3>
      <ul className="version-list" aria-label="Version history list">
        {versions.map((v) => (
          <li key={v.versionId} className={`version-card ${v.status.toLowerCase()}`}>
            <div className="version-header">
              <strong>
                Version {v.versionNumber} ({v.versionId})
              </strong>
              <span className={`badge ${v.status.toLowerCase()}`}>{v.status}</span>
            </div>
            <p className="version-meta">
              Authority: <strong>{v.authority}</strong> • Created:{" "}
              {new Date(v.createdAt).toLocaleTimeString()}
              {v.supersededAt && ` • Superseded: ${new Date(v.supersededAt).toLocaleTimeString()}`}
            </p>
            <p style={{ margin: "4px 0", color: "#334155" }}>{v.changeSummary}</p>
            <div className="diff-box">
              <strong>Snapshot Claims:</strong> {JSON.stringify(v.metadata)}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
