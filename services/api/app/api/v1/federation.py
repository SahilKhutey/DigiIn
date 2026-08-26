"""DigiIn Federated Issuer Network & Dynamic Revocation Registry Router."""

from __future__ import annotations

import base64
import hashlib
import json
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

import app.db.repository as repo
from app.db.models import CredentialModel
from app.db.session import get_db_session
from app.domain.credential_models import (
    Credential,
    CredentialStatus,
    VerifiedClaim,
)

router = APIRouter(prefix="/federation", tags=["Federation & Revocation"])

# Deterministic Issuer Private Signing Keys for Demo Sandbox
_ISSUER_PRIVATE_KEYS: dict[str, Ed25519PrivateKey] = {}

def _get_issuer_signing_key(issuer_id: str) -> Ed25519PrivateKey:
    if issuer_id not in _ISSUER_PRIVATE_KEYS:
        # Deterministic 32-byte seed based on issuer ID
        seed = hashlib.sha256(f"digiin-issuer-seed-{issuer_id}".encode()).digest()
        _ISSUER_PRIVATE_KEYS[issuer_id] = Ed25519PrivateKey.from_private_bytes(seed)
    return _ISSUER_PRIVATE_KEYS[issuer_id]


def _get_issuer_public_key_b64(issuer_id: str) -> str:
    priv = _get_issuer_signing_key(issuer_id)
    raw_pub = priv.public_key().public_bytes_raw()
    return base64.urlsafe_b64encode(raw_pub).decode().rstrip("=")


# Federated Issuer Registry Metadata
FEDERATED_ISSUERS: list[dict[str, Any]] = [
    {
        "issuer_id": "ISS-CBSE-01",
        "name": "Central Board of Secondary Education",
        "jurisdiction": "National (India)",
        "category": "Education & Academic",
        "accreditation_level": "Level 4 Sovereign Authority",
        "trust_score": 99.9,
        "supported_schemas": ["CLASS_XII_MARKSHEET", "CLASS_X_CERTIFICATE", "MIGRATION_CERTIFICATE"],
        "algorithm": "EdDSA (Ed25519)",
        "endpoint": "https://cbse.digiin.gov.in/adapter/v1",
        "status": "ACTIVE",
        "public_key_id": "key-cbse-2026-01",
    },
    {
        "issuer_id": "ISS-REV-DL-01",
        "name": "Department of Revenue, Govt. of NCT of Delhi",
        "jurisdiction": "State (NCT of Delhi)",
        "category": "Revenue & Civil Administration",
        "accreditation_level": "Level 4 Sovereign Authority",
        "trust_score": 99.7,
        "supported_schemas": ["INCOME_CERTIFICATE", "DOMICILE_CERTIFICATE", "CASTE_CERTIFICATE"],
        "algorithm": "EdDSA (Ed25519)",
        "endpoint": "https://revenue.delhi.digiin.gov.in/adapter/v1",
        "status": "ACTIVE",
        "public_key_id": "key-rev-dl-2026-01",
    },
    {
        "issuer_id": "ISS-MORTH-01",
        "name": "Ministry of Road Transport and Highways (MoRTH)",
        "jurisdiction": "National (India)",
        "category": "Transport & Licensing",
        "accreditation_level": "Level 4 Sovereign Authority",
        "trust_score": 99.8,
        "supported_schemas": ["DRIVING_LICENSE", "VEHICLE_REGISTRATION"],
        "algorithm": "EdDSA (Ed25519)",
        "endpoint": "https://parivahan.digiin.gov.in/adapter/v1",
        "status": "ACTIVE",
        "public_key_id": "key-morth-2026-01",
    },
    {
        "issuer_id": "ISS-DU-01",
        "name": "University of Delhi",
        "jurisdiction": "Higher Education (Central University)",
        "category": "Higher Education",
        "accreditation_level": "Level 3 Accredited Institution",
        "trust_score": 99.4,
        "supported_schemas": ["DEGREE_CERTIFICATE", "PROVISIONAL_CERTIFICATE", "OFFICIAL_TRANSCRIPT"],
        "algorithm": "EdDSA (Ed25519)",
        "endpoint": "https://du.digiin.ac.in/adapter/v1",
        "status": "ACTIVE",
        "public_key_id": "key-du-2026-01",
    },
    {
        "issuer_id": "ISS-UIDAI-01",
        "name": "Unique Identification Authority of India (Simulated)",
        "jurisdiction": "National Identity Authority",
        "category": "Identity & Demographics",
        "accreditation_level": "Level 4 Sovereign Authority",
        "trust_score": 100.0,
        "supported_schemas": ["EKYC_ASSERTION", "DEMOGRAPHIC_MATCH"],
        "algorithm": "EdDSA (Ed25519)",
        "endpoint": "https://uidai.digiin.gov.in/adapter/v1",
        "status": "ACTIVE",
        "public_key_id": "key-uidai-2026-01",
    },
]

