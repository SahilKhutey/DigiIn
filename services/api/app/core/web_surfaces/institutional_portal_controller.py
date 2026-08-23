"""
DigiIn Web Surfaces — Institutional Portal Controller
Manages 6-step verification request stepper wizard and institutional dashboard controllers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class StepperWizardState:
    step: int  # 1 to 6
    citizen_ref: str
    purpose: str
    claims: list[str]
    assurance: str
    disclosure_mode: str
    is_valid: bool

class InstitutionalPortalController:
    @staticmethod
    def validate_stepper_step(step: int, data: dict[str, Any]) -> tuple[bool, str]:
        if step == 1:  # Identify Citizen
            if not data.get("subjectReference", "").startswith("DGI-"):
                return False, "Invalid DigiIn Account ID format (Must start with DGI-)"
            return True, "STEP_1_VALID"
        elif step == 2:  # Purpose
            if not data.get("purpose"):
                return False, "Purpose must be selected"
            return True, "STEP_2_VALID"
        elif step == 3:  # Claims
            if not data.get("requestedClaims") or len(data["requestedClaims"]) == 0:
                return False, "At least one claim must be requested"
            return True, "STEP_3_VALID"
        elif step == 4:  # Policy
            if not data.get("disclosureMode"):
                return False, "Disclosure mode must be selected"
            return True, "STEP_4_VALID"
        elif step == 5:  # Review
            return True, "STEP_5_REVIEW_READY"
        elif step == 6:  # Send
            return True, "STEP_6_SEND_READY"
        return False, "UNKNOWN_STEP"
