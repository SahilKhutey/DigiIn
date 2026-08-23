"""
DigiIn Institutional Review — Request Templates & Service Configuration
Manages reusable request templates with pre-configured purposes, required claims, assurance levels, and disclosure modes.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field


@dataclass
class RequestTemplate:
    id: str
    organization_id: str
    department_id: str
    name: str
    purpose: str
    required_claims: list[str]
    minimum_assurance: str  # "A1_BASIC", "A2_STATUTORY", "A3_HIGH_ASSURANCE"
    disclosure_mode: str  # "MINIMAL", "SELECTIVE", "FULL"
    request_expiry_days: int = 7
    created_at: float = field(default_factory=time.time)

class RequestTemplateManager:
    def __init__(self):
        self._templates: dict[str, RequestTemplate] = {}
        self._seed_default_templates()

    def _seed_default_templates(self):
        t1 = RequestTemplate(
            id="tmpl_scholarship_eligibility",
            organization_id="org_delhi_university",
            department_id="dept_scholarships",
            name="Merit Scholarship Eligibility",
            purpose="SCHOLARSHIP_ELIGIBILITY",
            required_claims=["education.degree", "education.graduationYear", "education.grade"],
            minimum_assurance="A3_HIGH_ASSURANCE",
            disclosure_mode="MINIMAL",
            request_expiry_days=7
        )
        t2 = RequestTemplate(
            id="tmpl_ug_admission_verification",
            organization_id="org_delhi_university",
            department_id="dept_admissions",
            name="Undergraduate Admission Class XII Verification",
            purpose="ADMISSION_VERIFICATION",
            required_claims=["education.class_xii_marksheet", "identity.name", "identity.dob"],
            minimum_assurance="A3_HIGH_ASSURANCE",
            disclosure_mode="SELECTIVE",
            request_expiry_days=5
        )
        self._templates[t1.id] = t1
        self._templates[t2.id] = t2

    def create_template(
        self,
        organization_id: str,
        department_id: str,
        name: str,
        purpose: str,
        required_claims: list[str],
        minimum_assurance: str = "A3_HIGH_ASSURANCE",
        disclosure_mode: str = "MINIMAL",
        request_expiry_days: int = 7
    ) -> RequestTemplate:
        tid = f"tmpl_{secrets.token_hex(8)}"
        tmpl = RequestTemplate(
            id=tid,
            organization_id=organization_id,
            department_id=department_id,
            name=name,
            purpose=purpose,
            required_claims=required_claims,
            minimum_assurance=minimum_assurance,
            disclosure_mode=disclosure_mode,
            request_expiry_days=request_expiry_days
        )
        self._templates[tid] = tmpl
        return tmpl

    def get_template(self, template_id: str) -> RequestTemplate | None:
        return self._templates.get(template_id)

    def list_templates_for_department(self, department_id: str) -> list[RequestTemplate]:
        return [t for t in self._templates.values() if t.department_id == department_id]