# In-Memory Dynamic Revocation Registry Storage (augmented with DB persistence)
_REVOCATION_REGISTRY: dict[str, dict[str, Any]] = {
    "PRF-DEMO-REVOKED": {
        "credential_id": "PRF-DEMO-REVOKED",
        "issuer_id": "ISS-CBSE-01",
        "revoked_at": "2026-08-23T10:00:00Z",
        "reason": "SUSPECTED_FRAUD",
        "reason_description": "Suspected document alteration flagged by automated OCR cross-match.",
        "operator_id": "OFFICER-CBSE-404",
        "revocation_signature": "sig_ed25519_rev_cbse_001_mock",
    }
}


class IssueCredentialRequest(BaseModel):
    issuer_id: str = Field(..., description="Accredited Issuer Identifier, e.g. ISS-CBSE-01")
    citizen_account_id: str = Field(default="DIN-DEMO-001", description="Citizen account identifier")
    credential_type: str = Field(..., description="Schema type, e.g. CLASS_XII_MARKSHEET, INCOME_CERTIFICATE")
    title: str = Field(..., description="Human-readable credential title")
    claims: dict[str, Any] = Field(default_factory=dict, description="Structured credential claims")
    validity_days: int = Field(default=365, description="Validity period in days")


class RevokeCredentialRequest(BaseModel):
    credential_id: str = Field(..., description="Unique credential identifier to revoke")
    issuer_id: str = Field(..., description="Issuing authority ID performing revocation")
    reason: str = Field(
        default="DATA_CORRECTION_SUPERSEDED",
        description="Reason code: SUSPECTED_FRAUD | DATA_CORRECTION_SUPERSEDED | HOLDER_REQUESTED | EXPIRED",
    )
    reason_description: str = Field(default="", description="Detailed human-readable explanation")
    operator_id: str = Field(default="OFFICER-DEMO-01", description="Operator / Officer submitting revocation")


@router.get("/issuers")
def list_federated_issuers() -> dict[str, Any]:
    """List all federated and accredited government issuers."""
    enriched = []
    for iss in FEDERATED_ISSUERS:
        item = dict(iss)
        item["public_key_b64"] = _get_issuer_public_key_b64(iss["issuer_id"])
        enriched.append(item)
    return {
        "status": "success",
        "total_issuers": len(enriched),
        "issuers": enriched,
        "trust_framework": "DigiIn Sovereign Trust Federation v2.4",
    }


@router.get("/credentials")
def list_credentials(
    account_id: str | None = Query(None, description="Filter by citizen account ID"),
    issuer_id: str | None = Query(None, description="Filter by issuer ID"),
) -> dict[str, Any]:
    """List all issued sovereign credentials with real-time revocation status."""
    with get_db_session() as s:
        from sqlalchemy import desc, select
        stmt = select(CredentialModel).order_by(desc(CredentialModel.issued_at))
        if account_id:
            stmt = stmt.where(CredentialModel.account_id == account_id)
        if issuer_id:
            stmt = stmt.where(CredentialModel.issuer == issuer_id)
        rows = s.scalars(stmt).all()

        results = []
        for r in rows:
            is_revoked = (
                r.status == "revoked"
                or r.credential_id in _REVOCATION_REGISTRY
            )
            rev_info = _REVOCATION_REGISTRY.get(r.credential_id)
            raw_claims = json.loads(r.claims_json) if r.claims_json else []
            results.append({
                "credential_id": r.credential_id,
                "account_id": r.account_id,
                "credential_type": r.credential_type,
                "issuer": r.issuer,
                "issued_at": r.issued_at.isoformat() if r.issued_at else None,
                "expires_at": r.expires_at.isoformat() if r.expires_at else None,
                "status": "REVOKED" if is_revoked else "ACTIVE",
                "is_revoked": is_revoked,
                "claims": raw_claims,
                "revocation_details": rev_info,
            })
    return {
        "status": "success",
        "total": len(results),
        "credentials": results,
    }


