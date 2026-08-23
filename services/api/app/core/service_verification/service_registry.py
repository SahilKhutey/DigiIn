"""
DigiIn Service Verification — Service Registry & Identity Layer
Registers external verifying institutions, manages verification scopes, and generates ServiceContext.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field


class ServiceStatus:
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"

@dataclass
class DigiInService:
    id: str
    organization_id: str
    name: str
    description: str
    client_id: str
    client_secret_hash: str
    allowed_purposes: list[str]
    verification_methods: list[str]  # ["API", "QR", "DIGIIN_ID"]
    status: str = ServiceStatus.ACTIVE
    created_at: float = field(default_factory=time.time)

@dataclass
class ServiceContext:
    service_id: str
    organization_id: str
    service_name: str
    scopes: list[str]
    allowed_purposes: list[str]

class ServiceRegistry:
    def __init__(self):
        self._services: dict[str, DigiInService] = {}
        self._seed_default_services()

    def _seed_default_services(self):
        s1 = DigiInService(
            id="srv_scholarship_portal",
            organization_id="org_ministry_edu",
            name="National Scholarship Portal",
            description="Government scholarship portal for student eligibility verification",
            client_id="dgi_svc_scholarship_01",
            client_secret_hash="hash_sec_scholarship_01",
            allowed_purposes=["SCHOLARSHIP_ELIGIBILITY", "ADMISSION_VERIFICATION"],
            verification_methods=["API", "QR", "DIGIIN_ID"],
            status=ServiceStatus.ACTIVE
        )
        s2 = DigiInService(
            id="srv_sarathi_transport",
            organization_id="org_delhi_transport",
            name="Sarathi Transport Service",
            description="Vehicle registration and driving licence verification",
            client_id="dgi_svc_transport_01",
            client_secret_hash="hash_sec_transport_01",
            allowed_purposes=["LICENCE_VERIFICATION", "IDENTITY_VERIFICATION"],
            verification_methods=["API", "QR"],
            status=ServiceStatus.ACTIVE
        )
        self._services[s1.id] = s1
        self._services[s2.id] = s2

    def register_service(
        self,
        organization_id: str,
        name: str,
        description: str,
        allowed_purposes: list[str],
        verification_methods: list[str] | None = None
    ) -> tuple[DigiInService, str]:
        sid = f"srv_{secrets.token_hex(8)}"
        client_id = f"dgi_svc_{secrets.token_hex(8)}"
        plain_secret = f"dgi_sec_{secrets.token_hex(20)}"
        secret_hash = secrets.token_hex(32)

        service = DigiInService(
            id=sid,
            organization_id=organization_id,
            name=name,
            description=description,
            client_id=client_id,
            client_secret_hash=secret_hash,
            allowed_purposes=allowed_purposes,
            verification_methods=verification_methods or ["API", "QR", "DIGIIN_ID"]
        )
        self._services[sid] = service
        return service, plain_secret

    def authenticate_service(self, service_id: str) -> ServiceContext | None:
        s = self._services.get(service_id)
        if not s or s.status != ServiceStatus.ACTIVE:
            return None
        return ServiceContext(
            service_id=s.id,
            organization_id=s.organization_id,
            service_name=s.name,
            scopes=["verification:request", "verification:read"],
            allowed_purposes=s.allowed_purposes
        )

    def get_service(self, service_id: str) -> DigiInService | None:
        return self._services.get(service_id)
