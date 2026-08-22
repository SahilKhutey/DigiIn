import React, { useState } from "react";

export function App() {
  const [stats] = useState({
    issued: "1,284,912",
    verified: "1,241,008",
    pending: "3,204",
    revoked: "12,300",
  });

  return (
    <div style={{ fontFamily: "sans-serif", padding: "2rem", maxWidth: "1200px", margin: "0 auto" }}>
      <header style={{ borderBottom: "1px solid #e2e8f0", paddingBottom: "1rem", marginBottom: "2rem" }}>
        <h1 style={{ margin: 0, fontSize: "1.5rem", color: "#0f172a" }}>CBSE — Issuer Administration Console</h1>
        <p style={{ margin: "0.25rem 0 0 0", color: "#64748b" }}>
          Authoritative Credential Issuance & Verification Authority
        </p>
      </header>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1rem", marginBottom: "2rem" }}>
        <div style={{ padding: "1.5rem", backgroundColor: "#f8fafc", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
          <div style={{ fontSize: "0.875rem", color: "#64748b" }}>Credentials Issued</div>
          <div style={{ fontSize: "1.75rem", fontWeight: "700", color: "#0f172a", marginTop: "0.5rem" }}>{stats.issued}</div>
        </div>
        <div style={{ padding: "1.5rem", backgroundColor: "#f0fdf4", borderRadius: "8px", border: "1px solid #bbf7d0" }}>
          <div style={{ fontSize: "0.875rem", color: "#166534" }}>Verified Queries</div>
          <div style={{ fontSize: "1.75rem", fontWeight: "700", color: "#15803d", marginTop: "0.5rem" }}>{stats.verified}</div>
        </div>
        <div style={{ padding: "1.5rem", backgroundColor: "#fffbeb", borderRadius: "8px", border: "1px solid #fef3c7" }}>
          <div style={{ fontSize: "0.875rem", color: "#92400e" }}>Pending Review</div>
          <div style={{ fontSize: "1.75rem", fontWeight: "700", color: "#b45309", marginTop: "0.5rem" }}>{stats.pending}</div>
        </div>
        <div style={{ padding: "1.5rem", backgroundColor: "#fef2f2", borderRadius: "8px", border: "1px solid #fecaca" }}>
          <div style={{ fontSize: "0.875rem", color: "#991b1b" }}>Revoked</div>
          <div style={{ fontSize: "1.75rem", fontWeight: "700", color: "#b91c1c", marginTop: "0.5rem" }}>{stats.revoked}</div>
        </div>
      </div>

      <div style={{ backgroundColor: "#ffffff", border: "1px solid #e2e8f0", borderRadius: "8px", padding: "1.5rem" }}>
        <h2 style={{ fontSize: "1.125rem", margin: "0 0 1rem 0" }}>Quick Actions</h2>
        <div style={{ display: "flex", gap: "1rem" }}>
          <button style={{ padding: "0.75rem 1.25rem", backgroundColor: "#2563eb", color: "#fff", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: "600" }}>
            + Issue Single Credential
          </button>
          <button style={{ padding: "0.75rem 1.25rem", backgroundColor: "#f1f5f9", color: "#334155", border: "1px solid #cbd5e1", borderRadius: "6px", cursor: "pointer", fontWeight: "600" }}>
            Batch Bulk Upload (CSV)
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
