"""Phase 10 — Public Release / Hackathon Demonstration Layer Package."""

from app.core.demo.demo_engine import (
    DEMO_PERSONAS,
    DemoPersona,
    FlagshipDemoEngine,
    flagship_demo,
)
from app.core.demo.judge_scorecard import (
    JudgeScorecardCompiler,
    judge_scorecard,
)
from app.core.demo.qr_generator import (
    QRProofGenerator,
    qr_generator,
)

__all__ = [
    "QRProofGenerator",
    "qr_generator",
    "JudgeScorecardCompiler",
    "judge_scorecard",
    "FlagshipDemoEngine",
    "DemoPersona",
    "DEMO_PERSONAS",
    "flagship_demo",
]
