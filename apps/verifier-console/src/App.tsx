import React, { useState } from "react";

interface IntrospectionResult {
  active: boolean;
  status: string;
  keyId: string;
  algorithm: string;
  cryptoVerified: boolean;
  audience: string;
  purpose: string;
  disclosureLevel: string;
  results: any[];
  receipt: any;
  claims: any;
}

export function App() {
  const [activeTab, setActiveTab] = useState<"query" | "introspect">("query");
  const [credentialType, setCredentialType] = useState("CLASS_XII");
  const [policyMode, setPolicyMode] = useState<"PREDICATE_ONLY" | "BOOLEAN_ONLY" | "FULL_DOCUMENT">("PREDICATE_ONLY");
  const [purpose, setPurpose] = useState("NATIONAL_ENTRANCE_EXAMINATION_ELIGIBILITY");
  const [minPercentage, setMinPercentage] = useState("60.0");
  const [createdRequest, setCreatedRequest] = useState<any | null>(null);

  // Introspector State
  const [tokenInput, setTokenInput] = useState("");
  const [audienceInput, setAudienceInput] = useState("DELHI_UNIVERSITY_ADMISSION");
  const [introspectionResult, setIntrospectionResult] = useState<IntrospectionResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<string>("");

  const API_BASE = "http://localhost:8000/api/v1";

  const handleCreateRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      const res = await fetch(`${API_BASE}/verification/requests`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          requester_name: "National Testing Agency (NTA)",
          credential_type: credentialType,
          purpose: purpose,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setCreatedRequest(data);
        setMessage("✓ Verification Request Ingested into Sovereign Registry!");
      } else {
        const err = await res.json();
        setMessage(`Error: ${JSON.stringify(err)}`);
      }
    } catch {
      setMessage("API server offline. Ensure backend is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  const handleIntrospectToken = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      const res = await fetch(`${API_BASE}/verification/introspect`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          token: tokenInput.trim(),
          audience: audienceInput.trim(),
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setIntrospectionResult(data);
        setMessage("✓ Token cryptographically introspected and verified!");
      } else {
        const err = await res.json();
        setMessage(`Introspection error: ${JSON.stringify(err)}`);
      }
    } catch {
      setMessage("API server offline. Ensure backend is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ fontFamily: "Inter, sans-serif", padding: "2rem", maxWidth: "1080px", margin: "0 auto", color: "#0f172a" }}>
      <header style={{ borderBottom: "1px solid #e2e8f0", paddingBottom: "1.25rem", marginBottom: "2rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ margin: 0, fontSize: "1.625rem", fontWeight: "700" }}>Requester & Verifier Portal</h1>
          <p style={{ margin: "0.25rem 0 0 0", color: "#64748b", fontSize: "0.875rem" }}>
            Zero-Knowledge Verification Queries & RFC 7517/7519 Cryptographic Proof Introspection
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button
            onClick={() => setActiveTab("query")}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "6px",
              border: "1px solid #cbd5e1",
              backgroundColor: activeTab === "query" ? "#2563eb" : "#ffffff",
              color: activeTab === "query" ? "#ffffff" : "#334155",
              cursor: "pointer",
              fontWeight: "600",
              fontSize: "0.875rem",
            }}
          >
            Create Query
          </button>
          <button
            onClick={() => setActiveTab("introspect")}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "6px",
              border: "1px solid #cbd5e1",
              backgroundColor: activeTab === "introspect" ? "#2563eb" : "#ffffff",
              color: activeTab === "introspect" ? "#ffffff" : "#334155",
              cursor: "pointer",
              fontWeight: "600",
              fontSize: "0.875rem",
            }}
          >
            Introspect Proof Token
          </button>
        </div>
      </header>

      {message && (
        <div style={{ padding: "0.75rem 1rem", backgroundColor: "#eff6ff", border: "1px solid #bfdbfe", color: "#1e40af", borderRadius: "8px", marginBottom: "1.5rem", fontSize: "0.875rem" }}>
          {message}
        </div>
      )}

      {activeTab === "query" ? (
        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "2rem" }}>
          <form onSubmit={handleCreateRequest} style={{ backgroundColor: "#ffffff", border: "1px solid #e2e8f0", borderRadius: "8px", padding: "1.5rem" }}>
            <h2 style={{ fontSize: "1.125rem", fontWeight: "700", margin: "0 0 1.25rem 0" }}>Define Verification Policy</h2>

            <div style={{ marginBottom: "1rem" }}>
              <label style={{ display: "block", fontSize: "0.8125rem", fontWeight: "600", color: "#334155", marginBottom: "0.35rem" }}>
                Target Credential Schema
              </label>
              <select
                value={credentialType}
                onChange={(e) => setCredentialType(e.target.value)}
                style={{ width: "100%", padding: "0.625rem", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.875rem" }}
              >
                <option value="CLASS_XII">Class XII Certificate (CBSE / State Boards)</option>
                <option value="BTECH_DEGREE">University Graduation Degree</option>
                <option value="DOMICILE">State Domicile Certificate</option>
                <option value="DRIVING_LICENCE">Driving Licence (MoRTH)</option>
              </select>
            </div>

            <div style={{ marginBottom: "1rem" }}>
              <label style={{ display: "block", fontSize: "0.8125rem", fontWeight: "600", color: "#334155", marginBottom: "0.35rem" }}>
                Disclosure Privacy Mode
              </label>
              <select
                value={policyMode}
                onChange={(e) => setPolicyMode(e.target.value as any)}
                style={{ width: "100%", padding: "0.625rem", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.875rem" }}
              >
                <option value="PREDICATE_ONLY">Zero-Knowledge Predicate (Percentage &gt;= 60%, No Marks Revealed)</option>
                <option value="BOOLEAN_ONLY">Minimum Boolean Verification (VERIFIED = TRUE)</option>
                <option value="FULL_DOCUMENT">Selected Document Attributes</option>
              </select>
            </div>

            {policyMode === "PREDICATE_ONLY" && (
              <div style={{ marginBottom: "1rem", padding: "1rem", backgroundColor: "#f8fafc", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
                <label style={{ display: "block", fontSize: "0.8125rem", fontWeight: "600", color: "#334155", marginBottom: "0.35rem" }}>
                  Minimum Cutoff Threshold (%)
                </label>
                <input
                  type="number"
                  value={minPercentage}
                  onChange={(e) => setMinPercentage(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.875rem" }}
                />
                <span style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "0.25rem", display: "block" }}>
                  The citizen will prove satisfying this rule without transmitting their marksheet.
                </span>
              </div>
            )}

            <div style={{ marginBottom: "1.5rem" }}>
              <label style={{ display: "block", fontSize: "0.8125rem", fontWeight: "600", color: "#334155", marginBottom: "0.35rem" }}>
                Declared Statutory Purpose
              </label>
              <input
                type="text"
                value={purpose}
                onChange={(e) => setPurpose(e.target.value)}
                style={{ width: "100%", padding: "0.625rem", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.875rem" }}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                width: "100%",
                padding: "0.75rem 1.5rem",
                backgroundColor: "#2563eb",
                color: "#ffffff",
                border: "none",
                borderRadius: "6px",
                fontWeight: "600",
                cursor: "pointer",
                fontSize: "0.875rem",
              }}
            >
              {loading ? "Generating Query..." : "Create & Dispatch Verification Inquiry"}
            </button>
          </form>

          {/* Inquiry Status & Dispatch Card */}
          <div style={{ backgroundColor: "#ffffff", border: "1px solid #e2e8f0", borderRadius: "8px", padding: "1.5rem" }}>
            <h3 style={{ margin: "0 0 1rem 0", fontSize: "1rem", fontWeight: "700" }}>Inquiry Dispatch Payload</h3>
            {createdRequest ? (
              <div>
                <div style={{ padding: "1rem", backgroundColor: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: "6px", color: "#166534", marginBottom: "1rem" }}>
                  <div style={{ fontWeight: "700" }}>✓ Verification Request Active</div>
                  <div style={{ fontSize: "0.8125rem", marginTop: "0.25rem" }}>ID: {createdRequest.id}</div>
                  <div style={{ fontSize: "0.8125rem" }}>Status: {createdRequest.status}</div>
                </div>

                <div style={{ backgroundColor: "#f8fafc", padding: "1rem", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
                  <div style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: "600", marginBottom: "0.25rem" }}>DEEP LINK / QR MANIFEST</div>
                  <code style={{ fontSize: "0.75rem", wordBreak: "break-all", color: "#0f172a" }}>
                    digilocker://verify?req={createdRequest.id}&purpose={encodeURIComponent(purpose)}
                  </code>
                </div>
              </div>
            ) : (
              <div style={{ padding: "3rem 1rem", textAlign: "center", color: "#94a3b8" }}>
                Configure policy parameters and click create to generate an active verification inquiry.
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Token Introspector View */
        <div style={{ backgroundColor: "#ffffff", border: "1px solid #e2e8f0", borderRadius: "8px", padding: "1.5rem" }}>
          <h2 style={{ fontSize: "1.125rem", fontWeight: "700", margin: "0 0 1rem 0" }}>Cryptographic Proof Token Introspector</h2>
          <form onSubmit={handleIntrospectToken} style={{ marginBottom: "1.5rem" }}>
            <div style={{ marginBottom: "1rem" }}>
              <label style={{ display: "block", fontSize: "0.8125rem", fontWeight: "600", color: "#334155", marginBottom: "0.35rem" }}>
                Target Audience (Relying Party ID)
              </label>
              <input
                type="text"
                value={audienceInput}
                onChange={(e) => setAudienceInput(e.target.value)}
                style={{ width: "100%", padding: "0.625rem", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.875rem" }}
              />
            </div>
            <div style={{ marginBottom: "1rem" }}>
              <label style={{ display: "block", fontSize: "0.8125rem", fontWeight: "600", color: "#334155", marginBottom: "0.35rem" }}>
                Encoded JWS Proof Token
              </label>
              <textarea
                value={tokenInput}
                onChange={(e) => setTokenInput(e.target.value)}
                placeholder="eyJhbGciOiJFZERTQSI..."
                rows={4}
                style={{ width: "100%", padding: "0.625rem", borderRadius: "6px", border: "1px solid #cbd5e1", fontFamily: "monospace", fontSize: "0.8125rem" }}
              />
            </div>
            <button
              type="submit"
              disabled={loading || !tokenInput}
              style={{ padding: "0.75rem 1.5rem", backgroundColor: "#2563eb", color: "#ffffff", border: "none", borderRadius: "6px", fontWeight: "600", cursor: "pointer", fontSize: "0.875rem" }}
            >
              {loading ? "Validating..." : "Validate Asymmetric Cryptographic Signature"}
            </button>
          </form>

          {introspectionResult && (
            <div style={{ padding: "1.25rem", backgroundColor: introspectionResult.active ? "#f0fdf4" : "#fef2f2", border: introspectionResult.active ? "1px solid #bbf7d0" : "1px solid #fecaca", borderRadius: "8px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontWeight: "700", color: introspectionResult.active ? "#166534" : "#991b1b" }}>
                  {introspectionResult.active ? "✓ TRUSTED PROOF TOKEN" : "✕ INVALID / EXPIRED TOKEN"}
                </span>
                <span style={{ fontSize: "0.8125rem", fontWeight: "600", color: "#475569" }}>
                  Alg: {introspectionResult.algorithm} • Key: {introspectionResult.keyId}
                </span>
              </div>
              <pre style={{ marginTop: "1rem", backgroundColor: "#ffffff", padding: "1rem", borderRadius: "6px", border: "1px solid #e2e8f0", fontSize: "0.8125rem", overflowX: "auto" }}>
                {JSON.stringify(introspectionResult, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
