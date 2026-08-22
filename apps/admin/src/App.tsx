import React from "react";

export function App() {
  return (
    <div style={{ fontFamily: "sans-serif", padding: "2rem", maxWidth: "1200px", margin: "0 auto" }}>
      <header style={{ borderBottom: "1px solid #e2e8f0", paddingBottom: "1rem", marginBottom: "2rem" }}>
        <h1 style={{ margin: 0, fontSize: "1.5rem", color: "#0f172a" }}>DigiLocker X — System Administration</h1>
        <p style={{ margin: "0.25rem 0 0 0", color: "#64748b" }}>
          Platform Governance, Issuer Onboarding, Trust Anchors & Global Policies
        </p>
      </header>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem", marginBottom: "2rem" }}>
        <div style={{ padding: "1.5rem", backgroundColor: "#f8fafc", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
          <div style={{ fontSize: "0.875rem", color: "#64748b" }}>Registered Issuers</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "700", color: "#0f172a", marginTop: "0.5rem" }}>42 Authorities</div>
        </div>
        <div style={{ padding: "1.5rem", backgroundColor: "#f8fafc", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
          <div style={{ fontSize: "0.875rem", color: "#64748b" }}>Hardware Security Module (HSM)</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "700", color: "#16a34a", marginTop: "0.5rem" }}>ACTIVE (Ed25519)</div>
        </div>
        <div style={{ padding: "1.5rem", backgroundColor: "#f8fafc", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
          <div style={{ fontSize: "0.875rem", color: "#64748b" }}>Throughput</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "700", color: "#2563eb", marginTop: "0.5rem" }}>450 proofs/sec</div>
        </div>
      </div>

      <div style={{ backgroundColor: "#ffffff", border: "1px solid #e2e8f0", borderRadius: "8px", padding: "1.5rem" }}>
        <h2 style={{ fontSize: "1.125rem", margin: "0 0 1rem 0" }}>Administration Areas</h2>
        <ul style={{ paddingLeft: "1.25rem", color: "#475569", lineHeight: "1.8" }}>
          <li>Organizations & Identity Providers</li>
          <li>Issuer Registry & Public Key Anchors</li>
          <li>Verification Rule Policies & Escalation Queues</li>
          <li>Sovereign Audit Ledger & Event Stream</li>
          <li>Global Feature Flags & Maintenance Safeguards</li>
        </ul>
      </div>
    </div>
  );
}

export default App;
