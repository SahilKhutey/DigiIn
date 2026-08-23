"""
DigiIn Automated National-Scale Operations & Infrastructure Test Suite (Phase 29)
Validates Multi-Region Routing, Disaster Recovery Drills, Isolated Queues, SOC Threat Detection, Chaos Safe-Failure Semantics, and National Flagship E2E Workflow.
"""

import sys
import os

# Add services/api to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'services', 'api')))

from app.core.national_scale import (
    NationalTrafficRouter,
    RegionStatus,
    RequestTier,
    TrafficPriority,
    DisasterRecoveryManager,
    RecoveryTier,
    NationalQueueEngine,
    SecurityOperationsCenter,
    ThreatSeverity,
    NetworkRiskGraphEngine,
    ComplianceOperationsManager,
    ChaosTestRunner,
    NationalLoadHarness,
    NationalOperationsDashboard,
)
from app.core.trust_network import (
    IssuerRegistry,
    VerifierRegistry,
    ClaimSchemaRegistry,
    ClaimIssuanceEngine,
    ClaimPresentationEngine,
    TrustProtocolAdapter,
    ClaimStatus,
)

def test_multi_region_routing_and_automated_drain():
    print(">>> 1. Testing Multi-Region Routing & Automated Failover Draining...")
    router = NationalTrafficRouter()

    # 1. Primary region is healthy -> ROUTED_TO_PRIMARY_REGION
    ok1, reg1, msg1 = router.route_request("in-west-mumbai", RequestTier.INSTITUTIONAL, TrafficPriority.P1_VERIFICATION)
    assert ok1 is True
    assert reg1 == "in-west-mumbai"
    assert "PRIMARY" in msg1

    # 2. Mark Mumbai degraded -> Automated failover to healthy region (Hyderabad / Delhi)
    router.mark_region_degraded("in-west-mumbai")
    ok2, reg2, msg2 = router.route_request("in-west-mumbai", RequestTier.INSTITUTIONAL, TrafficPriority.P1_VERIFICATION)
    assert ok2 is True
    assert reg2 in ("in-south-hyderabad", "in-north-delhi")
    assert "FAILOVER_DRAINED" in msg2

    # Restore Mumbai
    router.restore_region("in-west-mumbai")
    assert router._regions["in-west-mumbai"].status == RegionStatus.ACTIVE
    print("    [PASS] Multi-region routing and automated failover draining verified")

