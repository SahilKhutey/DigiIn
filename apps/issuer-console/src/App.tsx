import React, { useState, useEffect } from "react";

interface QueueSummary {
  queueId: string;
  name: string;
  department: string;
  pendingCount: number;
  verifiedCount: number;
  totalCount: number;
}

interface VerificationCase {
  caseId: string;
  documentId: string;
  claimedIssuer: string;
  status: string;
  automatedMatchScore: number;
  recommendedAction: string;
  verifierQueue: string;
  createdAt: string;
}

interface FieldComparison {
  field: string;
  label: string;
  citizenValue: string;
  registryValue: string;
  isMatch: boolean;
  matchConfidence: number;
  discrepancyNote: string | null;
}

interface CaseComparison {
  caseId: string;
  documentId: string;
  documentType: string;
  subjectId: string;
  verifierQueue: string;
  claimedIssuer: string;
  overallMatchScore: number;
  recommendedAction: string;
  citizenClaims: Record<string, any>;
  officialRegistryClaims: Record<string, any>;
  fieldComparisons: FieldComparison[];
  caseStatus: string;
  createdAt: string;
}

export function App() {
  const [queues, setQueues] = useState<QueueSummary[]>([]);
  const [selectedQueue, setSelectedQueue] = useState<string>("queue_cbse");
  const [cases, setCases] = useState<VerificationCase[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [comparison, setComparison] = useState<CaseComparison | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<string>("");

  const API_BASE = "http://localhost:8000/api/v1";

  const fetchQueuesAndCases = async () => {
    setLoading(true);
    try {
      const qRes = await fetch(`${API_BASE}/government/queues`);
      if (qRes.ok) {
        const qData = await qRes.json();
        setQueues(qData);
      }
      const cRes = await fetch(`${API_BASE}/government/cases?queue=${selectedQueue}`);
      if (cRes.ok) {
        const cData = await cRes.json();
        setCases(cData);
      }
    } catch {
      setMessage("API server offline. Ensure backend is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCase = async (caseId: string) => {
    setSelectedCaseId(caseId);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/government/cases/${caseId}/comparison`);
      if (res.ok) {
        setComparison(await res.json());
      }
    } catch (e: any) {
      setMessage(`Failed to load comparison: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDecide = async (decision: "VERIFY" | "REJECT" | "TRANSFER" | "REQUEST_MORE_EVIDENCE", transferQueue?: string) => {
    if (!selectedCaseId) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/government/cases/${selectedCaseId}/decision`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          decision,
          verifierId: "officer_cbse_delhi_central",
          note: `Adjudication decision: ${decision}. Inspected by authorized reviewing officer.`,
          transferQueue: transferQueue || undefined,
        }),
      });
      if (res.ok) {
        setMessage(`✓ Case ${selectedCaseId} successfully updated with decision '${decision}'!`);
        setSelectedCaseId(null);
        setComparison(null);
        fetchQueuesAndCases();
      }
    } catch (e: any) {
      setMessage(`Decision error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueuesAndCases();
  }, [selectedQueue]);

  return (
    <div style={{ fontFamily: "Inter, sans-serif", padding: "2rem", maxWidth: "1280px", margin: "0 auto", color: "#0f172a" }}>
      <header style={{ borderBottom: "1px solid #e2e8f0", paddingBottom: "1.25rem", marginBottom: "2rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ margin: 0, fontSize: "1.625rem", fontWeight: "700" }}>Government Issuer & Review Console</h1>
          <p style={{ margin: "0.25rem 0 0 0", color: "#64748b", fontSize: "0.875rem" }}>
            Authoritative Credential Issuance & Discrepancy Adjudication Queue
          </p>
        </div>
        <button
          onClick={fetchQueuesAndCases}
          style={{ padding: "0.5rem 1rem", backgroundColor: "#f1f5f9", border: "1px solid #cbd5e1", borderRadius: "6px", cursor: "pointer", fontSize: "0.875rem", fontWeight: "600" }}
        >
          🔄 Refresh Queues
        </button>
      </header>

      {message && (
        <div style={{ padding: "0.75rem 1rem", backgroundColor: "#eff6ff", border: "1px solid #bfdbfe", color: "#1e40af", borderRadius: "8px", marginBottom: "1.5rem", fontSize: "0.875rem" }}>
          {message}
        </div>
      )}

      {/* Departmental Queues Summary Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
        {queues.map((q) => (
          <div
            key={q.queueId}
            onClick={() => setSelectedQueue(q.queueId)}
            style={{
              padding: "1.25rem",
              borderRadius: "8px",
              border: selectedQueue === q.queueId ? "2px solid #2563eb" : "1px solid #e2e8f0",
              backgroundColor: selectedQueue === q.queueId ? "#eff6ff" : "#ffffff",
              cursor: "pointer",
              transition: "all 0.15s ease",
            }}
          >
            <div style={{ fontSize: "0.75rem", textTransform: "uppercase", color: "#64748b", fontWeight: "700" }}>
              {q.department}
            </div>
            <div style={{ fontSize: "1.125rem", fontWeight: "700", marginTop: "0.25rem" }}>{q.name}</div>
            <div style={{ display: "flex", gap: "1rem", marginTop: "0.75rem", fontSize: "0.875rem" }}>
              <span style={{ color: "#b45309", fontWeight: "600" }}>{q.pendingCount} Pending</span>
              <span style={{ color: "#16a34a", fontWeight: "600" }}>{q.verifiedCount} Verified</span>
            </div>
          </div>
        ))}
      </div>

      {/* Main Content Area: Cases List & Comparison Detail */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.3fr", gap: "1.5rem" }}>
        {/* Cases List */}
        <div style={{ backgroundColor: "#ffffff", border: "1px solid #e2e8f0", borderRadius: "8px", padding: "1.25rem" }}>
          <h2 style={{ fontSize: "1rem", fontWeight: "700", margin: "0 0 1rem 0" }}>
            Active Cases in {queues.find((q) => q.queueId === selectedQueue)?.name || selectedQueue} ({cases.length})
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", maxHeight: "600px", overflowY: "auto" }}>
            {cases.map((c) => (
              <div
                key={c.caseId}
                onClick={() => handleSelectCase(c.caseId)}
                style={{
                  padding: "1rem",
                  borderRadius: "6px",
                  border: selectedCaseId === c.caseId ? "2px solid #2563eb" : "1px solid #e2e8f0",
                  backgroundColor: selectedCaseId === c.caseId ? "#f8fafc" : "#ffffff",
                  cursor: "pointer",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontWeight: "700", fontSize: "0.875rem" }}>{c.caseId}</span>
                  <span
                    style={{
                      fontSize: "0.75rem",
                      fontWeight: "700",
                      padding: "0.2rem 0.5rem",
                      borderRadius: "4px",
                      backgroundColor: c.status === "VERIFIED" ? "#dcfce7" : c.status === "REJECTED" ? "#fee2e2" : "#fef3c7",
                      color: c.status === "VERIFIED" ? "#166534" : c.status === "REJECTED" ? "#991b1b" : "#92400e",
                    }}
                  >
                    {c.status}
                  </span>
                </div>
                <div style={{ fontSize: "0.8125rem", color: "#64748b", marginTop: "0.35rem" }}>
                  Match Confidence: <strong>{c.automatedMatchScore}%</strong> • Issuer: {c.claimedIssuer}
                </div>
                <div style={{ fontSize: "0.75rem", color: "#475569", marginTop: "0.25rem" }}>{c.recommendedAction}</div>
              </div>
            ))}
            {!cases.length && (
              <div style={{ padding: "2rem", textAlign: "center", color: "#94a3b8", fontSize: "0.875rem" }}>
                No active discrepancy cases in this queue.
              </div>
            )}
          </div>
        </div>

        {/* Side-by-Side Comparison & Action Pane */}
        <div style={{ backgroundColor: "#ffffff", border: "1px solid #e2e8f0", borderRadius: "8px", padding: "1.25rem" }}>
          {comparison ? (
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #e2e8f0", paddingBottom: "0.75rem", marginBottom: "1rem" }}>
                <div>
                  <h3 style={{ margin: 0, fontSize: "1.125rem", fontWeight: "700" }}>Evidence Discrepancy Inspection</h3>
                  <div style={{ fontSize: "0.75rem", color: "#64748b" }}>Case ID: {comparison.caseId} • Document: {comparison.documentType}</div>
                </div>
                <span style={{ fontSize: "0.875rem", fontWeight: "700", padding: "0.25rem 0.75rem", backgroundColor: "#eff6ff", color: "#1d4ed8", borderRadius: "6px" }}>
                  Match Score: {comparison.overallMatchScore}%
                </span>
              </div>

              {/* Field by Field Comparison Table */}
              <div style={{ overflowX: "auto", marginBottom: "1.5rem" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8125rem" }}>
                  <thead>
                    <tr style={{ backgroundColor: "#f8fafc", textAlign: "left" }}>
                      <th style={{ padding: "0.5rem", borderBottom: "1px solid #e2e8f0" }}>Field</th>
                      <th style={{ padding: "0.5rem", borderBottom: "1px solid #e2e8f0" }}>Citizen OCR Claim</th>
                      <th style={{ padding: "0.5rem", borderBottom: "1px solid #e2e8f0" }}>Official State Registry</th>
                      <th style={{ padding: "0.5rem", borderBottom: "1px solid #e2e8f0" }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparison.fieldComparisons.map((fc, idx) => (
                      <tr key={idx} style={{ borderBottom: "1px solid #f1f5f9" }}>
                        <td style={{ padding: "0.5rem", fontWeight: "600" }}>{fc.label}</td>
                        <td style={{ padding: "0.5rem", color: "#334155" }}>{fc.citizenValue}</td>
                        <td style={{ padding: "0.5rem", color: "#0f172a", fontWeight: "500" }}>{fc.registryValue}</td>
                        <td style={{ padding: "0.5rem" }}>
                          {fc.isMatch ? (
                            <span style={{ color: "#16a34a", fontWeight: "700" }}>✓ Match</span>
                          ) : (
                            <span style={{ color: "#dc2626", fontWeight: "700" }}>✕ Diff</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Officer Action Buttons */}
              <div style={{ borderTop: "1px solid #e2e8f0", paddingTop: "1rem" }}>
                <h4 style={{ margin: "0 0 0.75rem 0", fontSize: "0.875rem", fontWeight: "700" }}>Officer Adjudication Actions</h4>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem" }}>
                  <button
                    onClick={() => handleDecide("VERIFY")}
                    disabled={loading}
                    style={{ padding: "0.625rem 1.25rem", backgroundColor: "#16a34a", color: "#ffffff", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: "600", fontSize: "0.8125rem" }}
                  >
                    ✓ Approve & Mint Level 4 Credential
                  </button>
                  <button
                    onClick={() => handleDecide("REJECT")}
                    disabled={loading}
                    style={{ padding: "0.625rem 1.25rem", backgroundColor: "#dc2626", color: "#ffffff", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: "600", fontSize: "0.8125rem" }}
                  >
                    ✕ Reject Case
                  </button>
                  <button
                    onClick={() => handleDecide("TRANSFER", "queue_revenue")}
                    disabled={loading}
                    style={{ padding: "0.625rem 1rem", backgroundColor: "#f1f5f9", color: "#334155", border: "1px solid #cbd5e1", borderRadius: "6px", cursor: "pointer", fontWeight: "600", fontSize: "0.8125rem" }}
                  >
                    ➔ Transfer to Revenue
                  </button>
                  <button
                    onClick={() => handleDecide("REQUEST_MORE_EVIDENCE")}
                    disabled={loading}
                    style={{ padding: "0.625rem 1rem", backgroundColor: "#fef3c7", color: "#92400e", border: "1px solid #fde68a", borderRadius: "6px", cursor: "pointer", fontWeight: "600", fontSize: "0.8125rem" }}
                  >
                    ❓ Request Evidence
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ padding: "4rem 2rem", textAlign: "center", color: "#94a3b8" }}>
              <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>📋</div>
              <div style={{ fontWeight: "600", fontSize: "0.9375rem" }}>Select a case from the list</div>
              <div style={{ fontSize: "0.8125rem", marginTop: "0.25rem" }}>View extracted OCR claims against state registry records.</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
