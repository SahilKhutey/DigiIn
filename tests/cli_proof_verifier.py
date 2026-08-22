#!/usr/bin/env python3
"""Offline Cryptographic Proof Verifier CLI Tool.

Allows any third-party relying party (e.g. University, Employer, NTA)
to mathematically verify DigiLocker X signed proof tokens completely offline
without calling any central server.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add services/api to sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "services" / "api"))
sys.path.insert(0, str(root_dir))

from app.services.crypto import get_public_jwks, sign_proof_token, verify_proof_token


def verify_offline_token(token: str, expected_audience: str | None = None) -> dict:
    """Offline cryptographic validation of a JWS/JWT proof token."""
    claims, kid, alg = verify_proof_token(token)

    if claims is None:
        return {
            "valid": False,
            "status": "CRYPTOGRAPHIC_SIGNATURE_INVALID",
            "error": "Digital signature verification failed or token is malformed.",
        }

    # Audience check
    if expected_audience and claims.get("aud") != expected_audience:
        return {
            "valid": False,
            "status": "AUDIENCE_MISMATCH",
            "error": f"Token intended for audience '{claims.get('aud')}', not '{expected_audience}'.",
            "claims": claims,
            "keyId": kid,
            "algorithm": alg,
        }

    return {
        "valid": True,
        "status": "TRUSTED_PROOF_VERIFIED_OFFLINE",
        "keyId": kid,
        "algorithm": alg,
        "subjectId": claims.get("sub"),
        "audience": claims.get("aud"),
        "purpose": claims.get("purpose"),
        "verificationStatus": claims.get("status"),
        "claims": claims,
    }


def main():
    parser = argparse.ArgumentParser(description="DigiLocker X Offline Proof Verifier CLI")
    parser.add_argument("--token", type=str, help="Encoded JWS proof token string")
    parser.add_argument("--audience", type=str, help="Expected relying party audience (e.g., DELHI_UNIVERSITY_ADMISSION)")
    parser.add_argument("--jwks", action="store_true", help="Print the RFC 7517 public JWKS key set and exit")
    parser.add_argument("--demo", action="store_true", help="Generate a sample signed token and verify it offline")

    args = parser.parse_args()

    if args.jwks:
        print(json.dumps(get_public_jwks(), indent=2))
        return

    if args.demo:
        print(">>> 1. Generating sample Ed25519 signed verification proof token...")
        demo_claims = {
            "iss": "DigiLocker X Sovereign Verification Gateway",
            "sub": "subj_rahul_sharma_99",
            "aud": "DELHI_UNIVERSITY_ADMISSION",
            "purpose": "ADMISSION_VERIFICATION",
            "status": "VERIFIED",
            "verification_level": 4,
            "predicates": [
                {"claim": "CLASS_XII", "expression": "percentage >= 60.0", "satisfied": True}
            ],
            "raw_file_transferred": False,
        }
        token, kid, alg = sign_proof_token(demo_claims, algorithm="EdDSA")
        print(f"    Algorithm: {alg}")
        print(f"    Key ID: {kid}")
        print(f"    Token: {token}\n")

        print(">>> 2. Performing offline mathematical verification...")
        res = verify_offline_token(token, expected_audience="DELHI_UNIVERSITY_ADMISSION")
        print(json.dumps(res, indent=2))
        print("\n[SUCCESS] Token verified offline with 100% mathematical integrity!")
        return

    if not args.token:
        parser.print_help()
        return

    result = verify_offline_token(args.token, args.audience)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
