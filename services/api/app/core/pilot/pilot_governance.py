"""
DigiIn Controlled Pilot & Production Validation — Pilot Program Governance
Manages the pilot program lifecycle and enforces strict pilot boundaries (allowed organizations, document types, providers, and verification scopes).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


class PilotStatus:
    PLANNED = "PLANNED"
    READY = "READY"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

@dataclass
class PilotProgram:
    id: str
    name: str
    status: str = PilotStatus.PLANNED
    participating_organizations: list[str] = field(default_factory=list)
    enabled_document_types: list[str] = field(default_factory=list)
    enabled_providers: list[str] = field(default_factory=list)
    owner_id: str = "PILOT_LEAD_01"
    start_at: float | None = None
    end_at: float | None = None

class PilotGovernanceManager:
    def __init__(self):
        self._programs: dict[str, PilotProgram] = {}
        self._seed_default_pilot()

    def _seed_default_pilot(self):
        pid = "pilot_digiin_2026_q3"
        program = PilotProgram(
            id=pid,
            name="DigiIn Sovereign Higher-Education & Statutory Pilot",
            status=PilotStatus.ACTIVE,
            participating_organizations=["org_delhi_university", "org_iit_bombay", "org_transport_dept"],
            enabled_document_types=["DEGREE_CERTIFICATE", "MARKSHEET", "DRIVING_LICENCE"],
            enabled_providers=["mock-cbse-001", "mock-transport-001", "mock-revenue-001"],
            owner_id="GOV_PILOT_ADMIN",
            start_at=time.time()
        )
        self._programs[pid] = program

    def get_program(self, program_id: str) -> PilotProgram | None:
        return self._programs.get(program_id)

    def validate_pilot_boundary(
        self,
        program_id: str,
        organization_id: str,
        document_type: str,
        provider_id: str
    ) -> tuple[bool, str | None]:
        """Enforces that only registered organizations, documents, and providers can participate in the active pilot."""
        program = self.get_program(program_id)
        if not program:
            return False, "PILOT_PROGRAM_NOT_FOUND"

        if program.status != PilotStatus.ACTIVE:
            return False, f"PILOT_NOT_ACTIVE: Current pilot status is '{program.status}'."

        if organization_id not in program.participating_organizations and "*" not in program.participating_organizations:
            return False, f"ORGANIZATION_OUTSIDE_PILOT: Organization '{organization_id}' is not enrolled in the pilot."

        if document_type not in program.enabled_document_types:
            return False, f"DOCUMENT_TYPE_OUTSIDE_PILOT: Document type '{document_type}' is not enabled in the pilot scope."

        if provider_id not in program.enabled_providers:
            return False, f"PROVIDER_OUTSIDE_PILOT: Provider '{provider_id}' is not enabled in the pilot scope."

        return True, None
