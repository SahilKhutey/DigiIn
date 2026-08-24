"""Phase 8.4 — Authorization Policy Engine (ABAC).

Replaces simple role checks with Attribute-Based Access Control:

  Subject + Role + Resource + Action + Purpose + Context → Policy Decision

Built-in rules:
  Department Officer + Verification Request + READ_CLAIM + Scholarship + Citizen Consent → ALLOW
  Department Officer + Original Document + READ + No Consent                             → DENY
  Citizen + Own Credential + READ                                                        → ALLOW
  Any Actor + Credential + READ_CLAIM + Expired Consent                                 → DENY
  ADMIN + Any Resource + ANY action                                                      → ALLOW + audit_required
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class PolicyEffect(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_CONSENT = "REQUIRE_CONSENT"
    REQUIRE_MFA = "REQUIRE_MFA"


class ResourceAction(StrEnum):
    READ = "READ"
    READ_CLAIM = "READ_CLAIM"
    WRITE = "WRITE"
    DELETE = "DELETE"
    VERIFY = "VERIFY"
    ISSUE = "ISSUE"
    REVOKE = "REVOKE"
    ADMIN = "ADMIN"
    ANY = "*"


# ---------------------------------------------------------------------------
# Policy data structures
# ---------------------------------------------------------------------------


@dataclass
class AccessContext:
    """Runtime context provided alongside a policy evaluation request."""

    consent_granted: bool = False
    consent_expired: bool = False
    is_own_resource: bool = False          # Subject is accessing their own data
    mfa_verified: bool = False
    request_purpose: str = ""
    additional: dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyDecision:
    effect: PolicyEffect
    reason: str
    audit_required: bool = False
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def allowed(self) -> bool:
        return self.effect == PolicyEffect.ALLOW


@dataclass
class PolicyRule:
    """Declarative access control rule."""

    rule_id: str
    description: str
    subject_roles: list[str]               # ["OFFICER", "ADMIN"] or ["*"]
    resource_type: str                     # "document", "credential", "*"
    action: ResourceAction
    effect: PolicyEffect
    priority: int = 50                     # Lower = higher priority
    require_consent: bool = False
    require_own_resource: bool = False
    deny_if_expired_consent: bool = False
    audit_required: bool = False
    reason: str = ""


# ---------------------------------------------------------------------------
# Built-in rules
# ---------------------------------------------------------------------------

_BUILTIN_RULES: list[PolicyRule] = [
    # Admins and operators can do anything (but always audited)
    PolicyRule(
        rule_id="admin-all",
        description="Admins and operators have full access — always audited",
        subject_roles=["ADMIN", "OPERATOR"],
        resource_type="*",
        action=ResourceAction.ANY,
        effect=PolicyEffect.ALLOW,
        priority=1,
        audit_required=True,
        reason="Admin access — audited",
    ),
    # Citizens can read their own resources
    PolicyRule(
        rule_id="citizen-own-read",
        description="Citizens can read their own documents, credentials, and consents",
        subject_roles=["CITIZEN"],
        resource_type="*",
        action=ResourceAction.READ,
        effect=PolicyEffect.ALLOW,
        priority=10,
        require_own_resource=True,
        reason="Citizen accessing own data",
    ),
    # Officers can read claims WITH consent
    PolicyRule(
        rule_id="officer-claim-with-consent",
        description="Officers can read claims only with active citizen consent",
        subject_roles=["OFFICER", "VERIFIER"],
        resource_type="credential",
        action=ResourceAction.READ_CLAIM,
        effect=PolicyEffect.ALLOW,
        priority=20,
        require_consent=True,
        reason="Officer reading claim with citizen consent",
    ),
    # Block officers reading original documents without consent
    PolicyRule(
        rule_id="officer-document-no-consent-deny",
        description="Officers cannot read original documents without citizen consent",
        subject_roles=["OFFICER", "VERIFIER"],
        resource_type="document",
        action=ResourceAction.READ,
        effect=PolicyEffect.DENY,
        priority=15,
        audit_required=True,
        reason="Attempted document access without consent — DENIED",
    ),
    # Deny any access when consent has expired
    PolicyRule(
        rule_id="expired-consent-deny",
        description="Deny all claim access when consent has expired",
        subject_roles=["*"],
        resource_type="credential",
        action=ResourceAction.READ_CLAIM,
        effect=PolicyEffect.DENY,
        priority=5,
        deny_if_expired_consent=True,
        audit_required=True,
        reason="Consent has expired — access DENIED",
    ),
    # Officers can verify (not read raw documents)
    PolicyRule(
        rule_id="officer-verify",
        description="Officers can perform verification actions",
        subject_roles=["OFFICER", "VERIFIER"],
        resource_type="credential",
        action=ResourceAction.VERIFY,
        effect=PolicyEffect.ALLOW,
        priority=25,
        reason="Officer verification action",
    ),
    # Citizens can issue consent
    PolicyRule(
        rule_id="citizen-consent-issue",
        description="Citizens can grant and revoke their own consents",
        subject_roles=["CITIZEN"],
        resource_type="consent",
        action=ResourceAction.WRITE,
        effect=PolicyEffect.ALLOW,
        priority=10,
        require_own_resource=True,
        reason="Citizen managing own consent",
    ),
    # Default deny for everything not explicitly allowed
    PolicyRule(
        rule_id="default-deny",
        description="Default deny — no explicit rule matched",
        subject_roles=["*"],
        resource_type="*",
        action=ResourceAction.ANY,
        effect=PolicyEffect.DENY,
        priority=999,
        audit_required=True,
        reason="No policy rule matched — default DENY",
    ),
]


# ---------------------------------------------------------------------------
# Policy Engine
# ---------------------------------------------------------------------------


class PolicyEngine:
    """
    Evaluates access control decisions using ordered policy rules.

    Rules are evaluated in priority order (lowest number = highest priority).
    The first matching rule's effect wins.
    """

    def __init__(self, extra_rules: list[PolicyRule] | None = None) -> None:
        self._rules: list[PolicyRule] = sorted(
            _BUILTIN_RULES + (extra_rules or []), key=lambda r: r.priority
        )

    def evaluate(
        self,
        subject_role: str,
        resource_type: str,
        action: ResourceAction,
        context: AccessContext | None = None,
    ) -> PolicyDecision:
        ctx = context or AccessContext()

        for rule in self._rules:
            if not self._matches_role(rule, subject_role):
                continue
            if not self._matches_resource(rule, resource_type):
                continue
            if not self._matches_action(rule, action):
                continue

            # Check contextual conditions
            if rule.deny_if_expired_consent and not ctx.consent_expired:
                continue  # Rule only applies when consent IS expired
            if rule.require_consent and not ctx.consent_granted:
                # Consent required but not granted — return REQUIRE_CONSENT
                return PolicyDecision(
                    effect=PolicyEffect.REQUIRE_CONSENT,
                    reason="Citizen consent required for this access",
                    audit_required=True,
                )
            if rule.require_own_resource and not ctx.is_own_resource:
                continue  # Rule only applies to own resources

            return PolicyDecision(
                effect=rule.effect,
                reason=rule.reason or rule.description,
                audit_required=rule.audit_required,
            )

        # Fallback (should never reach here given default-deny rule)
        return PolicyDecision(
            effect=PolicyEffect.DENY,
            reason="No rule matched — implicit deny",
            audit_required=True,
        )

    def assert_allowed(
        self,
        subject_role: str,
        resource_type: str,
        action: ResourceAction,
        context: AccessContext | None = None,
    ) -> PolicyDecision:
        """Evaluate and raise PermissionError if not ALLOW."""
        decision = self.evaluate(subject_role, resource_type, action, context)
        if not decision.allowed:
            raise PermissionError(
                f"Access DENIED: role={subject_role} resource={resource_type} "
                f"action={action.value} — {decision.reason}"
            )
        return decision

    def _matches_role(self, rule: PolicyRule, role: str) -> bool:
        return "*" in rule.subject_roles or role.upper() in [r.upper() for r in rule.subject_roles]

    def _matches_resource(self, rule: PolicyRule, resource_type: str) -> bool:
        return rule.resource_type in ("*", resource_type.lower())

    def _matches_action(self, rule: PolicyRule, action: ResourceAction) -> bool:
        return rule.action in (ResourceAction.ANY, action)


# ---------------------------------------------------------------------------
# Module singleton
# ---------------------------------------------------------------------------

policy_engine = PolicyEngine()
