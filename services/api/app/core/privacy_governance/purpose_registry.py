"""
DigiIn Privacy & Data Governance — Purpose Registry & Limitation
Defines legitimate processing purposes and controls allowed data classifications per purpose.
"""

from __future__ import annotations

from dataclasses import dataclass

from .data_classification import DataClassification


@dataclass
class DataPurpose:
    id: str
    code: str
    description: str
    active: bool
    allowed_data_classes: list[str]

class DataPurposeRegistry:
    def __init__(self):
        self._purposes: dict[str, DataPurpose] = {}
        self._seed_default_purposes()

    def _seed_default_purposes(self):
        defaults = [
            DataPurpose(
                id="purp_identity",
                code="IDENTITY_VERIFICATION",
                description="Verifying citizen sovereign identity attributes.",
                active=True,
                allowed_data_classes=[DataClassification.PUBLIC, DataClassification.PERSONAL, DataClassification.SENSITIVE_PERSONAL]
            ),
            DataPurpose(
                id="purp_education",
                code="EDUCATION_VERIFICATION",
                description="Verifying degrees, diplomas, and marksheet credentials.",
                active=True,
                allowed_data_classes=[DataClassification.PUBLIC, DataClassification.PERSONAL]
            ),
            DataPurpose(
                id="purp_employment",
                code="EMPLOYMENT_VERIFICATION",
                description="Verifying employer records, designations, and tenures.",
                active=True,
                allowed_data_classes=[DataClassification.PUBLIC, DataClassification.PERSONAL]
            ),
            DataPurpose(
                id="purp_proof",
                code="PROOF_PRESENTATION",
                description="Presenting minimal cryptographic zero-knowledge or Ed25519 proofs.",
                active=True,
                allowed_data_classes=[DataClassification.PUBLIC, DataClassification.PERSONAL]
            ),
            DataPurpose(
                id="purp_security",
                code="ACCOUNT_SECURITY",
                description="Authentication, MFA, device binding, and fraud prevention.",
                active=True,
                allowed_data_classes=[DataClassification.INTERNAL, DataClassification.CREDENTIAL]
            ),
        ]
        for p in defaults:
            self._purposes[p.code] = p

    def get_purpose(self, code: str) -> DataPurpose | None:
        return self._purposes.get(code)

    def is_data_class_allowed_for_purpose(self, purpose_code: str, data_class: str) -> bool:
        purp = self.get_purpose(purpose_code)
        if not purp or not purp.active:
            return False
        return data_class in purp.allowed_data_classes
