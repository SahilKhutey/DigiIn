"""
DigiIn Controlled Pilot & Production Validation — User Feedback & UX Metrics Collector
Gathers satisfaction ratings and feedback across onboarding, document upload, verification, and proof journeys.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class UserFeedback:
    id: str
    journey: str  # "ONBOARDING" | "UPLOAD" | "VERIFICATION" | "PROOF" | "ORGANIZATION"
    rating: int   # 1 to 5
    category: str
    comment: str = ""
    user_id: str | None = None
    created_at: float = field(default_factory=time.time)

class UserFeedbackCollector:
    def __init__(self):
        self._feedbacks: list[UserFeedback] = []

    def submit_feedback(
        self,
        journey: str,
        rating: int,
        category: str,
        comment: str = "",
        user_id: str | None = None
    ) -> UserFeedback:
        fid = f"fbk_{secrets.token_hex(8)}"
        fb = UserFeedback(
            id=fid,
            journey=journey,
            rating=rating,
            category=category,
            comment=comment,
            user_id=user_id
        )
        self._feedbacks.append(fb)
        return fb

    def calculate_csat_metrics(self) -> dict[str, Any]:
        if not self._feedbacks:
            return {"averageRating": 0.0, "totalResponses": 0, "satisfactionPct": "0.0%"}

        total = len(self._feedbacks)
        avg = sum(f.rating for f in self._feedbacks) / total
        satisfied = sum(1 for f in self._feedbacks if f.rating >= 4)
        pct = round((satisfied / total) * 100.0, 1)

        return {
            "averageRating": round(avg, 2),
            "totalResponses": total,
            "satisfactionPct": f"{pct}%"
        }
