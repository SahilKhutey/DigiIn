"""
DigiIn Verification Hardening — Hackathon Demo Environment Fixture
Pre-seeds realistic demonstration states for 2-browser live jury walkthroughs.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DemoEnvironmentState:
    citizen_account_id: str
    citizen_name: str
    university_org_id: str
    university_name: str
    service_id: str
    service_name: str
    credential_id: str
    credential_title: str

class HackathonDemoEnvironment:
    @staticmethod
    def get_preseeded_demo_state() -> DemoEnvironmentState:
        return DemoEnvironmentState(
            citizen_account_id="DGI-7K4M-X9P2-2026",
            citizen_name="Rahul Sharma",
            university_org_id="org_delhi_university",
            university_name="University of Delhi",
            service_id="srv_scholarship_portal",
            service_name="National Scholarship Portal",
            credential_id="DGP-7K4M-92PX-2026",
            credential_title="Bachelor of Technology in Computer Science"
        )
