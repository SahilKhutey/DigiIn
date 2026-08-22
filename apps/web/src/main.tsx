import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

type Stage = { name: string; status: "complete" | "attention" | "blocked" | "not_started"; message: string; owner: string; nextAction?: string };
type Recovery = { label: string; type: string; guidance: string };
type Diagnostic = { transactionId: string; documentLabel: string; trustLabel: string; overallStatus: "resolved" | "action_required" | "unavailable"; issueCode: string; issuerStatus: string; summary: string; steps: Stage[]; recovery: Recovery; fallbackAvailable: boolean; supportReference: string };
type Scenario = { id: string; title: string; description: string };
type DocumentOption = { id: string; label: string; category: string; trustLabel: string };
type VerificationRequest = { requestId: string; requesterName: string; purpose: string; audience: string; consentText: string; status: string; expiresAt: string; requirements: { credential: string; minimumLevel: number; attributes: string[] }[]; disclosure: { mode: string } };
type VerificationResult = { verificationId: string; status: string; audience: string; purpose: string; disclosureLevel: string; results: { credential: string; verified: boolean; status: string; issuer?: string; level: number; disclosedAttributes: Record<string, string | number | boolean>; message: string }[]; proof: { token: string; algorithm: string }; receipt: { requesterName: string; purpose: string; shared: string[]; documentShared: boolean; issuedAt: string; expiresAt: string } };
type TokenCheck = { active: boolean; status: string; message: string; verificationId?: string };
type PlatformEvent = { eventId: string; type: string; aggregateId: string; actor: string; message: string; createdAt: string };
type PlatformSnapshot = { featureFlags: { key: string; enabled: boolean; description: string }[]; mockIntegrations: { integrationId: string; name: string; status: string; supportedCredentials: string[] }[]; documents: unknown[]; verificationCases: unknown[]; transactions: unknown[]; events: PlatformEvent[] };
type StudentDemo = { document: { documentId: string; documentType: string; status: string; authenticity: string; verificationLevel: number }; verificationCase: { caseId: string; status: string; claimedIssuer: string; automatedMatchScore: number }; transaction: { transactionId: string; currentStage: string; state: string }; proofResult: VerificationResult; events: PlatformEvent[] };

const localScenarios: Scenario[] = [
  { id: "identity-mismatch", title: "Identity details do not match", description: "An education record cannot be matched to the supplied details." },
  { id: "issuer-unavailable", title: "Issuer service is unavailable", description: "The document issuer cannot respond right now." },
  { id: "callback-failed", title: "Requesting portal did not receive confirmation", description: "The handoff to another service did not complete." },
  { id: "resolved", title: "Document journey completed", description: "A successful issued-document journey." },
];
const localDocuments: DocumentOption[] = [{ id: "marksheet", label: "Class XII marksheet", category: "Education", trustLabel: "Government issued" }];
const fallback: Diagnostic = { transactionId: "demo-cbse-2026", documentLabel: "Class XII marksheet (demonstration)", trustLabel: "Government issued", overallStatus: "action_required", issueCode: "IDENTITY_MISMATCH", issuerStatus: "available", summary: "The issuer responded, but its record could not be matched.", recovery: { label: "Correct the issuer record", type: "correct_record", guidance: "Confirm the education record with the issuer, then begin a new official retrieval attempt." }, fallbackAvailable: false, supportReference: "DIGIIN-DEMO-IM-2026", steps: [{ name: "Account access", status: "complete", message: "The official sign-in step was completed.", owner: "Citizen / official service" }, { name: "Identity match", status: "attention", message: "The issuer could not match the details supplied for this request.", owner: "Issuing organisation", nextAction: "Check your name, date of birth and document year against the issuer record." }] };

