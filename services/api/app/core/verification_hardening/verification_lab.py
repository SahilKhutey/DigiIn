"""
DigiIn Verification Hardening — Verification Lab & Test Harness
Powers /admin/verification-lab and /dev/verification for live interactive judging and evidence extraction.
"""

from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass

from .cryptographic_fixtures import CryptographicFixtureRegistry
from .negative_proof_engine import NegativeProofEngine, VerificationEvaluationResult


@dataclass
class VerificationLabTestCase:
    test_id: str
    name: str
    description: str
    expected_status: str
    actual_result: VerificationEvaluationResult

class VerificationLabService:
    def __init__(self):
        self.fixtures = CryptographicFixtureRegistry()
        self.trust_registry = ["org_delhi_university", "org_cbse_board", "org_ministry_transport"]

    def run_all_lab_tests(self) -> list[VerificationLabTestCase]:
        base_cred = CryptographicFixtureRegistry.create_sample_degree_credential()
        base_digest = hashlib.sha256(NegativeProofEngine.canonicalize(base_cred)).hexdigest()
        keypair = self.fixtures.get_keypair("key_delhi_univ_ed25519_2026")

        results = []

        # 1. Valid Credential Test
        res_valid = NegativeProofEngine.evaluate_credential_integrity(
            base_cred, "sig_valid_hex", base_digest, keypair, self.trust_registry
        )
        results.append(VerificationLabTestCase(
            test_id="TC-01",
            name="Valid Authentic Credential",
            description="Authentic degree issued by University of Delhi with matching cryptographic digest",
            expected_status="VERIFIED",
            actual_result=res_valid
        ))

        # 2. Tampered Credential Test (Modified Grade)
        tampered_cred = copy.deepcopy(base_cred)
        tampered_cred["claims"]["degree"] = "Master of Science in Artificial Intelligence (Tampered)"
        res_tampered = NegativeProofEngine.evaluate_credential_integrity(
            tampered_cred, "sig_valid_hex", base_digest, keypair, self.trust_registry
        )
        results.append(VerificationLabTestCase(
            test_id="TC-02",
            name="Tampered Credential (Modified Claims)",
            description="Claims modified after issuance; SHA-256 digest fails verification",
            expected_status="INVALID",
            actual_result=res_tampered
        ))

        # 3. Untrusted Issuer Test
        untrusted_cred = copy.deepcopy(base_cred)
        untrusted_cred["issuerId"] = "org_unaccredited_bogus_college"
        untrusted_digest = hashlib.sha256(NegativeProofEngine.canonicalize(untrusted_cred)).hexdigest()
        res_untrusted = NegativeProofEngine.evaluate_credential_integrity(
            untrusted_cred, "sig_valid_hex", untrusted_digest, keypair, self.trust_registry
        )
        results.append(VerificationLabTestCase(
            test_id="TC-03",
            name="Untrusted Issuer (Unaccredited)",
            description="Issuer not registered in the National Trust Registry",
            expected_status="UNTRUSTED",
            actual_result=res_untrusted
        ))

        # 4. Revoked Credential Test
        revoked_cred = copy.deepcopy(base_cred)
        revoked_cred["status"] = "REVOKED"
        revoked_digest = hashlib.sha256(NegativeProofEngine.canonicalize(revoked_cred)).hexdigest()
        res_revoked = NegativeProofEngine.evaluate_credential_integrity(
            revoked_cred, "sig_valid_hex", revoked_digest, keypair, self.trust_registry
        )
        results.append(VerificationLabTestCase(
            test_id="TC-04",
            name="Authoritatively Revoked Credential",
            description="Credential was authentic but has been authoritatively revoked by issuer",
            expected_status="REVOKED",
            actual_result=res_revoked
        ))

        # 5. Expired Credential Test
        expired_cred = copy.deepcopy(base_cred)
        expired_cred["status"] = "EXPIRED"
        expired_digest = hashlib.sha256(NegativeProofEngine.canonicalize(expired_cred)).hexdigest()
        res_expired = NegativeProofEngine.evaluate_credential_integrity(
            expired_cred, "sig_valid_hex", expired_digest, keypair, self.trust_registry
        )
        results.append(VerificationLabTestCase(
            test_id="TC-05",
            name="Expired Credential",
            description="Credential validity period has expired",
            expected_status="EXPIRED",
            actual_result=res_expired
        ))

        return results
