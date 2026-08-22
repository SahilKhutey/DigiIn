import hashlib
import hmac
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import get_db
from app.models.entities import VerificationProof

router = APIRouter(prefix="/proofs", tags=["proofs"])


@router.get("/{proof_id}/verify")
def verify_proof(proof_id: str, db: Session = Depends(get_db)):
    proof = db.get(VerificationProof, proof_id)
    if not proof:
        raise HTTPException(status_code=404, detail="Proof not found")
    expected = hmac.new(
        settings.proof_secret.encode(), proof.proof_payload.encode(), hashlib.sha256
    ).hexdigest()
    valid = hmac.compare_digest(expected, proof.signature)
    return {"valid": valid, "proof": json.loads(proof.proof_payload) if valid else None}