function App() {
  const api = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
  const [scenarios, setScenarios] = useState(localScenarios);
  const [documents, setDocuments] = useState(localDocuments);
  const [scenarioId, setScenarioId] = useState("identity-mismatch");
  const [documentId, setDocumentId] = useState("marksheet");
  const [diagnostic, setDiagnostic] = useState(fallback);
  const [verificationRequest, setVerificationRequest] = useState<VerificationRequest | null>(null);
  const [verificationResult, setVerificationResult] = useState<VerificationResult | null>(null);
  const [tokenCheck, setTokenCheck] = useState<TokenCheck | null>(null);
  const [platformSnapshot, setPlatformSnapshot] = useState<PlatformSnapshot | null>(null);
  const [studentDemo, setStudentDemo] = useState<StudentDemo | null>(null);
  const [notice, setNotice] = useState("Demonstration only. DigiIn never asks for an Aadhaar number, OTP, password or document upload.");

  useEffect(() => {
    Promise.all([fetch(`${api}/api/v1/scenarios`), fetch(`${api}/api/v1/documents`)])
      .then(async ([scenarioResponse, documentResponse]) => {
        if (!scenarioResponse.ok || !documentResponse.ok) throw new Error("Unavailable");
        setScenarios(await scenarioResponse.json());
        setDocuments(await documentResponse.json());
      })
      .catch(() => setNotice("Demo API is unavailable; local fictional data is shown. No personal data is involved."));
  }, [api]);

  useEffect(() => {
    fetch(`${api}/api/v1/transactions/${scenarioId}/diagnosis`).then((response) => response.ok ? response.json() : Promise.reject()).then(setDiagnostic).catch(() => setDiagnostic(fallback));
  }, [api, scenarioId]);

  useEffect(() => {
    fetch(`${api}/api/v1/platform/snapshot`)
      .then((response) => response.ok ? response.json() : Promise.reject())
      .then(setPlatformSnapshot)
      .catch(() => undefined);
  }, [api]);

  const retry = () => {
    fetch(`${api}/api/v1/transactions/${scenarioId}/retry`, { method: "POST" })
      .then((response) => response.ok ? response.json() : Promise.reject())
      .then((result) => { setDiagnostic(result); setNotice("Targeted demo retry completed. No external government service was contacted."); })
      .catch(() => setNotice("This example can only be retried when the demo API is running."));
  };
  const copyEvidence = async () => {
    const evidence = `DigiIn support reference: ${diagnostic.supportReference}\nIssue: ${diagnostic.issueCode}\nTransaction: ${diagnostic.transactionId}`;
    try { await navigator.clipboard.writeText(evidence); setNotice("Support-safe reference copied. It contains no personal information."); }
    catch { setNotice(`Support reference: ${diagnostic.supportReference}`); }
  };
  const createVerificationRequest = () => {
    fetch(`${api}/api/v1/verification/request/demo-exam`, { method: "POST" })
      .then((response) => response.ok ? response.json() : Promise.reject())
      .then((request) => {
        setVerificationRequest(request);
        setVerificationResult(null);
        setTokenCheck(null);
        setNotice("Demo examination portal request created. Review the consent details before authorising.");
      })
      .catch(() => setNotice("Verification gateway demo is available when the API is running."));
  };
  const authorizeVerification = () => {
    if (!verificationRequest) return;
    fetch(`${api}/api/v1/verification/request/${verificationRequest.requestId}/authorize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ allow: true }),
    })
      .then((response) => response.ok ? response.json() : Promise.reject())
      .then((result) => {
        setVerificationResult(result);
        setNotice("Purpose-bound proof generated. No raw document was shared.");
      })
      .catch(() => setNotice("The demo request could not be authorised."));
  };
  const introspectProof = () => {
    if (!verificationResult) return;
    fetch(`${api}/api/v1/verification/introspect`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: verificationResult.proof.token, audience: verificationResult.audience }),
    })
      .then((response) => response.ok ? response.json() : Promise.reject())
      .then((result) => {
        setTokenCheck(result);
        setNotice(result.active ? "Requester validated a trusted proof token." : "Requester could not validate the proof token.");
      })
      .catch(() => setNotice("The demo proof token could not be checked."));
  };
  const runStudentDemo = () => {
    fetch(`${api}/api/v1/platform/demo/student`, { method: "POST" })
      .then((response) => response.ok ? response.json() : Promise.reject())
      .then((result) => {
        setStudentDemo(result);
        setVerificationResult(result.proofResult);
        setTokenCheck(null);
        setNotice("Student vertical slice completed: upload, classify, verify, approve, generate proof.");
        return fetch(`${api}/api/v1/platform/snapshot`);
      })
      .then((response) => response && response.ok ? response.json() : Promise.reject())
      .then(setPlatformSnapshot)
      .catch(() => setNotice("The full platform demo is available when the API is running."));
  };
  const document = documents.find((item) => item.id === documentId) ?? documents[0];

  return <main>
    <header><p className="brand">DigiIn <span>• Document trust platform</span></p><nav><a href="#proof">Verify proof</a><a href="#recovery">Recover</a><a href="#privacy">Privacy first</a></nav></header>
    <section className="hero"><p className="eyebrow">VERIFY ONCE. PROVE ANYWHERE.</p><h1>Government portals should request verified claims, not copies of documents.</h1><p>DigiIn demonstrates purpose-bound credential proofs, citizen consent, document recovery and privacy-minimised receipts with synthetic data.</p></section>
    <section className="notice" role="status">{notice}</section>
    <section className="card platform-card" aria-labelledby="platform-title"><div className="card-heading"><div><p className="eyebrow">RUNNABLE PRODUCT PLATFORM</p><h2 id="platform-title">Student document to verified proof</h2></div><span className="badge resolved">vertical slice</span></div><p className="summary">This demo runs the canonical MVP path through API, domain state, transaction, mock government review, audit events, and proof generation.</p><button type="button" onClick={runStudentDemo}>Run student vertical slice</button>{platformSnapshot && <div className="platform-grid"><p><strong>Feature flags</strong><span>{platformSnapshot.featureFlags.filter((flag) => flag.enabled).length} enabled</span></p><p><strong>Mock integrations</strong><span>{platformSnapshot.mockIntegrations.length} configured</span></p><p><strong>Transactions</strong><span>{platformSnapshot.transactions.length}</span></p><p><strong>Audit events</strong><span>{platformSnapshot.events.length}</span></p></div>}{studentDemo && <section className="result-panel" aria-label="Student demo result"><div className="stage-title"><h3>{studentDemo.document.documentType} credential</h3><span>{studentDemo.document.status}</span></div><div className="health-grid"><p><strong>Document</strong><span>{studentDemo.document.documentId}</span></p><p><strong>Verifier</strong><span>{studentDemo.verificationCase.claimedIssuer}</span></p><p><strong>Proof</strong><span>{studentDemo.proofResult.status}</span></p></div><ol className="proof-results">{studentDemo.events.map((event) => <li key={event.eventId} className="complete"><strong>{event.type}</strong><span>{event.message}</span></li>)}</ol></section>}</section>
    <section id="proof" className="card proof-card" aria-labelledby="proof-title"><div className="card-heading"><div><p className="eyebrow">VERIFICATION GATEWAY</p><h2 id="proof-title">Prove eligibility without uploading documents</h2></div><span className="badge resolved">proof first</span></div><p className="summary">A requester asks a question such as “does this citizen meet the exam eligibility requirements?” DigiIn returns a signed proof result after consent, not the underlying certificates.</p><div className="proof-actions"><button type="button" onClick={createVerificationRequest}>Create exam proof request</button><button className="secondary" type="button" onClick={authorizeVerification} disabled={!verificationRequest || Boolean(verificationResult)}>Allow verification</button><button className="secondary" type="button" onClick={introspectProof} disabled={!verificationResult}>Validate proof token</button></div>{verificationRequest && <section className="consent-panel" aria-label="Consent request"><p className="eyebrow">CONSENT REQUEST</p><h3>{verificationRequest.requesterName}</h3><p>{verificationRequest.consentText}</p><div className="request-grid"><p><strong>Purpose</strong><span>{verificationRequest.purpose}</span></p><p><strong>Audience</strong><span>{verificationRequest.audience}</span></p><p><strong>Disclosure</strong><span>{verificationRequest.disclosure.mode}</span></p></div><ul className="requirement-list">{verificationRequest.requirements.map((item) => <li key={item.credential}><strong>{item.credential}</strong><span>Minimum level {item.minimumLevel}{item.attributes.length ? ` • ${item.attributes.join(", ")}` : ""}</span></li>)}</ul></section>}{verificationResult && <section className="result-panel" aria-label="Verification result"><div className="stage-title"><h3>Verification receipt</h3><span>{verificationResult.status}</span></div><div className="health-grid"><p><strong>Verification ID</strong><span>{verificationResult.verificationId}</span></p><p><strong>Shared</strong><span>{verificationResult.disclosureLevel}</span></p><p><strong>Document shared</strong><span>{verificationResult.receipt.documentShared ? "Yes" : "No"}</span></p></div><ol className="proof-results">{verificationResult.results.map((item) => <li key={item.credential} className={item.verified ? "complete" : "attention"}><strong>{item.credential}</strong><span>{item.status} • Level {item.level} • {item.issuer ?? "No issuer"}</span>{Object.keys(item.disclosedAttributes).length > 0 && <code>{JSON.stringify(item.disclosedAttributes)}</code>}</li>)}</ol><p className="token-preview"><strong>Signed proof token</strong><code>{verificationResult.proof.token.slice(0, 96)}...</code></p></section>}{tokenCheck && <section className={`token-check ${tokenCheck.active ? "valid" : "invalid"}`} role="status"><strong>{tokenCheck.status}</strong><p>{tokenCheck.message}</p></section>}</section>
    <section className="intent scenario-picker" aria-labelledby="intent-title"><div><p className="eyebrow">1. START WITH THE OUTCOME</p><h2 id="intent-title">What document do you need?</h2></div><label>Document type<select value={documentId} onChange={(event) => setDocumentId(event.target.value)}>{documents.map((item) => <option key={item.id} value={item.id}>{item.label} — {item.category}</option>)}</select></label><div className="trust"><strong>{document?.trustLabel}</strong><span>Trust label: this prototype never treats a user-uploaded file as an official issued record.</span></div></section>
    <section className="scenario-picker" aria-labelledby="scenario-title"><div><p className="eyebrow">2. DIAGNOSE THE JOURNEY</p><h2 id="scenario-title">What happened?</h2></div><label>Fictional diagnostic case<select value={scenarioId} onChange={(event) => setScenarioId(event.target.value)}>{scenarios.map((scenario) => <option key={scenario.id} value={scenario.id}>{scenario.title}</option>)}</select></label><p>{scenarios.find((scenario) => scenario.id === scenarioId)?.description}</p></section>
    <section id="recovery" className="card" aria-labelledby="journey-title"><div className="card-heading"><div><p className="eyebrow">3. DOCUMENT HEALTH</p><h2 id="journey-title">{diagnostic.documentLabel}</h2></div><span className={`badge ${diagnostic.overallStatus}`}>{diagnostic.overallStatus.replace("_", " ")}</span></div><div className="health-grid"><p><strong>Trust</strong><span>{diagnostic.trustLabel}</span></p><p><strong>Issuer status</strong><span className={diagnostic.issuerStatus}>{diagnostic.issuerStatus}</span></p><p><strong>Diagnostic code</strong><span>{diagnostic.issueCode}</span></p></div><p className="summary">{diagnostic.summary}</p><ol className="timeline">{diagnostic.steps.map((item) => <li key={item.name} className={item.status}><div className="marker" aria-hidden="true">{item.status === "complete" ? "OK" : item.status === "attention" ? "!" : item.status === "blocked" ? "X" : "·"}</div><article><div className="stage-title"><h3>{item.name}</h3><span>{item.owner}</span></div><p>{item.message}</p>{item.nextAction && <div className="next"><strong>What you can do now</strong><p>{item.nextAction}</p></div>}</article></li>)}</ol><div className="recovery"><p className="eyebrow">RECOVERY ACTION</p><h3>{diagnostic.recovery.label}</h3><p>{diagnostic.recovery.guidance}</p>{diagnostic.fallbackAvailable && <p className="fallback">An authorised official fallback route is available in a production integration.</p>}<button type="button" onClick={retry} disabled={diagnostic.overallStatus === "resolved"}>Try targeted demo retry</button><button className="secondary" type="button" onClick={copyEvidence}>Copy support reference</button><p className="reference">Support reference: <code>{diagnostic.supportReference}</code></p></div></section>
    <section id="privacy" className="privacy"><h2>Your information stays yours.</h2><p>Use official services for identity verification. This recovery layer holds only privacy-minimised transaction evidence in a future authorised deployment.</p></section>
  </main>;
}

createRoot(document.getElementById("root")!).render(<App />);
