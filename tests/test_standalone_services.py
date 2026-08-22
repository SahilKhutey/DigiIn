"""Integration test suite for standalone core services:
1. Sovereign Immutable Audit Ledger (Hash Chaining & Tamper Detection)
2. Document Catalogue & Schema Registry
3. Zero-Knowledge Predicates & Notification Dispatcher
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add services and repo root to sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "services" / "api"))
sys.path.insert(0, str(root_dir))

from services.audit.ledger import SovereignAuditLedger
from services.catalogue.registry import CatalogueService


def test_sovereign_audit_ledger_hash_chaining_and_tamper_detection():
    ledger = SovereignAuditLedger()

    # 1. Check Genesis Block
    assert len(ledger.chain) == 1
    assert ledger.chain[0].event_type == "GENESIS_SOVEREIGN_ROOT"
    assert ledger.chain[0].previous_hash == "0" * 64

    # 2. Append events
    b1 = ledger.append_event(
        event_type="DOCUMENT_UPLOADED",
        aggregate_id="doc_rahul_001",
        actor="subj_rahul_99",
        message="Class XII marksheet uploaded.",
    )
    assert b1.index == 1
    assert b1.previous_hash == ledger.chain[0].hash

    b2 = ledger.append_event(
        event_type="OFFICER_APPROVED",
        aggregate_id="doc_rahul_001",
        actor="officer_cbse_01",
        message="Level 4 verified credential minted.",
    )
    assert b2.index == 2
    assert b2.previous_hash == b1.hash

    # 3. Verify Chain Integrity -> Valid
    valid, err = ledger.verify_chain_integrity()
    assert valid is True
    assert err is None

    # 4. Tamper Test: Modify message of block 1
    b1.message = "TAMPERED: Altered message to forge audit logs."
    valid_tampered, err_tampered = ledger.verify_chain_integrity()
    assert valid_tampered is False
    assert "Tampered block detected" in err_tampered


def test_document_catalogue_and_schema_validation():
    catalogue = CatalogueService()

    # 1. List Schemas
    schemas = catalogue.list_schemas()
    assert len(schemas) >= 3
    schema_ids = [s.schema_id for s in schemas]
    assert "CLASS_XII" in schema_ids
    assert "LAND_RECORD" in schema_ids
    assert "DRIVING_LICENCE" in schema_ids

    # 2. Validate Valid Claims
    valid_claims = {
        "student_name": "RAHUL SHARMA",
        "roll_number": "CBSE-2026-99214",
        "passing_year": 2026,
        "percentage": 94.2,
        "board": "CBSE",
    }
    is_valid, errors = catalogue.validate_claims_against_schema("CLASS_XII", valid_claims)
    assert is_valid is True
    assert len(errors) == 0

    # 3. Validate Invalid Claims (Missing roll_number)
    invalid_claims = {
        "student_name": "RAHUL SHARMA",
        "percentage": 94.2,
    }
    is_valid_bad, errors_bad = catalogue.validate_claims_against_schema("CLASS_XII", invalid_claims)
    assert is_valid_bad is False
    assert any("roll_number" in err for err in errors_bad)


if __name__ == "__main__":
    test_sovereign_audit_ledger_hash_chaining_and_tamper_detection()
    test_document_catalogue_and_schema_validation()
    print("SUCCESS: ALL STANDALONE CORE SERVICES TESTS PASSED!")
