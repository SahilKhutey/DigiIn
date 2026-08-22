import React, { useState } from "react";

export function App() {
  const [credentialType, setCredentialType] = useState("CLASS_XII");
  const [purpose, setPurpose] = useState("EXAMINATION_APPLICATION");
  const [createdRequestId, setCreatedRequestId] = useState<string | null>(null);

  const handleCreateRequest = (e: React.FormEvent) => {
    e.preventDefault();
    setCreatedRequestId(`req_${Date.now().toString(36)}`);
  };

  return (
    <div style={{ fontFamily: "sans-serif", padding: "2rem", maxWidth: "900px", margin: "0 auto" }}>
      <header style={{ borderBottom: "1px solid #e2e8f0", paddingBottom: "1rem", marginBottom: "2rem" }}>
        <h1 style={{ margin: 0, fontSize: "1.5rem", color: "#0f172a" }}>Requester Portal — National Testing Agency</h1>
        <p style={{ margin: "0.25rem 0 0 0", color: "#64748b" }}>
          Purpose-Bound Credential Verification Inquiries (Zero Raw Document Storage)
        </p>
      </header>

      <form onSubmit={handleCreateRequest} style={{ backgroundColor: "#ffffff", border: "1px solid #e2e8f0", borderRadius: "8px", padding: "1.5rem" }}>
        <h2 style={{ fontSize: "1.125rem", margin: "0 0 1.25rem 0" }}>Create New Verification Request</h2>

        <div style={{ marginBottom: "1rem" }}>
          <label style={{ display: "block", fontSize: "0.875rem", fontWeight: "600", color: "#334155", marginBottom: "0.5rem" }}>
            Target Credential
          </label>
          <select
            value={credentialType}
            onChange={(e) => setCredentialType(e.target.value)}
            style={{ width: "100%", padding: "0.625rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
          >
            <option value="CLASS_XII">Class XII Passing Certificate (CBSE / State Boards)</option>
            <option value="BTECH_DEGREE">University Graduation Degree</option>
            <option value="DOMICILE">State Domicile Certificate</option>
          </select>
        </div>

        <div style={{ marginBottom: "1.5rem" }}>
          <label style={{ display: "block", fontSize: "0.875rem", fontWeight: "600", color: "#334155", marginBottom: "0.5rem" }}>
            Declared Purpose
          </label>
          <input
            type="text"
            value={purpose}
            onChange={(e) => setPurpose(e.target.value)}
            style={{ width: "100%", padding: "0.625rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
          />
        </div>

        <button
          type="submit"
          style={{ padding: "0.75rem 1.5rem", backgroundColor: "#2563eb", color: "#fff", border: "none", borderRadius: "6px", fontWeight: "600", cursor: "pointer" }}
        >
          Create & Dispatch Verification Request
        </button>

        {createdRequestId && (
          <div style={{ marginTop: "1.5rem", padding: "1rem", backgroundColor: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: "6px", color: "#166534" }}>
            ✓ Verification Request Created: <strong>{createdRequestId}</strong> (Awaiting Citizen Consent)
          </div>
        )}
      </form>
    </div>
  );
}

export default App;
