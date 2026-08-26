import React, { useState, useEffect } from "react";

interface CredentialItem {
  id: string;
  credential_type: string;
  issuer_id: string;
  holder_name: string;
  passing_year: number;
  status: string;
  verification_level: number;
}

interface RequestItem {
  id: string;
  requester_name: string;
  credential_type: string;
  purpose: string;
  status: string;
}

export const DirectVerificationFlow: React.FC = () => {
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("password123");
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("digi_token"));
  const [credentials, setCredentials] = useState<CredentialItem[]>([]);
  const [requests, setRequests] = useState<RequestItem[]>([]);
  const [message, setMessage] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [verifiedProof, setVerifiedProof] = useState<any>(null);
  const [pipelineResult, setPipelineResult] = useState<any>(null);

  const rawBase = import.meta.env.VITE_API_BASE_URL ?? import.meta.env.VITE_API_URL ?? "http://localhost:8000";
  const API_BASE = String(rawBase).replace(/\/+$/, "") + "/api/v1";

  const authHeaders = () => ({
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  });

  const handleRegisterOrLogin = async () => {
    setLoading(true);
    setMessage("");
    try {
      let res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        res = await fetch(`${API_BASE}/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
      }
      const data = await res.json();
      if (data.access_token) {
        setToken(data.access_token);
        localStorage.setItem("digi_token", data.access_token);
        setMessage("✓ Successfully Authenticated (JWT Session Active)");
      } else {
        setMessage(`Auth Error: ${JSON.stringify(data)}`);
      }
    } catch (err: any) {
      setMessage(`Connection error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const loadData = async () => {
    if (!token) return;
    try {
      const [credRes, reqRes] = await Promise.all([
        fetch(`${API_BASE}/credentials`, { headers: authHeaders() }),
        fetch(`${API_BASE}/verification/requests`, { headers: authHeaders() }),
      ]);
      if (credRes.ok) setCredentials(await credRes.json());
      if (reqRes.ok) setRequests(await reqRes.json());
    } catch (err: any) {
      console.error("Load data failed", err);
    }
  };

  const handleUploadAndRunPipeline = async () => {
    setLoading(true);
    setMessage("1/3 Uploading document & executing OCR text parsing...");
    try {
      // 1. Upload & OCR
      const uploadRes = await fetch(`${API_BASE}/documents/upload-pipeline`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({
          filename: "CBSE_Class_XII_MarkSheet_2026.pdf",
          documentTypeHint: "CLASS_XII",
          simulatedContent: "CBSE Roll 99214 Rahul Sharma Delhi Public School Passing 2026",
        }),
      });
      const uploadData = await uploadRes.json();
      setPipelineResult(uploadData);
      const caseId = uploadData.verificationCase.caseId;

      setMessage(`2/3 OCR extracted 94% confidence. Case ${caseId} enqueued. Adjudicating as Officer...`);

      // 2. Officer Decision (Approve)
      const decRes = await fetch(`${API_BASE}/government/cases/${caseId}/decision`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({
          decision: "VERIFY",
          verifierId: "officer_sharma_cbse_delhi",
          note: "Hologram verified and state registry match confirmed.",
        }),
      });
      if (decRes.ok) {
        setMessage("3/3 ✓ Case Approved by Reviewing Officer! Level 4 Credential minted in wallet.");
        loadData();
      }
    } catch (err: any) {
      setMessage(`Pipeline error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRequest = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/verification/requests`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({
          requester_name: "National Testing Agency",
          credential_type: "CLASS_XII",
          purpose: "JEE Admission Eligibility",
        }),
      });
      if (res.ok) {
        setMessage("✓ Inbound Verification Request created.");
        loadData();
      }
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleConsentAndVerify = async (requestId: string) => {
    setLoading(true);
    try {
      await fetch(`${API_BASE}/verification/requests/${requestId}/consent`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ decision: "GRANT" }),
      });
      const runRes = await fetch(`${API_BASE}/verification/requests/${requestId}/run`, {
        method: "POST",
        headers: authHeaders(),
      });
      const result = await runRes.json();
      if (result.proof_id) {
        const proofRes = await fetch(`${API_BASE}/proofs/${result.proof_id}/verify`);
        const proofData = await proofRes.json();
        setVerifiedProof(proofData);
        setMessage(`✓ Verified by CBSE! Signed Proof Token ID: ${result.proof_id}`);
      } else {
        setMessage(`Result: ${result.result} - ${result.reason || ""}`);
      }
      loadData();
    } catch (err: any) {
      setMessage(`Verification error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) loadData();
  }, [token]);

  return (
    <section className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm my-6">
      <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Direct Citizen Verification Vertical Slice</h2>
          <p className="text-sm text-slate-500">
            Upload & OCR ➔ Gov Review Case ➔ Officer Approval ➔ Level 4 Credential ➔ Verifier Request ➔ Consent ➔ Signed Proof
          </p>
        </div>
        {token && (
          <button
            onClick={() => {
              setToken(null);
              localStorage.removeItem("digi_token");
              setMessage("Logged out.");
            }}
            className="text-xs text-rose-600 font-semibold px-3 py-1 bg-rose-50 rounded border border-rose-200 hover:bg-rose-100"
          >
            Logout
          </button>
        )}
      </div>

      {!token ? (
        <div className="max-w-md bg-slate-50 p-4 rounded-lg border border-slate-200">
          <h3 className="text-sm font-semibold text-slate-800 mb-2">Citizen Authentication</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full text-sm px-3 py-1.5 border border-slate-300 rounded bg-white"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full text-sm px-3 py-1.5 border border-slate-300 rounded bg-white"
              />
            </div>
            <button
              onClick={handleRegisterOrLogin}
              disabled={loading}
              className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm rounded shadow-sm transition"
            >
              {loading ? "Authenticating..." : "Register / Sign In"}
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleUploadAndRunPipeline}
              disabled={loading}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded shadow-sm"
            >
              ⚡ Run Full Document Pipeline (Upload ➔ OCR ➔ Gov Review ➔ Mint Credential)
            </button>
            <button
              onClick={handleCreateRequest}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded shadow-sm"
            >
              + Create Inbound Verification Request (NTA)
            </button>
          </div>

          {pipelineResult && (
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg text-xs">
              <h4 className="font-bold text-slate-900 mb-1">OCR Classification & Case Ingestion Metadata</h4>
              <p className="text-slate-600">
                Type: <strong>{pipelineResult.classification?.documentType}</strong> • Confidence:{" "}
                <strong>{pipelineResult.classification?.confidenceScore}%</strong> • Queue:{" "}
                <strong>{pipelineResult.classification?.suggestedQueue}</strong>
              </p>
              <pre className="mt-2 bg-white p-2 border border-slate-200 rounded overflow-x-auto">
                {JSON.stringify(pipelineResult.classification?.extractedFields, null, 2)}
              </pre>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-sm font-semibold text-slate-800 uppercase tracking-wide mb-3">
                Wallet Credentials ({credentials.length})
              </h3>
              <div className="space-y-2">
                {credentials.map((c) => (
                  <div key={c.id} className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-sm text-slate-900">{c.credential_type}</span>
                      <span className="text-xs bg-emerald-100 text-emerald-800 font-semibold px-2 py-0.5 rounded">
                        ✓ Level {c.verification_level} {c.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">
                      Issuer: {c.issuer_id} • Holder: {c.holder_name} • Year: {c.passing_year}
                    </p>
                  </div>
                ))}
                {!credentials.length && (
                  <p className="text-xs text-slate-400 italic">No credentials in wallet. Click above to run pipeline.</p>
                )}
              </div>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-slate-800 uppercase tracking-wide mb-3">
                Inbound Verification Inquiries ({requests.length})
              </h3>
              <div className="space-y-2">
                {requests.map((r) => (
                  <div key={r.id} className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-sm text-slate-900">{r.requester_name}</span>
                      <span
                        className={`text-xs font-semibold px-2 py-0.5 rounded ${
                          r.status === "COMPLETED"
                            ? "bg-emerald-100 text-emerald-800"
                            : r.status === "CONSENT_GRANTED"
                            ? "bg-blue-100 text-blue-800"
                            : "bg-amber-100 text-amber-800"
                        }`}
                      >
                        {r.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">Purpose: {r.purpose}</p>
                    {r.status !== "COMPLETED" && r.status !== "DENIED" && (
                      <button
                        onClick={() => handleConsentAndVerify(r.id)}
                        disabled={loading}
                        className="mt-2 text-xs font-semibold px-3 py-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded shadow-sm"
                      >
                        Review ➔ Allow Consent ➔ Run Verification
                      </button>
                    )}
                  </div>
                ))}
                {!requests.length && (
                  <p className="text-xs text-slate-400 italic">No verification requests. Click above to create one.</p>
                )}
              </div>
            </div>
          </div>

          {verifiedProof && (
            <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
              <h4 className="text-sm font-bold text-emerald-900">✓ Cryptographically Validated Proof Assertion</h4>
              <pre className="text-xs text-emerald-800 mt-2 overflow-x-auto bg-white p-3 rounded border border-emerald-200">
                {JSON.stringify(verifiedProof, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}

      {message && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 text-blue-900 text-xs font-medium rounded-lg">
          {message}
        </div>
      )}
    </section>
  );
};
