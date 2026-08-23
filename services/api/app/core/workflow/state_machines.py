"""
DigiIn Core Workflow Engine — Authoritative Domain State Machines
Enforces deterministic lifecycle transitions, optimistic concurrency versions, and illegal transition guards.
"""

from enum import StrEnum
from typing import Any


class IllegalStateTransitionError(Exception):
    def __init__(self, entity_type: str, current_state: str, event: str, allowed_events: set[str]):
        super().__init__(
            f"ILLEGAL_TRANSITION: Cannot transition {entity_type} from '{current_state}' via event '{event}'. "
            f"Allowed events: {sorted(list(allowed_events)) or 'None (Terminal State)'}"
        )
        self.entity_type = entity_type
        self.current_state = current_state
        self.event = event

# --- 1. Document Lifecycle States & Transitions ---
class DocumentState(StrEnum):
    UPLOADING = "UPLOADING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    UNDER_REVIEW = "UNDER_REVIEW"
    VERIFIED = "VERIFIED"
    PROCESSING_FAILED = "PROCESSING_FAILED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"

DOCUMENT_TRANSITIONS: dict[DocumentState, dict[str, DocumentState]] = {
    DocumentState.UPLOADING: {
        "PROCESS": DocumentState.PROCESSING,
        "FAIL": DocumentState.PROCESSING_FAILED,
    },
    DocumentState.PROCESSING: {
        "COMPLETE": DocumentState.READY,
        "FAIL": DocumentState.PROCESSING_FAILED,
    },
    DocumentState.READY: {
        "SUBMIT_FOR_REVIEW": DocumentState.UNDER_REVIEW,
        "AUTO_VERIFY": DocumentState.VERIFIED,
        "EXPIRE": DocumentState.EXPIRED,
    },
    DocumentState.UNDER_REVIEW: {
        "APPROVE": DocumentState.VERIFIED,
        "REJECT": DocumentState.REJECTED,
        "EXPIRE": DocumentState.EXPIRED,
    },
    DocumentState.VERIFIED: {
        "REVOKE": DocumentState.REVOKED,
        "EXPIRE": DocumentState.EXPIRED,
    },
    DocumentState.PROCESSING_FAILED: {},
    DocumentState.REJECTED: {},
    DocumentState.EXPIRED: {},
    DocumentState.REVOKED: {},
}

# --- 2. Verification Lifecycle States & Transitions ---
class VerificationState(StrEnum):
    CREATED = "CREATED"
    PENDING = "PENDING"
    EVIDENCE_COLLECTION = "EVIDENCE_COLLECTION"
    EVIDENCE_RECEIVED = "EVIDENCE_RECEIVED"
    EVALUATING = "EVALUATING"
    VERIFIED = "VERIFIED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    REJECTED = "REJECTED"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"

VERIFICATION_TRANSITIONS: dict[VerificationState, dict[str, VerificationState]] = {
    VerificationState.CREATED: {
        "START": VerificationState.PENDING,
    },
    VerificationState.PENDING: {
        "COLLECT_EVIDENCE": VerificationState.EVIDENCE_COLLECTION,
        "PROVIDER_TIMEOUT": VerificationState.PROVIDER_UNAVAILABLE,
    },
    VerificationState.EVIDENCE_COLLECTION: {
        "EVIDENCE_OK": VerificationState.EVIDENCE_RECEIVED,
        "PROVIDER_ERROR": VerificationState.PROVIDER_UNAVAILABLE,
    },
    VerificationState.EVIDENCE_RECEIVED: {
        "EVALUATE": VerificationState.EVALUATING,
    },
    VerificationState.EVALUATING: {
        "PASS": VerificationState.VERIFIED,
        "FAIL": VerificationState.REJECTED,
        "FLAG_REVIEW": VerificationState.NEEDS_REVIEW,
    },
    VerificationState.NEEDS_REVIEW: {
        "APPROVE": VerificationState.VERIFIED,
        "REJECT": VerificationState.REJECTED,
    },
    VerificationState.VERIFIED: {},
    VerificationState.REJECTED: {},
    VerificationState.PROVIDER_UNAVAILABLE: {
        "RETRY": VerificationState.PENDING,
    },
}

# --- 3. Consent Lifecycle States & Transitions ---
class ConsentState(StrEnum):
    CREATED = "CREATED"
    PENDING = "PENDING"
    GRANTED = "GRANTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"

CONSENT_TRANSITIONS: dict[ConsentState, dict[str, ConsentState]] = {
    ConsentState.CREATED: {
        "REQUEST": ConsentState.PENDING,
    },
    ConsentState.PENDING: {
        "GRANT": ConsentState.GRANTED,
        "DECLINE": ConsentState.DECLINED,
        "EXPIRE": ConsentState.EXPIRED,
    },
    ConsentState.GRANTED: {
        "REVOKE": ConsentState.REVOKED,
        "EXPIRE": ConsentState.EXPIRED,
    },
    ConsentState.DECLINED: {},
    ConsentState.EXPIRED: {},
    ConsentState.REVOKED: {},
}

