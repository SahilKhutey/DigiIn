from dataclasses import dataclass
from typing import Protocol
from app.models.entities import Credential

@dataclass
class IssuerResult:
    verified: bool
    level: int
    reason: str | None = None

class IssuerAdapter(Protocol):
    issuer_id: str
    async def verify(self, credential: Credential) -> IssuerResult: ...

class MockCBSEIssuer:
    issuer_id = "MOCK_CBSE"

    async def verify(self, credential):
        if credential.issuer_id != self.issuer_id:
            return IssuerResult(False, 0, "Issuer mismatch")
        if credential.status != "VERIFIED":
            return IssuerResult(False, 0, "Credential inactive")
        return IssuerResult(True, credential.verification_level)

class IssuerRegistry:
    def __init__(self):
        self._adapters = {"MOCK_CBSE": MockCBSEIssuer()}

    def get(self, issuer_id):
        return self._adapters.get(issuer_id)
