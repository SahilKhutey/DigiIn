"""Issuer adapter boundary. Real adapters require formal authorisation."""

from typing import Protocol

from app.domain.models import IssuerHealth


class IssuerAdapter(Protocol):
    issuer_id: str

    def health(self) -> IssuerHealth: ...

    def capabilities(self) -> set[str]: ...


class MockIssuerAdapter:
    """Safe in-memory issuer used to demonstrate normal and degraded states."""

    def __init__(self, issuer_id: str, name: str, status: str, latency_ms: int | None) -> None:
        self.issuer_id = issuer_id
        self._name = name
        self._status = status
        self._latency_ms = latency_ms

    def health(self) -> IssuerHealth:
        from datetime import UTC, datetime

        return IssuerHealth(
            issuerId=self.issuer_id,
            issuerName=self._name,
            status=self._status,  # type: ignore[arg-type]
            latencyMs=self._latency_ms,
            lastCheckedAt=datetime.now(UTC),
        )

    def capabilities(self) -> set[str]:
        return {"metadata", "fetch", "verify", "health"}
