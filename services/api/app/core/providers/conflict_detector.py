"""
DigiIn Provider Integration Subsystem — Multi-Source Conflict Detector
Detects factual discrepancies across multiple authoritative providers and routes them to manual review.
"""

from __future__ import annotations

from .evidence_normalizer import ProviderEvidence


class ConflictDetectionResult:
    def __init__(
        self,
        has_conflict: bool,
        conflict_type: str | None = None,
        conflicting_evidence: list[ProviderEvidence] | None = None,
        reason: str | None = None
    ):
        self.has_conflict = has_conflict
        self.conflict_type = conflict_type
        self.conflicting_evidence = conflicting_evidence or []
        self.reason = reason

class MultiSourceConflictDetector:
    @staticmethod
    def evaluate_evidence_consistency(evidence_list: list[ProviderEvidence]) -> ConflictDetectionResult:
        """
        Cross-correlate multiple pieces of evidence for the same claim type.
        Returns a ConflictDetectionResult flagging whether data conflicts exist.
        """
        if len(evidence_list) <= 1:
            return ConflictDetectionResult(has_conflict=False)

        # Group by claim type
        by_claim: dict[str, list[ProviderEvidence]] = {}
        for ev in evidence_list:
            by_claim.setdefault(ev.claim_type, []).append(ev)

        for claim_type, items in by_claim.items():
            if len(items) > 1:
                # Check for status divergence (e.g. one provider says VERIFIED, another says NOT_FOUND/INVALID)
                statuses = {ev.status for ev in items}
                if len(statuses) > 1 and "NOT_FOUND" in statuses and "VERIFIED" in statuses:
                    return ConflictDetectionResult(
                        has_conflict=True,
                        conflict_type="STATUS_DIVERGENCE",
                        conflicting_evidence=items,
                        reason=f"Conflicting verification statuses for claim '{claim_type}' across providers."
                    )

                # Check for value conflict in Education degrees / percentages
                if claim_type == "EDUCATION":
                    degrees = []
                    for ev in items:
                        if isinstance(ev.value, dict):
                            deg = ev.value.get("degree") or ev.value.get("qualification")
                            if deg:
                                degrees.append(deg)
                    if len(set(degrees)) > 1:
                        return ConflictDetectionResult(
                            has_conflict=True,
                            conflict_type="FACTUAL_DISCREPANCY",
                            conflicting_evidence=items,
                            reason=f"Conflicting degree qualifications reported: {degrees}"
                        )

        return ConflictDetectionResult(has_conflict=False)