def test_disaster_recovery_and_restore_drills():
    print(">>> 2. Testing Disaster Recovery Manager & Restore Integrity Drills...")
    dr_mgr = DisasterRecoveryManager()

    # 1. Register backup
    bkp = dr_mgr.register_backup(
        backup_class="IMMUTABLE_AUDIT",
        size_bytes=104857600,
        checksum="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )
    assert bkp.verified is True

    # 2. Execute restore drill
    passed_drill, drill_res = dr_mgr.execute_restore_drill(bkp.backup_id)
    assert passed_drill is True
    assert drill_res.integrity_verified is True
    assert drill_res.actual_rto_seconds < 5.0
    print("    [PASS] Disaster recovery policies and automated restore drills verified")

def test_isolated_queues_and_dlq():
    print(">>> 3. Testing Isolated Durable Queues & Dead Letter Queue (DLQ)...")
    queue_engine = NationalQueueEngine()

    # 1. Enqueue verification event
    job = queue_engine.enqueue("verification-events", {"verificationId": "vreq_9981"}, priority=1)
    assert queue_engine.get_queue_depth("verification-events") == 1

    # 2. Successful execution
    ok_p, _ = queue_engine.process_job(job, simulate_success=True)
    assert ok_p is True
    assert queue_engine.get_queue_depth("verification-events") == 0

    # 3. Repeated failure -> Route to DLQ
    failing_job = queue_engine.enqueue("notification-events", {"userId": "usr_998"}, priority=2)
    queue_engine.process_job(failing_job, simulate_success=False)  # retry 1
    queue_engine.process_job(failing_job, simulate_success=False)  # retry 2
    ok_fail_dlq, msg_dlq = queue_engine.process_job(failing_job, simulate_success=False)  # retry 3 -> DLQ

    assert ok_fail_dlq is False
    assert "DEAD_LETTER" in msg_dlq
    assert queue_engine.get_queue_depth("dead-letter-queue") == 1
    print("    [PASS] Isolated durable queues and DLQ escalation verified")

def test_soc_threat_detection_and_risk_graph():
    print(">>> 4. Testing Security Operations Center (SOC) & Fraud Risk Graph...")
    soc = SecurityOperationsCenter()
    risk_graph = NetworkRiskGraphEngine()

    # 1. Ingest Critical Threat Event -> Automatically Triggers SOC Alert
    evt = soc.ingest_event(
        event_type="TOKEN_REPLAY_ATTEMPT",
        severity=ThreatSeverity.CRITICAL,
        actor_id="bad_actor_ip_99",
        organization_id="org_suspicious_bot",
        details={"replayedTokenId": "tok_991823"}
    )
    alerts = soc.list_open_alerts()
    assert len(alerts) >= 1
    assert alerts[0].rule_name == "CRITICAL_TOKEN_REPLAY_OR_ABUSE"

    # 2. Risk Graph Node Evaluation
    risk_graph.record_verification_node("iss_du", "ver_scholarship", "education.degree", success=True)
    level, score = risk_graph.evaluate_risk_level("ver_scholarship")
    assert level == "LOW_RISK"
    assert score <= 0.1
    print("    [PASS] Security Operations Center threat detection & risk graph verified")

def test_chaos_safe_failure_invariants():
    print(">>> 5. Testing Chaos Invariants: Degraded Dependency NEVER Yields False Verified...")
    # Invariant 1: Provider database drop drill
    drill1 = ChaosTestRunner.simulate_provider_outage()
    assert drill1.passed is True
    assert drill1.no_false_positives is True

    # Invariant 2: Regional network partition drill
    drill2 = ChaosTestRunner.simulate_regional_network_partition()
    assert drill2.passed is True
    assert drill2.safe_failure_guaranteed is True

    # Synthetic Load Spike Simulation
    load_res = NationalLoadHarness.run_synthetic_load_spike(request_count=10000)
    assert load_res["systemStability"] == "STABLE"
    assert load_res["processedRequests"] >= 9500
    print("    [PASS] Chaos safe-failure invariants and synthetic load simulation verified")

def test_flagship_national_scale_e2e_scenario():
    print(">>> 6. Testing Flagship National-Scale Workflow Scenario...")
    # Multi-Region Route -> Autoscale & Throttle -> Region Drain -> Verification Continues -> Revocation Propagation
    router = NationalTrafficRouter()
    iss_reg = IssuerRegistry()
    ver_reg = VerifierRegistry()
    schema_reg = ClaimSchemaRegistry()
    issuance_engine = ClaimIssuanceEngine(iss_reg, schema_reg)
    pres_engine = ClaimPresentationEngine(ver_reg, issuance_engine)
    adapter = TrustProtocolAdapter(iss_reg, ver_reg, schema_reg, issuance_engine, pres_engine)

    # 1. Multi-region route to Mumbai
    ok_r, target_reg, _ = router.route_request("in-west-mumbai", RequestTier.INSTITUTIONAL, TrafficPriority.P1_VERIFICATION)
    assert ok_r is True

    # 2. Issue National Verified Claim
    ok_iss, _, claim = adapter.issue_claim(
        issuer_id="iss_delhi_university",
        subject_id="DGI-7K4M-X9P2",
        claim_type="education.degree",
        payload={"degree": "B.Tech Computer Science", "institution": "University of Delhi", "year": 2025}
    )
    assert ok_iss is True

    # 3. Simulate Regional Outage on Mumbai -> Drain to Hyderabad
    router.mark_region_degraded("in-west-mumbai")
    ok_drain, drained_reg, _ = router.route_request("in-west-mumbai", RequestTier.INSTITUTIONAL, TrafficPriority.P1_VERIFICATION)
    assert drained_reg in ("in-south-hyderabad", "in-north-delhi")

    # 4. Presentation & Verification continue seamlessly in failover region
    nonce = "nonce_national_failover_demo"
    ok_pres, _, pres = adapter.present_claim("DGI-7K4M-X9P2", "ver_scholarship_portal", "SCHOLARSHIP_ELIGIBILITY", [claim.id], nonce)
    assert ok_pres is True

    ok_ver, _ = adapter.verify_claim(pres, "ver_scholarship_portal", "SCHOLARSHIP_ELIGIBILITY", nonce)
    assert ok_ver is True

    # 5. Revocation propagates authoritative status
    issuance_engine.revoke_claim(claim.id, reason="AUTHORITATIVE_UPDATE")
    assert adapter.check_status(claim.id)["status"] == "REVOKED"
    print("    [PASS] Flagship national-scale failover, verification & revocation propagation verified")

def run_all_national_scale_tests():
    print("=" * 80)
    print("DIGIIN PHASE 29 NATIONAL-SCALE OPERATIONS & INFRASTRUCTURE TEST MATRIX")
    print("=" * 80)
    test_multi_region_routing_and_automated_drain()
    test_disaster_recovery_and_restore_drills()
    test_isolated_queues_and_dlq()
    test_soc_threat_detection_and_risk_graph()
    test_chaos_safe_failure_invariants()
    test_flagship_national_scale_e2e_scenario()
    print("=" * 80)
    print("SUCCESS: ALL 6 NATIONAL-SCALE OPERATIONS & INFRASTRUCTURE TESTS PASSED (100%)")
    print("=" * 80)

if __name__ == "__main__":
    run_all_national_scale_tests()
