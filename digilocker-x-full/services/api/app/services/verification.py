import hashlib
import hmac
import json
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.entities import (
    Credential, VerificationRequest, Consent,
    VerificationResult, VerificationProof, Notification
)
from app.integrations.issuer import IssuerRegistry
from app.services.audit import audit

class VerificationService:
    def __init__(self, db: Session):
        self.db = db
        self.registry = IssuerRegistry()

    def set_consent(self, request, user_id, decision):
        existing = self.db.query(Consent).filter(Consent.request_id == request.id).first()
        if existing:
            existing.decision = decision
        else:
            self.db.add(Consent(
                request_id=request.id,
                user_id=user_id,
                decision=decision
            ))
        request.status = "CONSENT_GRANTED" if decision == "GRANT" else "DENIED"
        self.db.commit()
        audit(self.db, user_id, "CONSENT_"+decision, "verification_request", request.id)
        return request

    async def verify(self, request, actor_id):
        consent = self.db.query(Consent).filter(
            Consent.request_id == request.id,
            Consent.decision == "GRANT"
        ).first()
        if not consent:
            raise ValueError("Explicit consent is required")

        credential = self.db.query(Credential).filter(
            Credential.user_id == request.user_id,
            Credential.credential_type == request.credential_type
        ).first()

        if not credential:
            result = VerificationResult(
                request_id=request.id,
                credential_id=None,
                result="NOT_FOUND",
                verification_level=0,
                reason="Credential not found",
            )
            self.db.add(result)
            request.status = "COMPLETED"
            self.db.commit()
            audit(self.db, actor_id, "VERIFICATION_NOT_FOUND", "verification_request", request.id)
            return result, None

        adapter = self.registry.get(credential.issuer_id)
        if not adapter:
            raise ValueError("Issuer integration unavailable")

        issuer_result = await adapter.verify(credential)
        result = VerificationResult(
            request_id=request.id,
            credential_id=credential.id,
            result="VERIFIED" if issuer_result.verified else "REJECTED",
            verification_level=issuer_result.level,
            reason=issuer_result.reason,
        )
        self.db.add(result)
        request.status = "COMPLETED"

        proof = None
        if issuer_result.verified:
            payload = {
                "request_id": request.id,
                "credential_type": credential.credential_type,
                "verification": "VERIFIED",
                "verification_level": issuer_result.level,
                "purpose": request.purpose,
                "audience": request.requester_name,
            }
            encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
            signature = hmac.new(
                settings.proof_secret.encode(),
                encoded.encode(),
                hashlib.sha256
            ).hexdigest()
            proof = VerificationProof(
                request_id=request.id,
                proof_payload=encoded,
                signature=signature,
            )
            self.db.add(proof)
            self.db.add(Notification(
                user_id=request.user_id,
                title="Verification completed",
                body=f"{request.requester_name} received a verified result for {credential.credential_type}."
            ))

        self.db.commit()
        audit(self.db, actor_id, "VERIFICATION_COMPLETED", "verification_request", request.id,
              {"result": result.result})
        return result, proof
