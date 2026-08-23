"""
DigiIn Long-Term Infrastructure — Versioned Platform Contracts
Manages permanent API, Event, and Schema lifecycles (ACTIVE, DEPRECATED, SUNSET) with ecosystem compatibility guarantees.
"""

from __future__ import annotations

from dataclasses import dataclass


class ContractState:
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    SUNSET = "SUNSET"

@dataclass
class PlatformContract:
    contract_id: str
    contract_type: str  # "API" | "EVENT" | "SCHEMA"
    version: str
    state: str = ContractState.ACTIVE
    supported_until: float | None = None

class VersionedContractManager:
    def __init__(self):
        self._contracts: dict[str, PlatformContract] = {}
        self._seed_default_contracts()

    def _seed_default_contracts(self):
        self._contracts["API:v1"] = PlatformContract("API:v1", "API", "v1", ContractState.ACTIVE)
        self._contracts["API:v2"] = PlatformContract("API:v2", "API", "v2", ContractState.ACTIVE)
        self._contracts["EVENT:v1"] = PlatformContract("EVENT:v1", "EVENT", "1.0", ContractState.ACTIVE)

    def is_contract_supported(self, contract_type: str, version: str) -> bool:
        key = f"{contract_type}:{version}"
        c = self._contracts.get(key)
        return c is not None and c.state in (ContractState.ACTIVE, ContractState.DEPRECATED)
