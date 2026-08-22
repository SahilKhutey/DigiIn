import type { EvidenceComparisonDetail } from "../../types";

type EvidenceDiffInspectorProps = {
  comparison: EvidenceComparisonDetail | null;
  loading: boolean;
};

export function EvidenceDiffInspector({
  comparison,
  loading,
}: EvidenceDiffInspectorProps) {
  if (loading) {
    return (
      <div className="inspector-loading">
        <p>Loading side-by-side evidence inspection diff...</p>
      </div>
    );
  }

  if (!comparison) {
    return (
      <div className="inspector-placeholder">
        <p>Select a verification case from the queue to inspect side-by-side evidence.</p>
      </div>
    );
  }

  return (
    <section className="evidence-inspector" aria-label="Evidence comparison inspection panel">
      <div className="inspector-header">
        <div>
          <span className="case-id-badge">Case #{comparison.caseId.slice(-8)}</span>
          <h3 className="inspector-title">
            {comparison.documentType.replace(/_/g, " ")} Verification Review
          </h3>
          <p className="inspector-subtitle">
            Claimed Authority: <strong>{comparison.claimedIssuer}</strong> • Subject:{" "}
            <code>{comparison.subjectId}</code>
          </p>
        </div>

        <div className="match-score-card">
          <span className="score-label">Automated Match Score</span>
          <div className="score-badge-row">
            <span
              className={`score-badge ${
                comparison.overallMatchScore >= 85
                  ? "high-match"
                  : comparison.overallMatchScore >= 65
                  ? "med-match"
                  : "low-match"
              }`}
            >
              {comparison.overallMatchScore}%
            </span>
          </div>
        </div>
      </div>

      <div className="recommendation-banner">
        <strong>Automated System Recommendation:</strong> {comparison.recommendedAction}
      </div>

      {/* Side-by-Side Comparison Table */}
      <div className="comparison-table-wrapper">
        <table className="comparison-table">
          <thead>
            <tr>
              <th style={{ width: "22%" }}>Attribute</th>
              <th style={{ width: "35%" }}>Citizen Claim / OCR Extract</th>
              <th style={{ width: "35%" }}>Official Department Registry</th>
              <th style={{ width: "8%" }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {comparison.fieldComparisons.map((field) => (
              <tr
                key={field.field}
                className={field.isMatch ? "match-row" : "mismatch-row"}
              >
                <td>
                  <strong>{field.label}</strong>
                  <span className="field-code">{field.field}</span>
                </td>
                <td>
                  <code className="claim-text citizen-claim">{field.citizenValue}</code>
                </td>
                <td>
                  <code className="claim-text registry-claim">{field.registryValue}</code>
                </td>
                <td>
                  <span
                    className={`diff-status-pill ${
                      field.isMatch ? "match-pill" : "mismatch-pill"
                    }`}
                    title={field.discrepancyNote ?? ""}
                  >
                    {field.isMatch ? "MATCH" : "DIFF"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
