from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.api.deps import current_user
from app.models.entities import User, Credential, VerificationRequest, CorrectionCase, Notification
from app.schemas.core import CredentialCreate, CredentialOut, VerificationCreate, VerificationOut, ConsentCreate, VerifyOut, CorrectionCreate
from app.services.verification import VerificationService
from app.services.audit import audit

router = APIRouter(prefix="", tags=["citizen"])

@router.get("/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "email": user.email, "role": user.role, "status": user.status}

@router.post("/credentials", response_model=CredentialOut)
def create_credential(payload: CredentialCreate, user=Depends(current_user), db: Session=Depends(get_db)):
    credential = Credential(user_id=user.id, **payload.model_dump())
    db.add(credential); db.commit(); db.refresh(credential)
    audit(db, user.id, "CREDENTIAL_CREATED", "credential", credential.id)
    return credential

@router.get("/credentials", response_model=list[CredentialOut])
def credentials(user=Depends(current_user), db: Session=Depends(get_db)):
    return db.query(Credential).filter(Credential.user_id == user.id).all()

@router.post("/verification/requests", response_model=VerificationOut)
def create_request(payload: VerificationCreate, user=Depends(current_user), db: Session=Depends(get_db)):
    request = VerificationRequest(user_id=user.id, **payload.model_dump())
    db.add(request); db.commit(); db.refresh(request)
    audit(db, user.id, "VERIFICATION_REQUEST_CREATED", "verification_request", request.id)
    return request

@router.get("/verification/requests", response_model=list[VerificationOut])
def requests(user=Depends(current_user), db: Session=Depends(get_db)):
    return db.query(VerificationRequest).filter(VerificationRequest.user_id == user.id).order_by(VerificationRequest.created_at.desc()).all()

@router.post("/verification/requests/{request_id}/consent")
def consent(request_id: str, payload: ConsentCreate, user=Depends(current_user), db: Session=Depends(get_db)):
    request = db.get(VerificationRequest, request_id)
    if not request or request.user_id != user.id:
        raise HTTPException(404, "Request not found")
    VerificationService(db).set_consent(request, user.id, payload.decision)
    return {"status": request.status}

@router.post("/verification/requests/{request_id}/run", response_model=VerifyOut)
async def run_verification(request_id: str, user=Depends(current_user), db: Session=Depends(get_db)):
    request = db.get(VerificationRequest, request_id)
    if not request or request.user_id != user.id:
        raise HTTPException(404, "Request not found")
    try:
        result, proof = await VerificationService(db).verify(request, user.id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return VerifyOut(
        result=result.result,
        verification_level=result.verification_level,
        reason=result.reason,
        proof_id=proof.id if proof else None
    )

@router.post("/corrections")
def correction(payload: CorrectionCreate, user=Depends(current_user), db: Session=Depends(get_db)):
    case = CorrectionCase(user_id=user.id, **payload.model_dump())
    db.add(case); db.commit(); db.refresh(case)
    audit(db, user.id, "CORRECTION_CREATED", "correction_case", case.id)
    return {"id": case.id, "status": case.status}

@router.get("/notifications")
def notifications(user=Depends(current_user), db: Session=Depends(get_db)):
    return db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.created_at.desc()).all()
