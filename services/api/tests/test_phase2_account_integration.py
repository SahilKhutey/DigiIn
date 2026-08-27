"""
Phase 2 — DigiIn Account ID Integration Test Matrix.

Verifies:
1. Central AccountIdentityService abstraction.
2. Integration across User, Documents, Credentials, and Verifications.
3. Controlled account lookup and anti-enumeration.
4. Database integrity constraints (1:1 Account to ID, 1:N resources).
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.core.ids import generate_account_id, is_valid_account_id
from app.db.session import get_db_session
from app.main import app
from app.models.entities import Credential, Document, User, VerificationRequest
from app.services.account_identity_service import account_identity_service


def test_account_identity_service_resolution():
    """Validates resolution of account by internal UUID and public DigiIn ID."""
    with get_db_session() as db:
        # Create a test citizen
        test_acc_id = generate_account_id()
        user = User(
            email=f"p2_user_{test_acc_id.replace('-', '_')}@example.com",
            password_hash="hashed_pw",
            digiin_account_id=test_acc_id,
        )
        db.add(user)
        db.flush()

        # 1. Resolve by internal UUID
        resolved_by_uuid = account_identity_service.get_account_by_internal_id(db, user.id)
        assert resolved_by_uuid is not None
        assert resolved_by_uuid.digiin_account_id == test_acc_id

        # 2. Resolve by DigiIn Public ID (case-insensitive)
        resolved_by_id = account_identity_service.get_account_by_digiin_id(db, test_acc_id.lower())
        assert resolved_by_id is not None
        assert resolved_by_id.id == user.id

        # 3. Check existence
        assert account_identity_service.account_exists(db, test_acc_id) is True
        assert account_identity_service.account_exists(db, "DI-9999-9999-9999") is False

        # Cleanup
        db.delete(user)


def test_database_integrity_1_to_1_and_unique_constraint():
    """Proves 1 Account -> 1 DigiIn ID, and prevents 1 DigiIn ID -> 2 Accounts."""
    with get_db_session() as db:
        duplicate_id = generate_account_id()
        user1 = User(
            email=f"user1_{duplicate_id.replace('-', '_')}@example.com",
            password_hash="hashed_pw",
            digiin_account_id=duplicate_id,
        )
        db.add(user1)
        db.flush()

        # Attempting to assign same digiin_account_id to user2 must fail IntegrityError
        user2 = User(
            email=f"user2_{duplicate_id.replace('-', '_')}@example.com",
            password_hash="hashed_pw",
            digiin_account_id=duplicate_id,
        )
        db.add(user2)
        with pytest.raises(IntegrityError):
            db.flush()

        db.rollback()


def test_resource_relationships_preserve_foreign_keys():
    """Validates 1 Account -> N Documents, N Credentials, N Verification Requests."""
    with get_db_session() as db:
        test_acc_id = generate_account_id()
        user = User(
            email=f"rel_{test_acc_id.replace('-', '_')}@example.com",
            password_hash="hashed_pw",
            digiin_account_id=test_acc_id,
        )
        db.add(user)
        db.flush()

        # Add 2 documents
        doc1 = Document(user_id=user.id, document_type="CLASS_12_MARKSHEET", title="CBSE Marksheet")
        doc2 = Document(user_id=user.id, document_type="INCOME_CERTIFICATE", title="Income Cert")
        db.add_all([doc1, doc2])

        # Add 1 credential
        cred = Credential(
            user_id=user.id,
            credential_type="DEGREE",
            issuer_id="CBSE",
            holder_name="Rahul",
            passing_year=2026,
        )
        db.add(cred)

        # Add 1 verification request
        v_req = VerificationRequest(
            user_id=user.id,
            requester_name="Delhi University",
            credential_type="DEGREE",
            purpose="Admission",
        )
        db.add(v_req)
        db.flush()

        # Query identity summary via service
        summary = account_identity_service.get_public_identity(db, test_acc_id, authenticated_actor=user)
        assert summary is not None
        assert summary["linked_documents_count"] >= 2
        assert summary["verified_credentials_count"] >= 1
        assert summary["verification_requests_count"] >= 1
        assert summary["is_owner"] is True

        db.rollback()


def test_me_identity_endpoint():
    """Validates GET /api/v1/me/identity endpoint."""
    client = TestClient(app)
    r = client.get("/api/v1/me/identity")
    assert r.status_code == 200
    data = r.json()
    assert "digiin_account_id" in data
    assert is_valid_account_id(data["digiin_account_id"])
    assert "account_status" in data
    assert "identity_status" in data


def test_controlled_account_lookup_and_anti_enumeration():
    """Validates GET /api/v1/accounts/{digiin_account_id} error states and permissions."""
    client = TestClient(app)

    # 1. Malformed ID returns 400 with helpful format guidance
    r_bad = client.get("/api/v1/accounts/INVALID-FORMAT-123")
    assert r_bad.status_code == 400
    assert "INVALID_ID" in r_bad.json()["detail"]

    # 2. Non-existent valid format returns 404 uniform response
    r_not_found = client.get("/api/v1/accounts/DI-9999-9999-9999")
    assert r_not_found.status_code == 404
    assert "ACCOUNT_NOT_FOUND" in r_not_found.json()["detail"]
