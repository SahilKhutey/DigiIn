"""
DigiIn Canonical Verification Gateway API Router.

Implements the authoritative, frozen Verification API endpoints:
- POST /api/v1/verification/requests
- GET  /api/v1/verification/requests/{request_id}
- POST /api/v1/verification/requests/{request_id}/consent
- POST /api/v1/verification/requests/{request_id}/revoke
- GET  /api/v1/verification/requests/{request_id}/result
- GET  /api/v1/verification/scopes
- POST /api/v1/verification/requests/{request_id}/run
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import current_user, get_optional_current_user
from app.core.ids import is_valid_account_id
from app.core.sandbox.mock_institution_registry import mock_institution_registry
from app.core.verification_layer import verification_layer
from app.db import get_db
from app.models.entities import User, VerificationRequest
from app.schemas.core import VerifyOut
from app.services.audit import audit
from app.services.verification import VerificationService

router = APIRouter(prefix="/verification", tags=["Canonical Verification Gateway"])


class CreateVerificationRequestPayload(BaseModel):
    # Canonical institution fields
    service_code: str | None = Field(None, description="Accredited service code (e.g. EDU-SCHOLARSHIP-DEMO)")
    institution_code: str | None = Field(None, description="Institution code (e.g. EDU-DEMO-001)")
    digiin_account_id: str | None = Field(None, description="Target citizen DigiIn Account ID (e.g. DI-7K4M-9Q2X-8P6R)")
    purpose: str | None = Field(None, description="Declared transaction purpose")
    scopes: list[str] | None = Field(None, description="Requested verification scopes")
    ttl_seconds: int = Field(900, description="Request validity window in seconds (default 15 mins)")

    # Legacy citizen fields
    requester_name: str | None = None
    credential_type: str | None = None
    required_level: int = 4
    callback_url: str | None = None


class ConsentDecisionPayload(BaseModel):
    decision: str = Field(..., description="'approved' / 'granted' / 'grant' or 'denied'")
    scopes: list[str] | None = Field(None, description="Optional approved scopes list")


@router.get("/scopes")
def list_verification_scopes() -> dict[str, Any]:
    """Lists standardized verification scopes."""
    return {
        "status": "success",
        "scopes": mock_institution_registry.list_scopes(),
    }


@router.post("/requests")
def create_verification_request_endpoint(
    payload: CreateVerificationRequestPayload,
    x_sandbox_service_key: str | None = Header(None, alias="X-Sandbox-Service-Key"),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_current_user),
) -> dict[str, Any]:
    """Creates a formal verification transaction bound to citizen's DigiIn Account ID or legacy DB."""
    # 1. Check if this is a legacy DB verification request from an authenticated user
    if payload.credential_type is not None and user is not None:
        db_req = VerificationRequest(
            user_id=user.id,
            requester_name=payload.requester_name or "National Authority",
            credential_type=payload.credential_type,
            purpose=payload.purpose or "Eligibility verification",
        )
        db.add(db_req)
        db.commit()
        db.refresh(db_req)
        audit(db, user.id, "VERIFICATION_REQUEST_CREATED", "verification_request", db_req.id)
        return {
            "id": db_req.id,
            "user_id": db_req.user_id,
            "requester_name": db_req.requester_name,
            "credential_type": db_req.credential_type,
            "purpose": db_req.purpose,
            "required_level": payload.required_level,
            "callback_url": payload.callback_url,
            "status": db_req.status,
            "created_at": db_req.created_at.isoformat() if hasattr(db_req.created_at, "isoformat") else str(db_req.created_at),
            "request_id": db_req.id,
        }

    # 2. Canonical Institutional Verification Layer flow
    if not payload.digiin_account_id or not is_valid_account_id(payload.digiin_account_id):
        raise HTTPException(status_code=400, detail=f"Invalid DigiIn Account ID: {payload.digiin_account_id}")

    if not payload.scopes:
        raise HTTPException(status_code=400, detail="Requested scopes list cannot be empty.")

    cleaned_scopes = sorted(list(set(payload.scopes)))
    inst_code = payload.institution_code or "EDU-DEMO-001"
    if payload.service_code:
        srv = mock_institution_registry.get_service(payload.service_code)
        if srv:
            inst_code = srv.institution_code

    inst = mock_institution_registry.get_institution(inst_code)
    if not inst:
        raise HTTPException(status_code=404, detail=f"Institution '{inst_code}' not found.")

    is_valid, unauthorized = mock_institution_registry.validate_service_scope(
        inst_code, cleaned_scopes, payload.service_code
    )
    if not is_valid:
        raise HTTPException(
            status_code=403,
            detail=f"UNAUTHORIZED_SCOPE: Institution '{inst_code}' is not accredited for scopes: {unauthorized}",
        )

    service_display = inst.display_name if inst else inst_code
    req = verification_layer.create_request(
        digiin_account_id=payload.digiin_account_id,
        requesting_service_id=inst_code,
        service_name=service_display,
        purpose=payload.purpose or "Verification Request",
        requested_attributes=cleaned_scopes,
        ttl_seconds=payload.ttl_seconds,
    )

    return {
        "status": "PENDING_CONSENT",
        "request_id": req["request_reference"],
        "request_reference": req["request_reference"],
        "digiin_account_id": payload.digiin_account_id,
        "purpose": payload.purpose,
        "scopes": cleaned_scopes,
        "expires_at": req["expires_at"],
    }


