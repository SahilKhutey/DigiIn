"""
DigiIn Ecosystem Adoption & Institutional Scale Subsystem (Phase 28)
Provides institutional RBAC, onboarding state machines, automated accreditation checks, service directory, integration marketplace, credential lifecycles, SLA management, migration frameworks, and integration certification.
"""

from .accreditation_automation import (
    MANDATORY_ACCREDITATION_CRITERIA,
    AccreditationEvaluation,
    AutomatedAccreditationChecker,
)
from .certification_engine import (
    CERTIFICATION_SUITE,
    IntegrationCertificationEngine,
    IntegrationCertificationResult,
)
from .credential_lifecycle import (
    AppCredential,
    AppEnvironment,
    CredentialLifecycleManager,
    DeveloperApplication,
)
from .institutional_analytics import InstitutionalAnalytics
from .institutional_rbac import ROLE_PERMISSIONS, InstitutionalRBACGuard, OrganizationRole
from .migration_framework import (
    MigrationBatch,
    MigrationBatchStatus,
    MigrationFramework,
)
from .onboarding_workflow import OnboardingCase, OnboardingState, OnboardingWorkflowEngine
from .service_directory_and_marketplace import (
    IntegrationMarketplace,
    IntegrationPackage,
    ServiceDirectory,
    ServiceEntry,
)
from .sla_and_operations import (
    IncidentSeverity,
    InstitutionalSLAManager,
    NetworkIncident,
)

__all__ = [
    "OrganizationRole",
    "ROLE_PERMISSIONS",
    "InstitutionalRBACGuard",
    "OnboardingState",
    "OnboardingCase",
    "OnboardingWorkflowEngine",
    "MANDATORY_ACCREDITATION_CRITERIA",
    "AccreditationEvaluation",
    "AutomatedAccreditationChecker",
    "ServiceEntry",
    "IntegrationPackage",
    "ServiceDirectory",
    "IntegrationMarketplace",
    "AppEnvironment",
    "AppCredential",
    "DeveloperApplication",
    "CredentialLifecycleManager",
    "IncidentSeverity",
    "NetworkIncident",
    "InstitutionalSLAManager",
    "MigrationBatchStatus",
    "MigrationBatch",
    "MigrationFramework",
    "CERTIFICATION_SUITE",
    "IntegrationCertificationResult",
    "IntegrationCertificationEngine",
    "InstitutionalAnalytics",
]
