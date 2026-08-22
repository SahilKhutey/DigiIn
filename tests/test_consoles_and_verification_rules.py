"""Integration test suite for:
1. Advanced Zero-Knowledge Predicate Rules Engine
2. Multi-Channel Notification Dispatcher
3. Government Queues and Verifier Policy Endpoints
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add services to sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "services" / "api"))
sys.path.insert(0, str(root_dir))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from services.verification.rules import PredicateRule, evaluate_predicate_condition, score_evidence_match
from services.verification.engine import VerificationEngine
from services.notification.dispatcher import NotificationDispatcher


def test_zero_knowledge_predicate_evaluations():
    attributes = {
        "percentage": 94.2,
        "age": 20,
        "passing_year": 2026,
        "state": "CHHATTISGARH",
        "qualification": "CLASS_XII",
    }

    # 1. GTE Rule (percentage >= 60.0) -> True
    rule_gte = PredicateRule(attribute="percentage", operator="GTE", value=60.0)
    assert evaluate_predicate_condition(rule_gte, attributes) is True

    # 2. GTE Rule (percentage >= 98.0) -> False
    rule_gte_fail = PredicateRule(attribute="percentage", operator="GTE", value=98.0)
    assert evaluate_predicate_condition(rule_gte_fail, attributes) is False

    # 3. EQUALS Rule (state == CHHATTISGARH) -> True
    rule_eq = PredicateRule(attribute="state", operator="EQUALS", value="Chhattisgarh")
    assert evaluate_predicate_condition(rule_eq, attributes) is True

    # 4. IN Rule (qualification in [CLASS_XII, BTECH]) -> True
    rule_in = PredicateRule(attribute="qualification", operator="IN", value=["CLASS_XII", "BTECH"])
    assert evaluate_predicate_condition(rule_in, attributes) is True

    # 5. BETWEEN Rule (passing_year between 2020 and 2026) -> True
    rule_between = PredicateRule(attribute="passing_year", operator="BETWEEN", value=[2020, 2026])
    assert evaluate_predicate_condition(rule_between, attributes) is True


def test_verification_engine_composite_evaluation():
    engine = VerificationEngine()
    attributes = {
        "roll_number": "26182910",
        "student_name": "RAHUL SHARMA",
        "passing_year": 2026,
        "percentage": 94.2,
        "board": "CBSE",
    }
    registry = {
        "roll_number": "26182910",
        "student_name": "RAHUL SHARMA",
        "passing_year": 2026,
        "board": "CBSE",
    }

    # 1. Match Evaluation
    match_res = engine.evaluate_match(attributes, registry)
    assert match_res["verdict"] == "VERIFIED"
    assert match_res["verificationLevel"] == 4
    assert match_res["score"] == 100.0

    # 2. Predicates Evaluation
    rules = [
        PredicateRule(attribute="percentage", operator="GTE", value=75.0),
        PredicateRule(attribute="board", operator="EQUALS", value="CBSE"),
    ]
    pred_res = engine.evaluate_predicates(rules, attributes)
    assert pred_res["allSatisfied"] is True
    assert len(pred_res["predicateResults"]) == 2
    assert pred_res["disclosureLevel"] == "BOOLEAN_PREDICATE_ONLY"


@pytest.mark.asyncio
async def test_notification_dispatcher_lifecycle_events():
    dispatcher = NotificationDispatcher()

    # 1. Dispatch CONSENT_REQUESTED event
    rec1 = await dispatcher.dispatch_event(
        event_type="CONSENT_REQUESTED",
        user_id="user_12345",
        template_params={"requester_name": "NTA Examination", "credential_type": "Class XII Passing Certificate"},
        channel="WHATSAPP",
    )
    assert rec1["status"] == "DELIVERED"
    assert "NTA Examination" in rec1["message"]

    # 2. Dispatch VERIFICATION_COMPLETED event
    rec2 = await dispatcher.dispatch_event(
        event_type="VERIFICATION_COMPLETED",
        user_id="user_12345",
        template_params={"requester_name": "NTA Examination", "credential_type": "Class XII Passing Certificate"},
        channel="SMS",
    )
    assert rec2["status"] == "DELIVERED"
    assert len(dispatcher.dispatched_history) == 2


def test_consoles_api_integration():
    client = TestClient(app)

    # 1. Issuer Queues Endpoint
    queues_res = client.get("/api/v1/government/queues")
    assert queues_res.status_code == 200
    queues = queues_res.json()
    assert len(queues) >= 4

    # 2. Cases in CBSE Queue
    cases_res = client.get("/api/v1/government/cases?queue=queue_cbse")
    assert cases_res.status_code == 200
    cases = cases_res.json()
    assert isinstance(cases, list)

    # 3. JWKS Discovery Endpoint
    jwks_res = client.get("/.well-known/jwks.json")
    assert jwks_res.status_code == 200
    jwks = jwks_res.json()
    assert "keys" in jwks
    assert len(jwks["keys"]) == 2

    # 4. Platform Snapshot Endpoint
    snap_res = client.get("/api/v1/platform/snapshot")
    assert snap_res.status_code == 200
    snap = snap_res.json()
    assert "featureFlags" in snap
    assert "events" in snap


if __name__ == "__main__":
    import asyncio
    test_zero_knowledge_predicate_evaluations()
    test_verification_engine_composite_evaluation()
    asyncio.run(test_notification_dispatcher_lifecycle_events())
    test_consoles_api_integration()
    print("SUCCESS: ALL CONSOLES AND VERIFICATION RULES TESTS PASSED!")
