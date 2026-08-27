"""
DigiIn Account Identity Service — Central Identity Abstraction.

Manages resolution between internal system identities (UUID primary keys)
and citizen-facing public DigiIn Account IDs (DI-7K4M-9Q2X-8P6R).
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.ids import (
    generate_account_id,
    is_valid_account_id,
)
from app.models.entities import (
    Credential,
    Document,
    User,
    VerificationRequest,
)


class AccountIdentityService:
    """Central abstraction for resolving, verifying, and guarding DigiIn Account Identities."""

    @staticmethod
    def generate_id() -> str:
        """Generate a cryptographically secure, Base32 DigiIn Account ID (DI-XXXX-XXXX-XXXX)."""
        return generate_account_id()

    @staticmethod
    def validate_id(digiin_account_id: str) -> bool:
        """Validate format, Base32 alphabet, and DI- prefix."""
        return is_valid_account_id(digiin_account_id)

    @staticmethod
    def get_account_by_internal_id(db: Session, internal_id: str) -> User | None:
        """Resolve database user by internal UUID primary key."""
        return db.query(User).filter(User.id == internal_id).first()

    @staticmethod
    def get_account_by_digiin_id(db: Session, digiin_account_id: str) -> User | None:
        """Resolve database user by public DigiIn Account ID."""
        if not is_valid_account_id(digiin_account_id):
            return None
        cleaned_id = digiin_account_id.strip().upper()
        return db.query(User).filter(User.digiin_account_id == cleaned_id).first()

    @staticmethod
    def account_exists(db: Session, digiin_account_id: str) -> bool:
        """Check if an account ID exists without returning the record."""
        if not is_valid_account_id(digiin_account_id):
            return False
        cleaned_id = digiin_account_id.strip().upper()
        return db.query(User.id).filter(User.digiin_account_id == cleaned_id).first() is not None

    @staticmethod
    def get_public_identity(
        db: Session,
        digiin_account_id: str,
        authenticated_actor: User | None = None,
    ) -> dict[str, Any] | None:
        """Return controlled public identity representation based on authorization."""
        user = AccountIdentityService.get_account_by_digiin_id(db, digiin_account_id)
        if not user:
            return None

        # Check authorization: Own account, admin, or basic public status
        is_owner = authenticated_actor and authenticated_actor.id == user.id
        is_admin = authenticated_actor and authenticated_actor.role == "ADMIN"

        if is_owner or is_admin:
            # Full authorized identity representation
            doc_count = db.query(func.count(Document.id)).filter(Document.user_id == user.id).scalar() or 0
            cred_count = db.query(func.count(Credential.id)).filter(Credential.user_id == user.id).scalar() or 0
            req_count = db.query(func.count(VerificationRequest.id)).filter(VerificationRequest.user_id == user.id).scalar() or 0

            return {
                "digiin_account_id": user.digiin_account_id,
                "account_status": user.status.lower(),
                "identity_status": "verified" if cred_count > 0 else "active",
                "linked_documents_count": doc_count,
                "verified_credentials_count": cred_count,
                "verification_requests_count": req_count,
                "role": user.role,
                "is_owner": is_owner,
            }

        # For third parties: minimal non-leaking status representation
        return {
            "digiin_account_id": user.digiin_account_id,
            "account_status": "active" if user.status == "ACTIVE" else "inactive",
            "identity_status": "verified",
        }


# Singleton helper instance
account_identity_service = AccountIdentityService()
