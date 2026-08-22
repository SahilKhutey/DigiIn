"""DigiIn modular-monolith API entry point."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.domain.models import ConsentPreview, DocumentOption, IssuerHealth, ScenarioSummary, TransactionDiagnosis
from app.services.catalogue import get_document, search_documents
from app.services.recovery import get_diagnosis, list_scenarios
from app.services.trust import consent_preview, issuer_health

app = FastAPI(title="DigiIn Prototype API", version="0.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "digiin-api", "mode": "synthetic-prototype"}


@app.get("/api/v1/documents", response_model=list[DocumentOption])
def list_documents(q: str = Query(default="", max_length=80)) -> list[DocumentOption]:
    """Intent-first search over the safe mock catalogue."""
    return search_documents(q)


@app.get("/api/v1/documents/{document_id}", response_model=DocumentOption)
def read_document(document_id: str) -> DocumentOption:
    document = get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document type not found")
    return document


@app.get("/api/v1/scenarios", response_model=list[ScenarioSummary])
def scenarios() -> list[ScenarioSummary]:
    return list_scenarios()


@app.get("/api/v1/transactions/{transaction_id}/diagnosis", response_model=TransactionDiagnosis)
def transaction_diagnosis(transaction_id: str) -> TransactionDiagnosis:
    diagnosis = get_diagnosis(transaction_id)
    if diagnosis is None:
        raise HTTPException(status_code=404, detail="Transaction diagnosis not found")
    return diagnosis


@app.get("/api/v1/diagnostics/{scenario_id}", response_model=TransactionDiagnosis, deprecated=True)
def legacy_diagnostic(scenario_id: str) -> TransactionDiagnosis:
    """Compatibility route; use the transaction diagnosis endpoint for new clients."""
    return transaction_diagnosis(scenario_id)


@app.post("/api/v1/transactions/{transaction_id}/retry", response_model=TransactionDiagnosis)
def targeted_retry(transaction_id: str) -> TransactionDiagnosis:
    """Prototype-only targeted retry; no external system is contacted."""
    return transaction_diagnosis(transaction_id)


@app.post("/api/v1/diagnostics/{scenario_id}/retry", response_model=TransactionDiagnosis, deprecated=True)
def legacy_retry(scenario_id: str) -> TransactionDiagnosis:
    return targeted_retry(scenario_id)


@app.get("/api/v1/issuers/health", response_model=list[IssuerHealth])
def list_issuer_health() -> list[IssuerHealth]:
    return issuer_health()


@app.get("/api/v1/consents/preview", response_model=ConsentPreview)
def get_consent_preview() -> ConsentPreview:
    return consent_preview()
