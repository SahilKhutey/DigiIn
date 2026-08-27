from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db import get_db
from app.domain.models import DirectUploadPayload, PipelineUploadResponse
from app.models.entities import CorrectionCase, Credential, Notification, User, VerificationRequest
from app.schemas.core import (
    ConsentCreate,
    CorrectionCreate,
    CredentialCreate,
    CredentialOut,
    VerificationCreate,
    VerificationOut,
    VerifyOut,
)
from app.services.account_identity_service import account_identity_service
from app.services.audit import audit
from app.services.platform import upload_and_classify_pipeline
from app.services.verification import VerificationService

router = APIRouter(prefix="", tags=["citizen"])


@router.get("/me")
def me(user: User = Depends(current_user)):
    return {
        "id": user.id,
        "digiin_account_id": getattr(user, "digiin_account_id", "DI-7K4M-9Q2X-8P6R"),
        "email": user.email,
        "role": user.role,
        "status": user.status,
    }


@router.get("/me/identity")
def get_my_identity(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Phase 2: Returns authenticated citizen's central public identity representation."""
    acc_id = getattr(user, "digiin_account_id", "DI-7K4M-9Q2X-8P6R")
    identity_info = account_identity_service.get_public_identity(db, acc_id, authenticated_actor=user)
    if not identity_info:
        return {
            "digiin_account_id": acc_id,
            "account_status": user.status.lower(),
            "identity_status": "active",
        }
    return identity_info


@router.get("/accounts/{digiin_account_id}")
def lookup_account_identity(
    digiin_account_id: str,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    """Phase 2: Controlled public account identity lookup with anti-enumeration protection."""
    if not account_identity_service.validate_id(digiin_account_id):
        raise HTTPException(
            status_code=400,
            detail="INVALID_ID: Enter a valid DigiIn Account ID in DI-XXXX-XXXX-XXXX format.",
        )

    info = account_identity_service.get_public_identity(db, digiin_account_id, authenticated_actor=user)
    if not info:
        # Uniform 404 response to prevent oracle timing discovery
        raise HTTPException(
            status_code=404,
            detail="ACCOUNT_NOT_FOUND: The requested DigiIn Account ID does not exist or is inactive.",
        )
    return info


@router.post("/credentials", response_model=CredentialOut)
def create_credential(payload: CredentialCreate, user=Depends(current_user), db: Session = Depends(get_db)):
    credential = Credential(user_id=user.id, **payload.model_dump())
    db.add(credential)
    db.commit()
    db.refresh(credential)
    audit(db, user.id, "CREDENTIAL_CREATED", "credential", credential.id)
    return credential


@router.get("/credentials")
def credentials(account_id: str | None = None, user=Depends(current_user), db: Session = Depends(get_db)):
    if account_id:
        import app.db.repository as repo
        from app.domain.credential_models import CredentialResponse, VerifiedClaimSchema
        creds = repo.list_credentials_for_account(account_id)
        return [
            CredentialResponse(
                credential_id=c.credential_id,
                account_id=c.account_id,
                credential_type=c.credential_type,
                issuer=c.issuer,
                claims=[
                    VerifiedClaimSchema(
                        claim_type=cl.claim_type,
                        value=cl.value,
                        source=cl.source,
                        verification_level=cl.verification_level,
                        verified_at=cl.verified_at,
                    )
                    for cl in c.claims
                ],
                issued_at=c.issued_at,
                expires_at=c.expires_at,
                status=c.status.value,
                verification_case_id=c.verification_case_id,
            )
            for c in creds
        ]
    return db.query(Credential).filter(Credential.user_id == user.id).all()


@router.post("/verification/requests", response_model=VerificationOut)
def create_request(payload: VerificationCreate, user=Depends(current_user), db: Session = Depends(get_db)):
    request = VerificationRequest(user_id=user.id, **payload.model_dump())
    db.add(request)
    db.commit()
    db.refresh(request)
    audit(db, user.id, "VERIFICATION_REQUEST_CREATED", "verification_request", request.id)
    return request


@router.get("/verification/requests", response_model=list[VerificationOut])
def requests(user=Depends(current_user), db: Session = Depends(get_db)):
    return (
        db.query(VerificationRequest)
        .filter(VerificationRequest.user_id == user.id)
        .order_by(VerificationRequest.created_at.desc())
        .all()
    )


@router.post("/verification/requests/{request_id}/consent")
def consent(request_id: str, payload: ConsentCreate, user=Depends(current_user), db: Session = Depends(get_db)):
    request = db.get(VerificationRequest, request_id)
    if not request or request.user_id != user.id:
        raise HTTPException(status_code=404, detail="Request not found")
    VerificationService(db).set_consent(request, user.id, payload.decision)
    return {"status": request.status}


@router.post("/verification/requests/{request_id}/run", response_model=VerifyOut)
async def run_verification(request_id: str, user=Depends(current_user), db: Session = Depends(get_db)):
    request = db.get(VerificationRequest, request_id)
    if not request or request.user_id != user.id:
        raise HTTPException(status_code=404, detail="Request not found")
    try:
        result, proof = await VerificationService(db).verify(request, user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return VerifyOut(
        result=result.result,
        verification_level=result.verification_level,
        reason=result.reason,
        proof_id=proof.id if proof else None,
    )


@router.post("/corrections")
def correction(payload: CorrectionCreate, user=Depends(current_user), db: Session = Depends(get_db)):
    case = CorrectionCase(user_id=user.id, **payload.model_dump())
    db.add(case)
    db.commit()
    db.refresh(case)
    audit(db, user.id, "CORRECTION_CREATED", "correction_case", case.id)
    return {"id": case.id, "status": case.status}


@router.get("/notifications")
def notifications(user=Depends(current_user), db: Session = Depends(get_db)):
    return (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )


@router.post("/documents/upload-pipeline", response_model=PipelineUploadResponse)
def upload_pipeline(payload: DirectUploadPayload, user=Depends(current_user)):
    """Upload document, run simulated OCR & classification, and create verification case."""
    payload.ownerSubjectId = user.id
    return upload_and_classify_pipeline(payload)