@router.get("/requests/{request_id}")
def get_verification_request(request_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Retrieves verification request details for citizen review or status checking."""
    req = verification_layer.get_request(request_id)
    if req:
        return {
            "status": "success",
            "request": req,
        }

    db_req = db.get(VerificationRequest, request_id)
    if db_req:
        return {
            "id": db_req.id,
            "status": db_req.status,
            "requester_name": db_req.requester_name,
            "credential_type": db_req.credential_type,
            "purpose": db_req.purpose,
        }

    raise HTTPException(status_code=404, detail=f"Verification request '{request_id}' not found.")


@router.post("/requests/{request_id}/consent")
def submit_citizen_consent(
    request_id: str,
    payload: ConsentDecisionPayload,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_current_user),
) -> dict[str, Any]:
    """Citizen approves or denies an incoming verification request."""
    # Check Verification Layer
    req = verification_layer.get_request(request_id)
    if req:
        decision_clean = "GRANTED" if payload.decision.lower() in ("approved", "granted", "grant") else "DENIED"
        try:
            updated_req = verification_layer.submit_consent(request_id, decision=decision_clean)
            return {
                "status": "CONSENT_GRANTED" if decision_clean == "GRANTED" else "CONSENT_DENIED",
                "request_id": request_id,
                "decision": decision_clean,
                "verification_status": updated_req["status"],
                "consent_status": updated_req["consent_status"],
                "verification_result": updated_req.get("result"),
            }
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Check DB VerificationRequest
    db_req = db.get(VerificationRequest, request_id)
    if db_req:
        user_id = user.id if user else db_req.user_id
        VerificationService(db).set_consent(db_req, user_id, payload.decision)
        return {"status": db_req.status}

    raise HTTPException(status_code=404, detail=f"Verification request '{request_id}' not found.")


@router.post("/requests/{request_id}/revoke")
def revoke_citizen_consent(request_id: str) -> dict[str, Any]:
    """Citizen unilaterally revokes previously approved verification access."""
    try:
        updated_req = verification_layer.revoke_consent(request_id)
        return {
            "status": "success",
            "request_id": request_id,
            "verification_status": updated_req["status"],
            "consent_status": updated_req["consent_status"],
            "message": "Consent successfully revoked.",
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/requests/{request_id}/result")
def get_verification_result(request_id: str) -> dict[str, Any]:
    """Retrieves the verified assertion result once consent has been granted."""
    req = verification_layer.get_request(request_id)
    if not req:
        raise HTTPException(status_code=404, detail=f"Verification request '{request_id}' not found.")

    if req["status"] != "VERIFIED":
        return {
            "status": req["status"],
            "request_id": request_id,
            "verification_status": req["status"],
            "message": f"Verification is not finalized. Current status: {req['status']}",
        }

    return {
        "status": "VERIFIED",
        "request_id": request_id,
        "verification_status": "VERIFIED",
        "digiin_account_id": req["digiin_account_id"],
        "verification": req["result"],
    }


@router.post("/requests/{request_id}/run", response_model=VerifyOut)
async def run_verification_endpoint(
    request_id: str,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    """Run verification pipeline for DB credential requests."""
    db_req = db.get(VerificationRequest, request_id)
    if not db_req or db_req.user_id != user.id:
        raise HTTPException(status_code=404, detail="Request not found")
    try:
        result, proof = await VerificationService(db).verify(db_req, user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return VerifyOut(
        result=result.result,
        verification_level=result.verification_level,
        reason=result.reason,
        proof_id=proof.id if proof else None,
    )
