from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db import get_db
from app.domain.models import (
    EvidenceComparisonDetail,
    GovernmentReviewDecision,
    VerificationCase,
    VerifierQueueId,
    VerifierQueueSummary,
)
from app.models.entities import VerificationRequest
from app.services.platform import (
    decide_verification_case,
    get_case_evidence_comparison,
    list_verifier_cases,
    list_verifier_queues,
)

router = APIRouter(prefix="/government", tags=["government"])


@router.get("/review-queue")
def review_queue(user=Depends(require_role("OFFICER", "ADMIN", "CITIZEN")), db: Session = Depends(get_db)):
    return (
        db.query(VerificationRequest)
        .filter(VerificationRequest.status.in_(["PENDING_REVIEW", "PENDING_CONSENT", "OPEN"]))
        .order_by(VerificationRequest.created_at.asc())
        .all()
    )


@router.get("/queues", response_model=list[VerifierQueueSummary])
def get_queues():
    """Retrieve summary metrics across all departmental verifier review queues."""
    return list_verifier_queues()


@router.get("/cases", response_model=list[VerificationCase])
def get_cases(
    queue: VerifierQueueId | None = Query(default=None),
    status: str | None = Query(default=None),
):
    """Retrieve all verification discrepancy cases for review."""
    return list_verifier_cases(queue_id=queue, status=status)


@router.get("/cases/{case_id}/comparison", response_model=EvidenceComparisonDetail)
def get_case_comparison(case_id: str):
    """Side-by-side comparison of citizen OCR extracted claims vs official state registry records."""
    detail = get_case_evidence_comparison(case_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Verification case not found")
    return detail


@router.post("/cases/{case_id}/decision", response_model=VerificationCase)
def submit_case_decision(case_id: str, payload: GovernmentReviewDecision):
    """Submit officer adjudication decision (VERIFY, REJECT, REQUEST_MORE_EVIDENCE, TRANSFER)."""
    resolved = decide_verification_case(case_id, payload)
    if resolved is None:
        raise HTTPException(status_code=404, detail="Verification case not found")
    return resolved
