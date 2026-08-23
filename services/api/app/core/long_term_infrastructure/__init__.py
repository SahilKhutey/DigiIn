"""
DigiIn Long-Term Digital Trust Infrastructure Subsystem (Phase 30)
Provides the canonical digital trust model, stable account identifiers, portable credentials, universal claim registries, national trust registries, advanced proof engines, subject-controlled consent, platform governance, versioned contracts, platform SDK, and the 9-layer reference architecture.
"""

from .advanced_proof_engine import (
    AdvancedProofEngine,
    ProofType,
    VerifiableProof,
)
from .canonical_trust_model import (
    ACCOUNT_ID_PATTERN,
    CredentialStatus,
    DigiInAccount,
    PortableCredential,
    PortableCredentialManager,
)
from .national_trust_registry import (
    NationalTrustRegistry,
    TrustRegistryEntry,
)
from .platform_governance import (
    GovernanceCommittee,
    PlatformGovernanceEngine,
    VersionedPolicy,
)
from .platform_sdk import (
    DigiInPlatformSDK,
    PlatformErrorCode,
    SDKVerificationResponse,
)
from .reference_architecture import (
    PLATFORM_LAYERS,
    PlatformReferenceArchitecture,
)
from .subject_controlled_trust import (
    CitizenConsentGrant,
    SubjectControlledConsentManager,
)
from .universal_claim_registry import (
    UniversalClaimRegistry,
    UniversalClaimSchema,
)
from .versioned_contracts import (
    ContractState,
    PlatformContract,
    VersionedContractManager,
)

__all__ = [
    "ACCOUNT_ID_PATTERN",
    "CredentialStatus",
    "DigiInAccount",
    "PortableCredential",
    "PortableCredentialManager",
    "UniversalClaimSchema",
    "UniversalClaimRegistry",
    "TrustRegistryEntry",
    "NationalTrustRegistry",
    "ProofType",
    "VerifiableProof",
    "AdvancedProofEngine",
    "CitizenConsentGrant",
    "SubjectControlledConsentManager",
    "GovernanceCommittee",
    "VersionedPolicy",
    "PlatformGovernanceEngine",
    "ContractState",
    "PlatformContract",
    "VersionedContractManager",
    "PlatformErrorCode",
    "SDKVerificationResponse",
    "DigiInPlatformSDK",
    "PLATFORM_LAYERS",
    "PlatformReferenceArchitecture",
]
