"""
DigiIn Provider Integration Subsystem — Provider Registry & Lifecycle
Manages registered authoritative evidence providers, capabilities, trust levels, and lifecycle states.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any


class ProviderStatus(StrEnum):
    REGISTERED = "REGISTERED"
    CONFIGURED = "CONFIGURED"
    TESTING = "TESTING"
    VERIFIED = "VERIFIED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DISABLED = "DISABLED"
    REVOKED = "REVOKED"

class ProviderType(StrEnum):
    GOVERNMENT = "GOVERNMENT"
    UNIVERSITY = "UNIVERSITY"
    BOARD = "BOARD"
    INSTITUTION = "INSTITUTION"
    EMPLOYER = "EMPLOYER"
    BANK = "BANK"
    SANDBOX = "SANDBOX"

class ProviderTrustLevel(StrEnum):
    SOVEREIGN = "SOVEREIGN"       # Constitutional / statutory authority
    STATUTORY = "STATUTORY"       # Legislatively created body
    ACCREDITED = "ACCREDITED"     # Officially accredited entity
    INSTITUTIONAL = "INSTITUTIONAL"

class ProviderManifest:
    def __init__(
        self,
        id: str,
        name: str,
        type: ProviderType,
        capabilities: list[str],
        trust_level: ProviderTrustLevel = ProviderTrustLevel.ACCREDITED,
        status: ProviderStatus = ProviderStatus.ACTIVE,
        environment: str = "PRODUCTION",
        jurisdiction: str = "IN",
        timeout_ms: int = 10000
    ):
        self.id = id
        self.name = name
        self.type = type
        self.capabilities = capabilities
        self.trust_level = trust_level
        self.status = status
        self.environment = environment
        self.jurisdiction = jurisdiction
        self.timeout_ms = timeout_ms

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": str(self.type),
            "capabilities": self.capabilities,
            "trust_level": str(self.trust_level),
            "status": str(self.status),
            "environment": self.environment,
            "jurisdiction": self.jurisdiction,
            "timeout_ms": self.timeout_ms,
        }

class CoreProviderRegistry:
    def __init__(self):
        self._providers: dict[str, ProviderManifest] = {}
        self._seed_default_providers()

    def _seed_default_providers(self):
        # 1. Central Board of Secondary Education (CBSE)
        self.register(
            ProviderManifest(
                id="provider_cbse_in",
                name="Central Board of Secondary Education",
                type=ProviderType.BOARD,
                capabilities=["EDUCATION", "CLASS_X", "CLASS_XII"],
                trust_level=ProviderTrustLevel.SOVEREIGN,
                status=ProviderStatus.ACTIVE,
                jurisdiction="IN"
            )
        )
        # 2. Delhi University Academic Registry
        self.register(
            ProviderManifest(
                id="provider_delhi_univ",
                name="University of Delhi",
                type=ProviderType.UNIVERSITY,
                capabilities=["EDUCATION", "DEGREE_GRADUATION", "TRANSCRIPT"],
                trust_level=ProviderTrustLevel.STATUTORY,
                status=ProviderStatus.ACTIVE,
                jurisdiction="IN-DL"
            )
        )
        # 3. Transport Department Authority (Driving Licences)
        self.register(
            ProviderManifest(
                id="provider_sarathi_parivahan",
                name="Ministry of Road Transport & Highways (Sarathi)",
                type=ProviderType.GOVERNMENT,
                capabilities=["IDENTITY", "DRIVING_LICENCE", "AGE_ELIGIBILITY"],
                trust_level=ProviderTrustLevel.SOVEREIGN,
                status=ProviderStatus.ACTIVE,
                jurisdiction="IN"
            )
        )
        # 4. Sandbox Mock Provider
        self.register(
            ProviderManifest(
                id="provider_sandbox_sim",
                name="DigiIn Universal Sandbox Simulator",
                type=ProviderType.SANDBOX,
                capabilities=["EDUCATION", "IDENTITY", "AGE_ELIGIBILITY", "ADDRESS"],
                trust_level=ProviderTrustLevel.INSTITUTIONAL,
                status=ProviderStatus.ACTIVE,
                environment="SANDBOX"
            )
        )

    def register(self, manifest: ProviderManifest) -> None:
        self._providers[manifest.id] = manifest

    def get(self, provider_id: str) -> ProviderManifest | None:
        return self._providers.get(provider_id)

    def find_providers_for_claim(self, claim_type: str, jurisdiction: str | None = None) -> list[ProviderManifest]:
        """Find active authoritative providers capable of verifying the requested claim type."""
        exact_matches = []
        national_matches = []
        for p in self._providers.values():
            if p.status == ProviderStatus.ACTIVE and claim_type in p.capabilities:
                if jurisdiction is not None and p.jurisdiction == jurisdiction:
                    exact_matches.append(p)
                elif p.jurisdiction == "IN" or jurisdiction is None:
                    national_matches.append(p)

        priority = {
            ProviderTrustLevel.SOVEREIGN: 0,
            ProviderTrustLevel.STATUTORY: 1,
            ProviderTrustLevel.ACCREDITED: 2,
            ProviderTrustLevel.INSTITUTIONAL: 3,
        }
        exact_matches.sort(key=lambda p: priority.get(p.trust_level, 99))
        national_matches.sort(key=lambda p: priority.get(p.trust_level, 99))
        return exact_matches if exact_matches else national_matches

    def update_status(self, provider_id: str, new_status: ProviderStatus) -> bool:
        provider = self._providers.get(provider_id)
        if provider:
            provider.status = new_status
            return True
        return False
