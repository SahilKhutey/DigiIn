"""
DigiIn Provider Integration Subsystem (Phase 19)
Provides provider registry, adapter framework, gateway orchestrator, normalized evidence, conflict detection, and webhook receivers.
"""

from .conflict_detector import ConflictDetectionResult, MultiSourceConflictDetector
from .evidence_normalizer import EvidenceNormalizer, ProviderEvidence
from .provider_adapter import (
    BoardAdapter,
    GovernmentAdapter,
    ProviderAdapter,
    ProviderVerificationRequest,
    RawProviderResponse,
    SandboxSimulatorAdapter,
    UniversityAdapter,
)
from .provider_gateway import CircuitBreakerState, ProviderCircuitBreaker, ProviderGateway
from .provider_registry import (
    CoreProviderRegistry,
    ProviderManifest,
    ProviderStatus,
    ProviderTrustLevel,
    ProviderType,
)
from .webhook_receiver import WebhookReceiverService

__all__ = [
    "CoreProviderRegistry",
    "ProviderManifest",
    "ProviderStatus",
    "ProviderType",
    "ProviderTrustLevel",
    "ProviderAdapter",
    "ProviderVerificationRequest",
    "RawProviderResponse",
    "BoardAdapter",
    "UniversityAdapter",
    "GovernmentAdapter",
    "SandboxSimulatorAdapter",
    "ProviderEvidence",
    "EvidenceNormalizer",
    "MultiSourceConflictDetector",
    "ConflictDetectionResult",
    "WebhookReceiverService",
    "ProviderGateway",
    "ProviderCircuitBreaker",
    "CircuitBreakerState",
]
