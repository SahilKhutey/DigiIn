"""Issuer adapter boundary and concrete mock government adapters."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

from app.domain.models import IssuerHealth


@dataclass
class IssuerVerificationResult:
    is_verified: bool
    level: int
    reason: str | None = None
    disclosed_claims: dict[str, Any] | None = None


@dataclass
class CredentialFetchRequest:
    subject_id: str
    credential_type: str
    identifier: str


class IssuerAdapter(Protocol):
    issuer_id: str
    name: str

    def health(self) -> IssuerHealth: ...
    def capabilities(self) -> set[str]: ...
    async def verify(self, credential_type: str, claims: dict[str, Any]) -> IssuerVerificationResult: ...
    async def fetch(self, request: CredentialFetchRequest) -> dict[str, Any] | None: ...
    async def revoke(self, credential_id: str) -> None: ...


class MockIssuerAdapter:
    """Safe in-memory issuer used to demonstrate normal and degraded states."""

    def __init__(self, issuer_id: str, name: str, status: str, latency_ms: int | None = None) -> None:
        self.issuer_id = issuer_id
        self.name = name
        self._status = status
        self._latency_ms = latency_ms

    def health(self) -> IssuerHealth:
        return IssuerHealth(
            issuerId=self.issuer_id,
            issuerName=self.name,
            status=self._status,  # type: ignore[arg-type]
            latencyMs=self._latency_ms,
            lastCheckedAt=datetime.now(UTC),
        )

    def capabilities(self) -> set[str]:
        return {"metadata", "fetch", "verify", "health"}

    async def verify(self, credential_type: str, claims: dict[str, Any]) -> IssuerVerificationResult:
        return IssuerVerificationResult(is_verified=True, level=4)

    async def fetch(self, request: CredentialFetchRequest) -> dict[str, Any] | None:
        return {"status": "ok"}

    async def revoke(self, credential_id: str) -> None:
        pass



class MockCBSEIssuer:
    """Mock Central Board of Secondary Education Issuer Adapter."""

    def __init__(self) -> None:
        self.issuer_id = "org_cbse_gov_in"
        self.name = "Central Board of Secondary Education"

    def health(self) -> IssuerHealth:
        return IssuerHealth(
            issuerId=self.issuer_id,
            issuerName=self.name,
            status="healthy",
            latencyMs=12,
            lastCheckedAt=datetime.now(UTC),
        )

    def capabilities(self) -> set[str]:
        return {"CLASS_X_CERTIFICATE", "CLASS_XII_CERTIFICATE", "CLASS_XII_MIGRATION", "verify", "fetch", "health"}

    async def verify(self, credential_type: str, claims: dict[str, Any]) -> IssuerVerificationResult:
        if credential_type in {"CLASS_XII", "CLASS_XII_CERTIFICATE", "CLASS_XII_QUALIFICATION"}:
            return IssuerVerificationResult(
                is_verified=True,
                level=4,
                reason=None,
                disclosed_claims={
                    "qualification": "Senior School Certificate Examination (Class XII)",
                    "board": "Central Board of Secondary Education",
                    "passing_year": 2026,
                    "result": "PASS",
                    "stream": "Science",
                },
            )
        return IssuerVerificationResult(
            is_verified=False,
            level=0,
            reason=f"Unsupported credential type: {credential_type}",
        )

    async def fetch(self, request: CredentialFetchRequest) -> dict[str, Any] | None:
        return {
            "qualification": "Senior School Certificate Examination (Class XII)",
            "roll_number": request.identifier,
            "passing_year": 2026,
            "result": "PASS",
        }

    async def revoke(self, credential_id: str) -> None:
        pass


class MockStateBoardIssuer:
    """Mock State Board of Secondary & Higher Secondary Education."""

    def __init__(self) -> None:
        self.issuer_id = "org_state_board_in"
        self.name = "State Board of Secondary Education"

    def health(self) -> IssuerHealth:
        return IssuerHealth(
            issuerId=self.issuer_id,
            issuerName=self.name,
            status="healthy",
            latencyMs=28,
            lastCheckedAt=datetime.now(UTC),
        )

    def capabilities(self) -> set[str]:
        return {"STATE_CLASS_XII", "DOMICILE_CERTIFICATE", "verify", "fetch", "health"}

    async def verify(self, credential_type: str, claims: dict[str, Any]) -> IssuerVerificationResult:
        return IssuerVerificationResult(
            is_verified=True,
            level=4,
            disclosed_claims={
                "qualification": "Higher Secondary Certificate",
                "passing_year": 2025,
                "result": "DISTINCTION",
            },
        )

    async def fetch(self, request: CredentialFetchRequest) -> dict[str, Any] | None:
        return {"qualification": "HSC", "passing_year": 2025}

    async def revoke(self, credential_id: str) -> None:
        pass


class MockUniversityIssuer:
    """Mock University Issuer Adapter."""

    def __init__(self) -> None:
        self.issuer_id = "org_university_in"
        self.name = "State Technical University"

    def health(self) -> IssuerHealth:
        return IssuerHealth(
            issuerId=self.issuer_id,
            issuerName=self.name,
            status="healthy",
            latencyMs=45,
            lastCheckedAt=datetime.now(UTC),
        )

    def capabilities(self) -> set[str]:
        return {"BTECH_DEGREE", "TRANSCRIPT", "verify", "fetch", "health"}

    async def verify(self, credential_type: str, claims: dict[str, Any]) -> IssuerVerificationResult:
        return IssuerVerificationResult(
            is_verified=True,
            level=4,
            disclosed_claims={
                "degree": "Bachelor of Technology",
                "branch": "Computer Science & Engineering",
                "cgpa": 8.85,
                "graduation_year": 2026,
            },
        )

    async def fetch(self, request: CredentialFetchRequest) -> dict[str, Any] | None:
        return {"degree": "B.Tech", "graduation_year": 2026}

    async def revoke(self, credential_id: str) -> None:
        pass


class IssuerRegistry:
    """Registry maintaining active issuer adapters."""

    def __init__(self) -> None:
        self._adapters: dict[str, IssuerAdapter] = {}
        # Register default mock adapters
        self.register(MockCBSEIssuer())
        self.register(MockStateBoardIssuer())
        self.register(MockUniversityIssuer())

    def register(self, adapter: IssuerAdapter) -> None:
        self._adapters[adapter.issuer_id] = adapter

    def get(self, issuer_id: str) -> IssuerAdapter | None:
        return self._adapters.get(issuer_id) or self._adapters.get("org_cbse_gov_in")

    def list_all(self) -> list[IssuerAdapter]:
        return list(self._adapters.values())


issuer_registry = IssuerRegistry()