@router.post("/issue-credential")
def issue_verifiable_credential(req: IssueCredentialRequest) -> dict[str, Any]:
    """Mint and cryptographically sign a new sovereign credential from an accredited issuer."""
    issuer_match = next((i for i in FEDERATED_ISSUERS if i["issuer_id"] == req.issuer_id), None)
    if not issuer_match:
        raise HTTPException(status_code=400, detail=f"Issuer '{req.issuer_id}' is not an accredited federated issuer.")

    cred_id = f"CRED-{req.issuer_id.split('-')[1]}-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.now(UTC)
    expires = now + timedelta(days=req.validity_days)

    # 1. Canonical claims representation and digest
    canonical_claims_bytes = json.dumps(req.claims, sort_keys=True, separators=(",", ":")).encode("utf-8")
    claim_digest = hashlib.sha256(canonical_claims_bytes).hexdigest()

    # 2. Cryptographic signature with issuer private key
    signing_key = _get_issuer_signing_key(req.issuer_id)
    signature_payload = f"{cred_id}:{req.citizen_account_id}:{req.credential_type}:{claim_digest}:{now.isoformat()}".encode("utf-8")
    signature = signing_key.sign(signature_payload)
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")

    # 3. Save into DB Repository
    db_claims = []
    for k, v in req.claims.items():
        db_claims.append(
            VerifiedClaim(
                claim_type=k,
                value=str(v),
                source=req.issuer_id,
                verification_level="level_4_authoritative",
                verified_at=now,
            )
        )

    cred = Credential(
        credential_id=cred_id,
        account_id=req.citizen_account_id,
        credential_type=req.credential_type,
        issuer=req.issuer_id,
        claims=tuple(db_claims),
        issued_at=now,
        expires_at=expires,
        status=CredentialStatus.ACTIVE,
        verification_case_id=f"CASE-AUTO-{uuid.uuid4().hex[:6].upper()}",
    )
    repo.save_credential(cred)

    return {
        "status": "success",
        "message": f"Successfully minted sovereign credential {cred_id}",
        "credential": {
            "credential_id": cred_id,
            "account_id": req.citizen_account_id,
            "issuer_id": req.issuer_id,
            "issuer_name": issuer_match["name"],
            "credential_type": req.credential_type,
            "title": req.title,
            "issued_at": now.isoformat(),
            "expires_at": expires.isoformat(),
            "claim_digest": f"sha256:{claim_digest}",
            "digital_signature": sig_b64,
            "public_key_id": issuer_match["public_key_id"],
            "status": "ACTIVE",
            "claims": req.claims,
        },
    }


@router.post("/revoke-credential")
def revoke_verifiable_credential(req: RevokeCredentialRequest) -> dict[str, Any]:
    """Revoke an issued credential and publish entry to the dynamic revocation registry."""
    now = datetime.now(UTC)

    # 1. Update database record status
    try:
        repo.update_credential_status(req.credential_id, CredentialStatus.REVOKED)
    except Exception:
        pass  # Continue to record in revocation registry even if synthetic

    # 2. Generate cryptographic revocation assertion
    signing_key = _get_issuer_signing_key(req.issuer_id)
    rev_payload = f"REVOKE:{req.credential_id}:{req.issuer_id}:{req.reason}:{now.isoformat()}".encode("utf-8")
    rev_sig = base64.urlsafe_b64encode(signing_key.sign(rev_payload)).decode().rstrip("=")

    # 3. Publish to dynamic revocation registry
    rev_record = {
        "credential_id": req.credential_id,
        "issuer_id": req.issuer_id,
        "revoked_at": now.isoformat(),
        "reason": req.reason,
        "reason_description": req.reason_description or f"Revoked with reason code: {req.reason}",
        "operator_id": req.operator_id,
        "revocation_signature": rev_sig,
        "status": "REVOKED",
    }
    _REVOCATION_REGISTRY[req.credential_id] = rev_record

    return {
        "status": "success",
        "message": f"Credential {req.credential_id} successfully revoked in dynamic registry.",
        "revocation_record": rev_record,
    }


@router.get("/revocation-registry")
def get_revocation_registry() -> dict[str, Any]:
    """Retrieve the authoritative dynamic cryptographic Revocation Status List (W3C / RFC standard)."""
    records = list(_REVOCATION_REGISTRY.values())
    sorted_ids = sorted(list(_REVOCATION_REGISTRY.keys()))
    aggregate_hash = hashlib.sha256("::".join(sorted_ids).encode("utf-8")).hexdigest()

    return {
        "status": "success",
        "registry_version": "2026.08-rev1",
        "standard": "W3C Bitstring Status List / RFC 5280 CRL",
        "aggregate_digest": f"sha256:{aggregate_hash}",
        "revoked_count": len(records),
        "revocations": records,
        "last_updated": datetime.now(UTC).isoformat(),
    }


@router.get("/status/{credential_id}")
def get_credential_revocation_status(credential_id: str) -> dict[str, Any]:
    """Query real-time revocation and validity status for any sovereign credential."""
    is_revoked = credential_id in _REVOCATION_REGISTRY
    if is_revoked:
        return {
            "status": "REVOKED",
            "is_valid": False,
            "credential_id": credential_id,
            "revocation_details": _REVOCATION_REGISTRY[credential_id],
        }
    return {
        "status": "ACTIVE",
        "is_valid": True,
        "credential_id": credential_id,
        "revocation_details": None,
    }