# --- 4. Verification Request Lifecycle States ---
class RequestState(StrEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    PENDING_CONSENT = "PENDING_CONSENT"
    CONSENTED = "CONSENTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"

REQUEST_TRANSITIONS: dict[RequestState, dict[str, RequestState]] = {
    RequestState.DRAFT: {
        "SUBMIT": RequestState.SUBMITTED,
    },
    RequestState.SUBMITTED: {
        "REQUIRE_CONSENT": RequestState.PENDING_CONSENT,
        "CANCEL": RequestState.CANCELLED,
    },
    RequestState.PENDING_CONSENT: {
        "CONSENT_GRANTED": RequestState.CONSENTED,
        "CONSENT_DECLINED": RequestState.DECLINED,
        "EXPIRE": RequestState.EXPIRED,
        "CANCEL": RequestState.CANCELLED,
    },
    RequestState.CONSENTED: {
        "START_PROCESS": RequestState.PROCESSING,
        "CANCEL": RequestState.CANCELLED,
    },
    RequestState.PROCESSING: {
        "COMPLETE": RequestState.COMPLETED,
        "FAIL": RequestState.FAILED,
    },
    RequestState.COMPLETED: {},
    RequestState.DECLINED: {},
    RequestState.EXPIRED: {},
    RequestState.CANCELLED: {},
    RequestState.FAILED: {},
}

# --- 5. Proof Lifecycle States ---
class ProofState(StrEnum):
    CREATED = "CREATED"
    ISSUED = "ISSUED"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    SUPERSEDED = "SUPERSEDED"

PROOF_TRANSITIONS: dict[ProofState, dict[str, ProofState]] = {
    ProofState.CREATED: {
        "ISSUE": ProofState.ISSUED,
    },
    ProofState.ISSUED: {
        "ACTIVATE": ProofState.ACTIVE,
    },
    ProofState.ACTIVE: {
        "EXPIRE": ProofState.EXPIRED,
        "REVOKE": ProofState.REVOKED,
        "SUPERSEDE": ProofState.SUPERSEDED,
    },
    ProofState.EXPIRED: {},
    ProofState.REVOKED: {},
    ProofState.SUPERSEDED: {},
}

class DomainWorkflowEngine:
    @staticmethod
    def transition_document(doc: dict[str, Any], event: str) -> str:
        current = doc.get("status", DocumentState.UPLOADING)
        allowed = DOCUMENT_TRANSITIONS.get(current, {})
        if event not in allowed:
            raise IllegalStateTransitionError("Document", current, event, set(allowed.keys()))
        new_state = allowed[event]
        doc["status"] = new_state
        doc["version"] = doc.get("version", 1) + 1
        return new_state

    @staticmethod
    def transition_verification(ver: dict[str, Any], event: str) -> str:
        current = ver.get("status", VerificationState.CREATED)
        allowed = VERIFICATION_TRANSITIONS.get(current, {})
        if event not in allowed:
            raise IllegalStateTransitionError("Verification", current, event, set(allowed.keys()))
        new_state = allowed[event]
        ver["status"] = new_state
        ver["version"] = ver.get("version", 1) + 1
        return new_state

    @staticmethod
    def transition_consent(consent: dict[str, Any], event: str) -> str:
        current = consent.get("status", ConsentState.CREATED)
        allowed = CONSENT_TRANSITIONS.get(current, {})
        if event not in allowed:
            raise IllegalStateTransitionError("Consent", current, event, set(allowed.keys()))
        new_state = allowed[event]
        consent["status"] = new_state
        consent["version"] = consent.get("version", 1) + 1
        return new_state

    @staticmethod
    def transition_request(req: dict[str, Any], event: str) -> str:
        current = req.get("status", RequestState.DRAFT)
        allowed = REQUEST_TRANSITIONS.get(current, {})
        if event not in allowed:
            raise IllegalStateTransitionError("VerificationRequest", current, event, set(allowed.keys()))
        new_state = allowed[event]
        req["status"] = new_state
        req["version"] = req.get("version", 1) + 1
        return new_state

    @staticmethod
    def transition_proof(proof: dict[str, Any], event: str) -> str:
        current = proof.get("status", ProofState.CREATED)
        allowed = PROOF_TRANSITIONS.get(current, {})
        if event not in allowed:
            raise IllegalStateTransitionError("Proof", current, event, set(allowed.keys()))
        new_state = allowed[event]
        proof["status"] = new_state
        proof["version"] = proof.get("version", 1) + 1
        return new_state
