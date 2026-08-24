"""Phase 10 API Router — Hackathon Showcase, Demonstration & Evaluation Endpoints.

Endpoints:
  - POST /api/v1/demo/run-scenario  -> Executes complete flagship end-to-end hackathon showcase
  - GET  /api/v1/demo/personas      -> Lists interactive demo personas (Citizen, Officer, Reviewer, Operator)
  - GET  /api/v1/demo/scorecard     -> Generates live evaluation scorecard for hackathon judges
  - POST /api/v1/demo/qr/encode     -> Encodes cryptographic proof into compact QR payload & ASCII art
  - POST /api/v1/demo/qr/decode     -> Decodes and unpacks QR payload for offline verification
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from app.core.demo.demo_engine import flagship_demo
from app.core.demo.judge_scorecard import judge_scorecard
from app.core.demo.qr_generator import qr_generator

router = APIRouter(prefix="/demo", tags=["hackathon-demo"])


@router.post("/run-scenario")
def run_hackathon_flagship_scenario() -> dict[str, Any]:
    """Executes the complete 10-step flagship hackathon demonstration scenario."""
    return flagship_demo.run_flagship_scenario()


@router.get("/personas")
def list_demo_personas() -> list[dict[str, Any]]:
    """Returns pre-configured personas for live interactive multi-role walkthroughs."""
    return flagship_demo.get_personas()


@router.get("/scorecard")
def get_judge_scorecard() -> dict[str, Any]:
    """Compiles a comprehensive system maturity, benchmark, and security scorecard for judges."""
    return judge_scorecard.compile_scorecard()


@router.post("/qr/encode")
def encode_proof_to_qr(proof: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Encodes a verifiable proof into a compact QR protocol payload and ASCII visual."""
    payload = qr_generator.encode_proof_to_qr_payload(proof)
    ascii_qr = qr_generator.generate_ascii_qr(
        proof.get("proofType", "VERIFIED PROOF"), payload
    )
    return {
        "status": "ENCODED",
        "qr_payload": payload,
        "payload_length_bytes": len(payload),
        "visual_ascii_qr": ascii_qr,
    }


@router.post("/qr/decode")
def decode_qr_payload(data: dict[str, str] = Body(...)) -> dict[str, Any]:
    """Decodes a compact QR payload back into the full cryptographic proof dictionary."""
    qr_payload = data.get("qr_payload", "")
    proof = qr_generator.decode_qr_payload_to_proof(qr_payload)
    return {
        "status": "DECODED",
        "proof": proof,
    }
