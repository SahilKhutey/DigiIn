"""Synthetic verification gateway for purpose-bound proof tokens."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from app.domain.models import (
    ConsentRecord,
    CredentialProofResult,
    DisclosureLevel,
    DisclosureMode,
    PredicateProofResult,
    ProofTokenIntrospection,
    SelectiveDisclosurePreference,
    VerificationAuthorization,
    VerificationProof,
    VerificationReceipt,
    VerificationRequestCreate,
    VerificationRequestRecord,
    VerificationRequirement,
    VerificationResult,
    VerificationStatus,
)
from app.services.crypto import sign_proof_token, verify_proof_token

DEMO_SIGNING_KEY = b"digiin-local-demo-signing-key"
DEMO_SUBJECT_ID = "subj_demo_5c7b90"


REQUESTS: dict[str, VerificationRequestRecord] = {}
RESULTS: dict[str, VerificationResult] = {}
REVOKED_VERIFICATIONS: dict[str, dict[str, Any]] = {}


DEMO_CREDENTIALS: dict[str, dict[str, Any]] = {
    "CLASS_XII": {
        "issuer": "Mock CBSE",
        "level": 4,
        "status": VerificationStatus.VERIFIED,
        "attributes": {
            "qualification": "Class XII",
            "qualification_status": "PASSED",
            "passing_year": 2026,
            "board": "CBSE",
            "percentage": 94.2,
            "roll_number": "99214",
            "school_code": "SCH-DEL-4012",
        },
    },
    "CLASS_XII_QUALIFICATION": {
        "issuer": "Mock CBSE",
        "level": 4,
        "status": VerificationStatus.VERIFIED,
        "attributes": {
            "qualification": "Class XII",
            "qualification_status": "PASSED",
            "passing_year": 2026,
            "board": "CBSE",
            "percentage": 94.2,
            "roll_number": "99214",
            "school_code": "SCH-DEL-4012",
        },
    },
    "GRADUATION": {
        "issuer": "Mock State University",
        "level": 4,
        "status": VerificationStatus.VERIFIED,
        "attributes": {
            "qualification": "Bachelor's Degree",
            "course": "B.Tech Computer Science",
            "issue_year": 2025,
            "cgpa": 8.9,
            "enrollment_no": "ENR-2021-CS-890",
        },
    },
    "DOMICILE": {
        "issuer": "Mock State Authority",
        "level": 4,
        "status": VerificationStatus.VERIFIED,
        "attributes": {
            "jurisdiction": "CHHATTISGARH",
            "residence_verified": True,
            "ward_number": "W-14",
            "district": "Raipur",
        },
    },
    "AGE_OVER_18": {
        "issuer": "Mock Birth Registry",
        "level": 5,
        "status": VerificationStatus.VERIFIED,
        "attributes": {
            "age_requirement_met": True,
            "date_of_birth": "2006-05-12",
            "aadhaar_ref": "XXXX-XXXX-8910",
        },
    },
    "CATEGORY_CERTIFICATE": {
        "issuer": "Mock State Welfare Department",
        "level": 4,
        "status": VerificationStatus.VERIFIED,
        "attributes": {
            "category_certificate": "VERIFIED",
            "current_status": "ACTIVE",
            "caste_category": "OBC-NCL",
        },
    },
}


def create_verification_request(payload: VerificationRequestCreate) -> VerificationRequestRecord:
    now = datetime.now(UTC)
    request = VerificationRequestRecord(
        **payload.model_dump(),
        requestId=f"vr_{uuid4().hex[:12]}",
        status="PENDING_CONSENT",
        createdAt=now,
        expiresAt=now + timedelta(minutes=payload.ttlMinutes),
        consentText=_consent_text(payload),
    )
    REQUESTS[request.requestId] = request
    return request


def list_verification_requests() -> list[VerificationRequestRecord]:
    return sorted(REQUESTS.values(), key=lambda request: request.createdAt, reverse=True)


def get_verification_request(request_id: str) -> VerificationRequestRecord | None:
    return REQUESTS.get(request_id)


def authorize_verification_request(
    request_id: str, authorization: VerificationAuthorization
) -> VerificationResult | None:
    request = REQUESTS.get(request_id)
    if request is None:
        return None
    if datetime.now(UTC) > request.expiresAt:
        REQUESTS[request_id] = request.model_copy(update={"status": "EXPIRED"})
        return _expired_result(request, authorization.subjectId)
    if not authorization.allow:
        REQUESTS[request_id] = request.model_copy(update={"status": "DECLINED"})
        return _declined_result(request, authorization.subjectId)

    now = datetime.now(UTC)
    custom = authorization.customDisclosure
    results = [
        _evaluate_requirement(item, request.disclosure.mode, custom)
        for item in request.requirements
    ]
    status = _overall_status(results)
    verification_id = f"ver_{uuid4().hex[:12]}"
    expires_at = min(request.expiresAt, now + timedelta(minutes=request.ttlMinutes))

    if custom:
        if custom.mode == "PREDICATE_ONLY":
            disclosure_level = DisclosureLevel.BOOLEAN
        elif custom.mode == "SELECTIVE_ATTRIBUTES":
            disclosure_level = DisclosureLevel.ATTRIBUTE
        else:
            disclosure_level = DisclosureLevel.DOCUMENT
    else:
        disclosure_level = _disclosure_level(request.disclosure.mode)

    all_predicates: list[PredicateProofResult] = []
    all_masked_fields: list[str] = []
    for r in results:
        all_predicates.extend(r.predicateResults)
        all_masked_fields.extend(f"{r.credential}.{m}" for m in r.maskedAttributes)

    claims = _token_claims(
        request=request,
        verification_id=verification_id,
        subject_id=authorization.subjectId,
        status=status,
        results=results,
        disclosure_level=disclosure_level,
        issued_at=now,
        expires_at=expires_at,
        predicate_proofs=all_predicates,
        masked_attributes=all_masked_fields,
    )
    token, key_id, alg = sign_proof_token(claims, algorithm="EdDSA")
    proof = VerificationProof(token=token, algorithm=alg, keyId=key_id)  # type: ignore[arg-type]
    receipt = VerificationReceipt(
        verificationId=verification_id,
        requesterName=request.requesterName,
        purpose=request.purpose,
        status=status,
        shared=_shared_fields(results, disclosure_level),
        documentShared=disclosure_level == DisclosureLevel.DOCUMENT,
        issuedAt=now,
        expiresAt=expires_at,
    )
    result = VerificationResult(
        verificationId=verification_id,
        requestId=request.requestId,
        status=status,
        subjectId=authorization.subjectId,
        audience=request.audience,
        purpose=request.purpose,
        disclosureLevel=disclosure_level,
        results=results,
        predicateProofs=all_predicates,
        maskedAttributesSummary=all_masked_fields,
        proof=proof,
        receipt=receipt,
        issuedAt=now,
        expiresAt=expires_at,
    )
    REQUESTS[request_id] = request.model_copy(update={"status": "AUTHORIZED"})
    RESULTS[verification_id] = result
    return result


def get_verification_result(verification_id: str) -> VerificationResult | None:
    return RESULTS.get(verification_id)


def result_for_request(request_id: str) -> VerificationResult | None:
    for result in RESULTS.values():
        if result.requestId == request_id:
            return result
    return None


def introspect_token(token: str, audience: str, nonce: str | None = None) -> ProofTokenIntrospection:
    claims, key_id, alg = verify_proof_token(token)
    if claims is None:
        # Fallback to legacy HMAC verification
        claims = _verify_token(token)
        if claims is None:
            return ProofTokenIntrospection(
                active=False,
                status="INVALID_PROOF",
                message="The proof token signature or structure is invalid.",
                cryptoVerified=False,
            )
        key_id = "legacy-hmac-key"
        alg = "HS256"

    verification_id = claims.get("verification_id", "")
    expires_at = None
    if claims.get("exp"):
        try:
            expires_at = datetime.fromisoformat(claims["exp"])
        except ValueError:
            pass

    # Check if proof was cryptographically revoked by citizen
    if verification_id in REVOKED_VERIFICATIONS:
        rev_info = REVOKED_VERIFICATIONS[verification_id]
        return ProofTokenIntrospection(
            active=False,
            status="REVOKED",
            verificationId=verification_id,
            audience=claims.get("aud"),
            expiresAt=expires_at,
            keyId=key_id,
            algorithm=alg,
            cryptoVerified=True,
            message=f"The proof token was revoked by the citizen on {rev_info.get('revokedAt', 'recent')}. Reason: {rev_info.get('reason', 'Citizen revoked consent')}",
        )

    if expires_at and datetime.now(UTC) > expires_at:
        return ProofTokenIntrospection(
            active=False,
            status="EXPIRED",
            verificationId=verification_id,
            audience=claims.get("aud"),
            expiresAt=expires_at,
            keyId=key_id,
            algorithm=alg,
            cryptoVerified=True,
            message="The proof token has expired.",
        )
    if claims.get("aud") != audience:
        return ProofTokenIntrospection(
            active=False,
            status="AUDIENCE_MISMATCH",
            verificationId=verification_id,
            audience=claims.get("aud"),
            expiresAt=expires_at,
            keyId=key_id,
            algorithm=alg,
            cryptoVerified=True,
            message="The proof token was issued for a different audience.",
        )
    if nonce is not None and claims.get("nonce") != nonce:
        return ProofTokenIntrospection(
            active=False,
            status="INVALID_PROOF",
            verificationId=verification_id,
            audience=claims.get("aud"),
            expiresAt=expires_at,
            keyId=key_id,
            algorithm=alg,
            cryptoVerified=True,
            message="The proof token nonce does not match the requester challenge.",
        )
    return ProofTokenIntrospection(
        active=True,
        status="TRUSTED_PROOF",
        verificationId=verification_id,
        subjectId=claims.get("sub"),
        audience=claims.get("aud"),
        purpose=claims.get("purpose"),
        expiresAt=expires_at,
        claims=claims,
        keyId=key_id,
        algorithm=alg,
        cryptoVerified=True,
        message="The proof token is asymmetric-signed, active, audience-bound and purpose-bound.",
    )


def list_consents(subject_id: str = "subj_demo_5c7b90") -> list[ConsentRecord]:
    """Lists all active and historical consents granted by the citizen."""
    consents: list[ConsentRecord] = []
    now = datetime.now(UTC)
    for v_id, res in RESULTS.items():
        if res.subjectId != subject_id and subject_id != "*":
            continue
        req = REQUESTS.get(res.requestId)
        req_name = req.requesterName if req else "Authorised Verifier"
        client_id = req.clientId if req else "verifier-client"

        is_revoked = v_id in REVOKED_VERIFICATIONS
        is_expired = now > res.expiresAt
        if is_revoked:
            status = "REVOKED"
        elif is_expired:
            status = "EXPIRED"
        else:
            status = "ACTIVE"

        rev_info = REVOKED_VERIFICATIONS.get(v_id, {})
        consents.append(
            ConsentRecord(
                consentId=f"cst_{v_id[4:] if len(v_id) > 4 else v_id}",
                verificationId=v_id,
                requestId=res.requestId,
                subjectId=res.subjectId,
                requesterName=req_name,
                clientId=client_id,
                purpose=res.purpose,
                audience=res.audience,
                disclosureLevel=res.disclosureLevel,
                credentialsVerified=[r.credential for r in res.results],
                predicateCount=len(res.predicateProofs),
                maskedAttributesCount=len(res.maskedAttributesSummary),
                status=status,
                issuedAt=res.issuedAt,
                expiresAt=res.expiresAt,
                revokedAt=rev_info.get("revokedAt"),
                revocationReason=rev_info.get("reason"),
            )
        )
    return sorted(consents, key=lambda c: c.issuedAt, reverse=True)


def revoke_verification_consent(
    verification_id: str,
    subject_id: str = "subj_demo_5c7b90",
    reason: str = "Citizen requested credential revocation.",
) -> ConsentRecord | None:
    """Revokes an issued verification proof token immediately."""
    result = RESULTS.get(verification_id)
    if result is None:
        return None
    now = datetime.now(UTC)
    REVOKED_VERIFICATIONS[verification_id] = {
        "revokedAt": now,
        "reason": reason,
    }
    # Update result status
    RESULTS[verification_id] = result.model_copy(update={"status": VerificationStatus.NOT_VERIFIED})

    # Return updated consent record
    consents = list_consents(subject_id)
    for c in consents:
        if c.verificationId == verification_id:
            return c
    return None



def demo_exam_request() -> VerificationRequestCreate:
    return VerificationRequestCreate(
        clientId="nta-2026",
        requesterName="Demo Examination Portal",
        purpose="EXAM_APPLICATION",
        audience="NTA_APPLICATION_PORTAL",
        requirements=[
            VerificationRequirement(
                credential="CLASS_XII",
                minimumLevel=3,
                attributes=["qualification", "passing_year"],
            ),
            VerificationRequirement(
                credential="DOMICILE",
                minimumLevel=3,
                jurisdiction="CHHATTISGARH",
                attributes=["jurisdiction"],
            ),
            VerificationRequirement(credential="AGE_OVER_18", minimumLevel=4),
        ],
    )


def _evaluate_requirement(
    requirement: VerificationRequirement,
    default_mode: DisclosureMode,
    custom: SelectiveDisclosurePreference | None = None,
) -> CredentialProofResult:
    credential = DEMO_CREDENTIALS.get(requirement.credential)
    if credential is None:
        return CredentialProofResult(
            credential=requirement.credential,
            verified=False,
            status=VerificationStatus.NOT_FOUND,
            level=0,
            message="No matching credential exists in the synthetic wallet.",
        )
    status = credential["status"]
    level = credential["level"]
    attributes = dict(credential["attributes"])
    verified = status == VerificationStatus.VERIFIED and level >= requirement.minimumLevel

    if requirement.jurisdiction and attributes.get("jurisdiction") != requirement.jurisdiction:
        verified = False
        status = VerificationStatus.NOT_VERIFIED

    # 1. Evaluate explicit and derived predicates
    predicates: list[PredicateProofResult] = []
    if requirement.predicate:
        sat = _predicate_passes(requirement.predicate, attributes)
        if not sat:
            verified = False
            status = VerificationStatus.NOT_VERIFIED
        predicates.append(
            PredicateProofResult(
                predicateId=f"pred_{requirement.credential.lower()}_{uuid4().hex[:6]}",
                claimName=requirement.credential,
                expression=f"{requirement.predicate.attribute} {requirement.predicate.operator} {requirement.predicate.value}",
                satisfied=sat,
                proofType="DERIVED_ZERO_KNOWLEDGE_PREDICATE",
                maskedAttributes=[requirement.predicate.attribute],
            )
        )
    else:
        # Generate default derived zero-knowledge predicates for standard credentials
        if requirement.credential in ["CLASS_XII", "CLASS_XII_QUALIFICATION"]:
            predicates.append(
                PredicateProofResult(
                    predicateId=f"pred_class12_{uuid4().hex[:6]}",
                    claimName=requirement.credential,
                    expression="qualification_status == PASSED",
                    satisfied=True,
                    proofType="DERIVED_ZERO_KNOWLEDGE_PREDICATE",
                    maskedAttributes=["roll_number", "percentage", "school_code"],
                )
            )
        elif requirement.credential == "AGE_OVER_18":
            predicates.append(
                PredicateProofResult(
                    predicateId=f"pred_age_{uuid4().hex[:6]}",
                    claimName="AGE_OVER_18",
                    expression="age >= 18",
                    satisfied=True,
                    proofType="DERIVED_ZERO_KNOWLEDGE_PREDICATE",
                    maskedAttributes=["date_of_birth", "aadhaar_ref"],
                )
            )
        elif requirement.credential == "DOMICILE":
            predicates.append(
                PredicateProofResult(
                    predicateId=f"pred_dom_{uuid4().hex[:6]}",
                    claimName="DOMICILE",
                    expression=f"jurisdiction == '{attributes.get('jurisdiction', 'CHHATTISGARH')}'",
                    satisfied=True,
                    proofType="DERIVED_ZERO_KNOWLEDGE_PREDICATE",
                    maskedAttributes=["ward_number", "district"],
                )
            )

    # 2. Determine disclosed vs masked attributes based on mode
    eff_mode = custom.mode if custom else ("PREDICATE_ONLY" if default_mode == DisclosureMode.MINIMUM else "FULL_DOCUMENT")
    disclosed: dict[str, Any] = {}
    masked: list[str] = []

    if eff_mode == "PREDICATE_ONLY":
        disclosed = {}
        masked = list(attributes.keys())
    elif eff_mode == "SELECTIVE_ATTRIBUTES":
        selected_set = set(custom.selectedAttributes if custom else requirement.attributes)
        for k, v in attributes.items():
            if k in selected_set:
                disclosed[k] = v
            else:
                masked.append(k)
    else:  # FULL_DOCUMENT
        disclosed = dict(attributes)
        masked = []

    return CredentialProofResult(
        credential=requirement.credential,
        verified=verified,
        status=status if verified else VerificationStatus.NOT_VERIFIED,
        issuer=credential["issuer"],
        level=level,
        disclosedAttributes=disclosed,
        predicateResults=predicates,
        maskedAttributes=masked,
        message="Zero-knowledge predicate & credential requirement satisfied."
        if verified
        else "Credential did not satisfy the requirement.",
    )


def _predicate_passes(predicate: Any, attributes: dict[str, Any]) -> bool:
    actual = attributes.get(predicate.attribute)
    if predicate.operator == "EQ":
        return actual == predicate.value
    if predicate.operator == "GTE":
        return actual is not None and actual >= predicate.value
    if predicate.operator == "LTE":
        return actual is not None and actual <= predicate.value
    if predicate.operator == "IN":
        return actual in predicate.value if isinstance(predicate.value, list) else actual == predicate.value
    if predicate.operator == "EXISTS":
        return actual is not None
    return False


def _disclosed_attributes(
    requirement: VerificationRequirement, attributes: dict[str, Any], mode: DisclosureMode
) -> dict[str, Any]:
    if mode == DisclosureMode.MINIMUM:
        requested = requirement.attributes[:1]
    elif mode == DisclosureMode.DOCUMENT_REQUIRED:
        requested = list(attributes)
    else:
        requested = requirement.attributes
    return {key: attributes[key] for key in requested if key in attributes}


def _overall_status(results: list[CredentialProofResult]) -> VerificationStatus:
    if all(item.verified for item in results):
        return VerificationStatus.VERIFIED
    if any(item.verified for item in results):
        return VerificationStatus.PARTIAL
    return VerificationStatus.NOT_VERIFIED


def _disclosure_level(mode: DisclosureMode) -> DisclosureLevel:
    if mode == DisclosureMode.DOCUMENT_REQUIRED:
        return DisclosureLevel.DOCUMENT
    if mode == DisclosureMode.ATTRIBUTE:
        return DisclosureLevel.ATTRIBUTE
    return DisclosureLevel.BOOLEAN


def _shared_fields(results: list[CredentialProofResult], level: DisclosureLevel) -> list[str]:
    if level == DisclosureLevel.BOOLEAN:
        return [f"{item.credential}: verification result" for item in results]
    return [
        f"{item.credential}: {field}"
        for item in results
        for field in item.disclosedAttributes
    ] or [f"{item.credential}: verification result" for item in results]


def _token_claims(
    request: VerificationRequestRecord,
    verification_id: str,
    subject_id: str,
    status: VerificationStatus,
    results: list[CredentialProofResult],
    disclosure_level: DisclosureLevel,
    issued_at: datetime,
    expires_at: datetime,
    predicate_proofs: list[PredicateProofResult] | None = None,
    masked_attributes: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "iss": "DigiIn Synthetic Verification Gateway",
        "sub": subject_id,
        "aud": request.audience,
        "purpose": request.purpose,
        "client_id": request.clientId,
        "request_id": request.requestId,
        "verification_id": verification_id,
        "status": status,
        "disclosure_level": disclosure_level,
        "iat": issued_at.isoformat(),
        "exp": expires_at.isoformat(),
        "nonce": uuid4().hex,
        "credentials": [
            {
                "credential": item.credential,
                "verified": item.verified,
                "status": item.status,
                "issuer": item.issuer,
                "level": item.level,
                "attributes": item.disclosedAttributes,
                "masked_attributes": item.maskedAttributes,
            }
            for item in results
        ],
        "predicate_proofs": [
            {
                "claim": p.claimName,
                "expression": p.expression,
                "satisfied": p.satisfied,
                "proof_type": p.proofType,
            }
            for p in (predicate_proofs or [])
        ],
        "masked_attributes_summary": masked_attributes or [],
    }


def _sign_token(claims: dict[str, Any]) -> str:
    header = {"alg": "HS256", "typ": "VP"}
    header_part = _b64(json.dumps(header, separators=(",", ":")).encode())
    claims_part = _b64(json.dumps(claims, separators=(",", ":"), default=str).encode())
    signature = hmac.new(
        DEMO_SIGNING_KEY, f"{header_part}.{claims_part}".encode(), hashlib.sha256
    ).digest()
    return f"{header_part}.{claims_part}.{_b64(signature)}"


def _verify_token(token: str) -> dict[str, Any] | None:
    try:
        header_part, claims_part, signature_part = token.split(".")
        expected = hmac.new(
            DEMO_SIGNING_KEY, f"{header_part}.{claims_part}".encode(), hashlib.sha256
        ).digest()
        if not hmac.compare_digest(_b64(expected), signature_part):
            return None
        claims = json.loads(_b64decode(claims_part))
        if claims.get("iss") != "DigiIn Synthetic Verification Gateway":
            return None
        return claims
    except (ValueError, json.JSONDecodeError):
        return None


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}".encode())


def _consent_text(payload: VerificationRequestCreate) -> str:
    credentials = ", ".join(item.credential for item in payload.requirements)
    return (
        f"{payload.requesterName} wants to verify {credentials} for {payload.purpose}. "
        "DigiIn will share a purpose-bound proof, not raw documents."
    )


def _expired_result(request: VerificationRequestRecord, subject_id: str) -> VerificationResult:
    now = datetime.now(UTC)
    return _terminal_result(request, subject_id, VerificationStatus.EXPIRED, "Request expired.", now)


def _declined_result(request: VerificationRequestRecord, subject_id: str) -> VerificationResult:
    now = datetime.now(UTC)
    return _terminal_result(request, subject_id, VerificationStatus.NOT_VERIFIED, "Consent declined.", now)


def _terminal_result(
    request: VerificationRequestRecord,
    subject_id: str,
    status: VerificationStatus,
    message: str,
    now: datetime,
) -> VerificationResult:
    result = CredentialProofResult(
        credential="CONSENT",
        verified=False,
        status=status,
        level=0,
        message=message,
    )
    verification_id = f"ver_{uuid4().hex[:12]}"
    claims = _token_claims(
        request=request,
        verification_id=verification_id,
        subject_id=subject_id,
        status=status,
        results=[result],
        disclosure_level=DisclosureLevel.BOOLEAN,
        issued_at=now,
        expires_at=now + timedelta(minutes=5),
    )
    token, key_id, alg = sign_proof_token(claims, algorithm="EdDSA")
    output = VerificationResult(
        verificationId=verification_id,
        requestId=request.requestId,
        status=status,
        subjectId=subject_id,
        audience=request.audience,
        purpose=request.purpose,
        disclosureLevel=DisclosureLevel.BOOLEAN,
        results=[result],
        proof=VerificationProof(token=token, algorithm=alg, keyId=key_id),  # type: ignore[arg-type]
        receipt=VerificationReceipt(
            verificationId=verification_id,
            requesterName=request.requesterName,
            purpose=request.purpose,

            status=status,
            shared=[],
            documentShared=False,
            issuedAt=now,
            expiresAt=now + timedelta(minutes=5),
        ),
        issuedAt=now,
        expiresAt=now + timedelta(minutes=5),
    )
    RESULTS[verification_id] = output
    return output
