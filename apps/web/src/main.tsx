import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

type Stage = { name: string; status: "complete" | "attention" | "blocked" | "not_started"; message: string; owner: string; nextAction?: string };
type Recovery = { label: string; type: string; guidance: string };
type Diagnostic = { transactionId: string; documentLabel: string; trustLabel: string; overallStatus: "resolved" | "action_required" | "unavailable"; issueCode: string; issuerStatus: string; summary: string; steps: Stage[]; recovery: Recovery; fallbackAvailable: boolean; supportReference: string };
type Scenario = { id: string; title: string; description: string };
type DocumentOption = { id: string; label: string; category: string; trustLabel: string };

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
  const document = documents.find((item) => item.id === documentId) ?? documents[0];

  return <main>
    <header><p className="brand">DigiIn <span>• Document reliability layer</span></p><a href="#privacy">Privacy first</a></header>
    <section className="hero"><p className="eyebrow">DOCUMENT RECOVERY</p><h1>Get your document successfully — or know exactly what to do next.</h1><p>DigiIn identifies the failed step across identity, issuer, document and destination systems without taking over official accounts.</p></section>
    <section className="notice" role="status">{notice}</section>
    <section className="intent scenario-picker" aria-labelledby="intent-title"><div><p className="eyebrow">1. START WITH THE OUTCOME</p><h2 id="intent-title">What document do you need?</h2></div><label>Document type<select value={documentId} onChange={(event) => setDocumentId(event.target.value)}>{documents.map((item) => <option key={item.id} value={item.id}>{item.label} — {item.category}</option>)}</select></label><div className="trust"><strong>{document?.trustLabel}</strong><span>Trust label: this prototype never treats a user-uploaded file as an official issued record.</span></div></section>
    <section className="scenario-picker" aria-labelledby="scenario-title"><div><p className="eyebrow">2. DIAGNOSE THE JOURNEY</p><h2 id="scenario-title">What happened?</h2></div><label>Fictional diagnostic case<select value={scenarioId} onChange={(event) => setScenarioId(event.target.value)}>{scenarios.map((scenario) => <option key={scenario.id} value={scenario.id}>{scenario.title}</option>)}</select></label><p>{scenarios.find((scenario) => scenario.id === scenarioId)?.description}</p></section>
    <section className="card" aria-labelledby="journey-title"><div className="card-heading"><div><p className="eyebrow">3. DOCUMENT HEALTH</p><h2 id="journey-title">{diagnostic.documentLabel}</h2></div><span className={`badge ${diagnostic.overallStatus}`}>{diagnostic.overallStatus.replace("_", " ")}</span></div><div className="health-grid"><p><strong>Trust</strong><span>{diagnostic.trustLabel}</span></p><p><strong>Issuer status</strong><span className={diagnostic.issuerStatus}>{diagnostic.issuerStatus}</span></p><p><strong>Diagnostic code</strong><span>{diagnostic.issueCode}</span></p></div><p className="summary">{diagnostic.summary}</p><ol className="timeline">{diagnostic.steps.map((item) => <li key={item.name} className={item.status}><div className="marker" aria-hidden="true">{item.status === "complete" ? "✓" : item.status === "attention" ? "!" : item.status === "blocked" ? "×" : "•"}</div><article><div className="stage-title"><h3>{item.name}</h3><span>{item.owner}</span></div><p>{item.message}</p>{item.nextAction && <div className="next"><strong>What you can do now</strong><p>{item.nextAction}</p></div>}</article></li>)}</ol><div className="recovery"><p className="eyebrow">RECOVERY ACTION</p><h3>{diagnostic.recovery.label}</h3><p>{diagnostic.recovery.guidance}</p>{diagnostic.fallbackAvailable && <p className="fallback">An authorised official fallback route is available in a production integration.</p>}<button type="button" onClick={retry} disabled={diagnostic.overallStatus === "resolved"}>Try targeted demo retry</button><button className="secondary" type="button" onClick={copyEvidence}>Copy support reference</button><p className="reference">Support reference: <code>{diagnostic.supportReference}</code></p></div></section>
    <section id="privacy" className="privacy"><h2>Your information stays yours.</h2><p>Use official services for identity verification. This recovery layer holds only privacy-minimised transaction evidence in a future authorised deployment.</p></section>
  </main>;
}

createRoot(document.getElementById("root")!).render(<App />);
