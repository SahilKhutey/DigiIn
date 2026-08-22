#!/usr/bin/env python3
"""Multi-Persona Database Seeder for DigiLocker X (DigiIn).

Populates realistic digital public infrastructure (DPI) fixtures across:
1. Rahul Sharma (Student applying for JEE/NEET College Admission)
2. Sunita Verma (Farmer/Citizen applying for Land Subsidy)
3. Amit Patel (Commercial Transport Driver applying for RTO Renewal)
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Add services/api to sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "services" / "api"))
sys.path.insert(0, str(root_dir))

from app.db import repository as repo
from app.db.session import init_db
from app.domain.models import (
    DomainEvent,
    UploadedDocument,
    VerificationCase,
    VerificationRequestRecord,
    VerificationRequirement,
    VerifierQueueId,
)
from app.services.verification import REQUESTS


def seed_multi_persona_data() -> None:
    init_db()
    now = datetime.now(UTC)

    print(">>> Seeding DigiLocker X Multi-Persona Fixtures...")

    # Persona 1: Rahul Sharma (Student)
    doc_rahul = UploadedDocument(
        documentId="doc_rahul_cbse_2026",
        ownerSubjectId="subj_rahul_sharma_99",
        documentType="CLASS_XII",
        source="GOVERNMENT_ISSUED",
        filename="cbse_class_xii_marksheet.pdf",
        status="VERIFIED",
        authenticity="VERIFIED",
        verificationLevel=4,
        currentVersion=1,
        extractedMetadata={"rollNumber": "CBSE-2026-99214", "studentName": "RAHUL SHARMA", "percentage": 94.2, "board": "CBSE"},
        createdAt=now - timedelta(days=30),
    )
    repo.save_document(doc_rahul)

    # Persona 2: Sunita Verma (Land & Revenue)
    doc_sunita = UploadedDocument(
        documentId="doc_sunita_land_1998",
        ownerSubjectId="subj_sunita_verma_44",
        documentType="LAND_RECORD",
        source="CITIZEN_UPLOAD",
        filename="khasra_b1_title_deed.pdf",
        status="PENDING_VERIFICATION",
        authenticity="UNKNOWN",
        verificationLevel=2,
        currentVersion=1,
        extractedMetadata={"surveyNumber": "SUR-98/104", "recordedOwner": "SUNITA VERMA", "areaHectares": "2.40", "district": "Raipur"},
        createdAt=now - timedelta(days=2),
    )
    repo.save_document(doc_sunita)

    # Persona 3: Amit Patel (Transport Driver)
    doc_amit = UploadedDocument(
        documentId="doc_amit_dl_2024",
        ownerSubjectId="subj_amit_patel_12",
        documentType="DRIVING_LICENCE",
        source="GOVERNMENT_ISSUED",
        filename="commercial_driving_licence.pdf",
        status="VERIFIED",
        authenticity="VERIFIED",
        verificationLevel=4,
        currentVersion=1,
        extractedMetadata={"licenceNumber": "DL-1420210019283", "holderName": "AMIT PATEL", "validTill": "2028-12-31"},
        createdAt=now - timedelta(days=60),
    )
    repo.save_document(doc_amit)

    # Verification Case for Sunita Verma (Revenue Queue)
    case_sunita = VerificationCase(
        caseId="case_revenue_sunita_001",
        documentId="doc_sunita_land_1998",
        claimedIssuer="Revenue & Land Records Department, Chhattisgarh",
        status="UNDER_REVIEW",
        automatedMatchScore=88,
        recommendedAction="Requires officer inspection for khasra survey number verification.",
        verifierQueue=VerifierQueueId.QUEUE_REVENUE,
        createdAt=now - timedelta(days=2),
    )
    repo.save_verification_case(case_sunita)

    # Inbound Verification Request from NTA for Rahul Sharma
    req_nta = VerificationRequestRecord(
        requestId="vr_nta_jee_2026",
        clientId="client_nta_admission_portal",
        requesterName="National Testing Agency (NTA)",
        purpose="JEE Advanced / NEET Eligibility & Cutoff Verification",
        audience="NTA_ADMISSION_PORTAL",
        requirements=[
            VerificationRequirement(
                credential="CLASS_XII",
                description="Minimum aggregate score >= 75.0% in Senior Secondary Examination",
            )
        ],
        createdAt=now - timedelta(hours=1),
        expiresAt=now + timedelta(days=7),
        status="PENDING_CONSENT",
        consentText="I authorize National Testing Agency to verify my Class XII passing status without transferring raw certificate files.",
    )
    REQUESTS[req_nta.requestId] = req_nta

    # Domain Events
    repo.save_domain_event(
        DomainEvent(
            eventId="evt_seed_001",
            type="PERSONA_PROVISIONED",
            aggregateId="doc_rahul_cbse_2026",
            actor="SYSTEM_SEEDER",
            message="Seeded authoritative Class XII verified credential for Rahul Sharma.",
            createdAt=now - timedelta(days=30),
        )
    )
    repo.save_domain_event(
        DomainEvent(
            eventId="evt_seed_002",
            type="DISCREPANCY_CASE_ENQUEUED",
            aggregateId="doc_sunita_land_1998",
            actor="SYSTEM_SEEDER",
            message="Enqueued Khasra Title Deed discrepancy case into Revenue departmental queue.",
            createdAt=now - timedelta(days=2),
        )
    )

    print("[OK] Seeded 3 Personas (Student, Landowner, Commercial Driver)")
    print("[OK] Seeded Discrepancy Review Case in Revenue Department Queue")
    print("[OK] Seeded Inbound Verification Request from National Testing Agency")
    print("[OK] Seeded Sovereign Audit Trail Events")


if __name__ == "__main__":
    seed_multi_persona_data()
    print("SUCCESS: MULTI-PERSONA DEMO FIXTURES SEEDED SUCCESSFULLY!")
