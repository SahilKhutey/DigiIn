"""Transaction diagnosis, recovery policy, and synthetic failure scenarios."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from app.domain.models import (
    FailureCode,
    RecoveryAction,
    ScenarioSummary,
    SupportSafeSummary,
    TransactionDiagnosis,
    TransactionState,
    TransactionStep,
)


def step(name: str, status: str, message: str, owner: str, action: str | None = None) -> TransactionStep:
    return TransactionStep(name=name, status=status, message=message, owner=owner, nextAction=action)  # type: ignore[arg-type]


SCENARIOS: dict[str, tuple[ScenarioSummary, TransactionDiagnosis]] = {
    "identity-mismatch": (ScenarioSummary(id="identity-mismatch", title="Identity details do not match", description="The issuer record cannot be matched to the supplied details."), TransactionDiagnosis(transactionId="demo-cbse-2026", documentLabel="Class XII marksheet (demonstration)", trustLabel="Government issued", state=TransactionState.FAILED, overallStatus="action_required", issueCode=FailureCode.IDENTITY_MISMATCH, issuerStatus="available", summary="The issuer responded, but its record could not be matched to the request details.", steps=[step("Account access", "complete", "The official sign-in step was completed.", "Citizen / official service"), step("Identity match", "attention", "The issuer could not match the name, date of birth or document year.", "Issuing organisation", "Check these fields against the issuer record and use its official correction route if needed."), step("Document retrieval", "not_started", "Retrieval starts after the identity record matches.", "Document platform / issuer")], recovery=RecoveryAction(label="Correct the issuer record", type="correct_record", guidance="DigiIn cannot change an official record. Confirm the record with the issuer, then start a new official retrieval attempt."), fallbackAvailable=False, supportReference="DIGIIN-DEMO-IM-2026")),
    "issuer-unavailable": (ScenarioSummary(id="issuer-unavailable", title="Issuer service is unavailable", description="The document issuer cannot currently respond to a lookup."), TransactionDiagnosis(transactionId="demo-issuer-2026", documentLabel="Class XII marksheet (demonstration)", trustLabel="Government issued", state=TransactionState.FAILED, overallStatus="unavailable", issueCode=FailureCode.ISSUER_TIMEOUT, issuerStatus="unavailable", summary="The issuing organisation is not responding to document lookup requests.", steps=[step("Account access", "complete", "The official sign-in step was completed.", "Citizen / official service"), step("Issuer lookup", "blocked", "The issuer service is temporarily unavailable.", "Issuing organisation", "Retry later or use the issuer's official support route if the document is urgent."), step("Document retrieval", "not_started", "Retrieval cannot start until the issuer responds.", "Document platform / issuer")], recovery=RecoveryAction(label="Use an official fallback", type="official_fallback", guidance="Use the issuer's official website or support channel. A production configuration would show an authorised issuer-specific route."), fallbackAvailable=True, supportReference="DIGIIN-DEMO-IU-2026")),
    "callback-failed": (ScenarioSummary(id="callback-failed", title="Requesting portal did not receive confirmation", description="Authorisation succeeded, but the destination portal did not complete handoff."), TransactionDiagnosis(transactionId="demo-callback-2026", documentLabel="Verified marksheet (demonstration)", trustLabel="Government issued", state=TransactionState.FAILED, overallStatus="action_required", issueCode=FailureCode.CALLBACK_FAILED, issuerStatus="available", summary="The document was authorised, but the requesting portal did not confirm receipt.", steps=[step("Account access", "complete", "The official sign-in step was completed.", "Citizen / official service"), step("Document retrieval", "complete", "The issued document was located and authorised.", "Document platform / issuer"), step("Destination handoff", "attention", "The requesting portal did not confirm receipt.", "Requesting service", "Return to the requesting portal and start its official handoff flow once more.")], recovery=RecoveryAction(label="Return to the requesting portal", type="return_to_requester", guidance="The requesting service owns this step. If it repeats, contact its support with the safe reference below."), fallbackAvailable=False, supportReference="DIGIIN-DEMO-CB-2026")),
    "resolved": (ScenarioSummary(id="resolved", title="Document journey completed", description="A complete end-to-end issued-document journey."), TransactionDiagnosis(transactionId="demo-resolved-2026", documentLabel="Driving licence (demonstration)", trustLabel="Government issued", state=TransactionState.COMPLETED, overallStatus="resolved", issueCode=FailureCode.JOURNEY_COMPLETE, issuerStatus="available", summary="The official document was located, verified and received by the requesting service.", steps=[step("Account access", "complete", "The official sign-in step was completed.", "Citizen / official service"), step("Document retrieval", "complete", "The issued document was found and verified.", "Document platform / issuer"), step("Destination handoff", "complete", "The requesting service confirmed receipt.", "Requesting service")], recovery=RecoveryAction(label="Journey complete", type="retry_later", guidance="No recovery action is needed for this demonstration journey."), fallbackAvailable=False, supportReference="DIGIIN-DEMO-OK-2026")),
}


def get_diagnosis(scenario_id: str) -> TransactionDiagnosis | None:
    scenario = SCENARIOS.get(scenario_id)
    return scenario[1] if scenario else None


def list_scenarios() -> list[ScenarioSummary]:
    return [item[0] for item in SCENARIOS.values()]


def generate_support_summary(scenario_id: str) -> SupportSafeSummary | None:
    diag = get_diagnosis(scenario_id)
    if diag is None:
        return None
    now = datetime.now(UTC)

    code_hash = hashlib.sha256(f"{scenario_id}_{diag.transactionId}".encode()).hexdigest().upper()
    support_code = f"DIGIIN-REC-{code_hash[:4]}-{code_hash[4:8]}"
    correlation_id = f"corr_{code_hash[8:20].lower()}"

    if scenario_id == "identity-mismatch":
        failure_stage = "IDENTITY_MATCH_MISMATCH"
        diagnostic_title = "Identity Discrepancy with Issuing Authority Record"
        plain_lang = (
            "The document issuer (CBSE Examination Registry) responded successfully, but "
            "the student name, date of birth or roll number in the request does not exactly match "
            "the authoritative board register. DigiIn cannot alter official state records."
        )
        affected_auth = "Central Board of Secondary Education (CBSE)"
        issuer_status = "OPERATIONAL (200 OK)"
        citizen_guidance = [
            "Verify the exact spelling of your full name on your official Admit Card and secondary certificate.",
            "If your name contains a typographical error in the board register, initiate an official Correction Request via the 'Correct record' tab.",
            "Present this Support Code at your university admission or facilitation desk for manual discrepancy logging.",
        ]
        officer_guidance = [
            "Check student identity against secondary gazette / Class X certificate transcript.",
            "Verify if an approved Correction Version (v2) has been issued in the DigiIn Verifier Console.",
            "Do NOT request raw password credentials or OTP from the candidate.",
        ]
    elif scenario_id == "issuer-unavailable":
        failure_stage = "ISSUER_GATEWAY_TIMEOUT"
        diagnostic_title = "Upstream Issuing Authority Service Unavailable"
        plain_lang = (
            "The departmental document lookup gateway (MoRTH / State Registry) is temporarily "
            "unreachable or undergoing maintenance. Your credentials and request parameters are intact."
        )
        affected_auth = "Ministry of Road Transport & Highways (MoRTH)"
        issuer_status = "DEGRADED / 503 SERVICE UNAVAILABLE"
        citizen_guidance = [
            "The issuing department server is temporarily down. Please retry after 30–60 minutes.",
            "If immediate verification is required for admission/licence renewal, present this summary to the desk officer.",
            "No data was lost or compromised during this connection timeout.",
        ]
        officer_guidance = [
            "Verify MoRTH Sarathi API health status on the State Gateway dashboard.",
            "If upstream outage persists, accept signed offline credential proof or schedule secondary verification batch.",
        ]
    elif scenario_id == "callback-failed":
        failure_stage = "DESTINATION_HANDOFF_TIMEOUT"
        diagnostic_title = "Relying Party Portal Handshake Incomplete"
        plain_lang = (
            "The document was successfully authenticated and authorized by DigiIn, but the destination "
            "portal (e.g. university application server) failed to confirm receipt of the verification token."
        )
        affected_auth = "Relying Party Application Gateway"
        issuer_status = "OPERATIONAL (DigiIn Gateway Healthy)"
        citizen_guidance = [
            "Your document verification was successful in DigiIn.",
            "Return to the requesting university/employer portal and re-trigger the 'Verify with DigiIn' button.",
            "Check if your session on the receiving portal has timed out.",
        ]
        officer_guidance = [
            "Verify if the callback webhook URL on the requesting application is responding with HTTP 200.",
            "Introspect the verification token using the DigiIn Verification Gateway using token ID.",
        ]
    else:  # resolved or generic
        failure_stage = "JOURNEY_COMPLETED_HEALTHY"
        diagnostic_title = "Verification Journey Completed Successfully"
        plain_lang = "All transaction stages, issuer lookups, and token handoffs completed with verified authenticity."
        affected_auth = "All Integrated Issuers"
        issuer_status = "OPERATIONAL"
        citizen_guidance = ["No corrective action required. Your verified credential proof is active."]
        officer_guidance = ["Verification token is valid and active. Proceed with standard processing."]

    qr_digest = f"DIGIIN://VERIFY?code={support_code}&corr={correlation_id}&auth={affected_auth}&stage={failure_stage}"

    return SupportSafeSummary(
        supportCode=support_code,
        timestamp=now,
        scenarioId=scenario_id,
        failureStage=failure_stage,
        diagnosticTitle=diagnostic_title,
        plainLanguageExplanation=plain_lang,
        affectedAuthority=affected_auth,
        issuerStatus=issuer_status,
        correlationId=correlation_id,
        guidanceForCitizen=citizen_guidance,
        guidanceForDeskOfficer=officer_guidance,
        securityNotice="SECURITY & PRIVACY GUARANTEE: This summary contains zero personal passwords, OTPs, or raw identity numbers. Safe for public service desk inspection.",
        qrDigest=qr_digest,
    )

