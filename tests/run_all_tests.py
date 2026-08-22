#!/usr/bin/env python3
"""Unified Monorepo Test Orchestrator for DigiLocker X (DigiIn).

Runs all linting, unit, integration, worker, and cryptographic proof verification test suites:
1. Ruff Code Style & Linter Check
2. Backend Pytest Matrix (22 tests)
3. Consoles & ZK Rules Integration Test Suite
4. Background Worker & Mobile Integration Test Suite
5. Document Pipeline & Officer Review E2E Test Suite
6. Core Verification Flow E2E Test Suite
7. Offline Cryptographic CLI Proof Verifier Demo
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

root_dir = Path(__file__).parent.parent


def run_command(name: str, cmd: list[str], cwd: Path) -> bool:
    print(f"\n================================================================================")
    print(f">> RUNNING: {name}")
    print(f"   Command: {' '.join(cmd)}")
    print(f"   Directory: {cwd}")
    print(f"================================================================================")
    start = time.time()
    res = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    duration = time.time() - start

    if res.stdout:
        print(res.stdout.strip())
    if res.stderr and res.returncode != 0:
        print(f"[STDERR]\n{res.stderr.strip()}")

    if res.returncode == 0:
        print(f"\n[PASS] {name} passed in {duration:.2f}s")
        return True
    else:
        print(f"\n[FAIL] {name} failed with exit code {res.returncode}")
        return False


def main():
    test_suites = [
        ("Ruff Linter Check", ["python", "-m", "ruff", "check", "app/", "tests/"], root_dir / "services" / "api"),
        ("Backend Pytest Matrix", ["python", "-m", "pytest", "-v", "--tb=short"], root_dir / "services" / "api"),
        ("Consoles & ZK Rules Test", ["python", "tests/test_consoles_and_verification_rules.py"], root_dir),
        ("Standalone Core Services (Audit & Catalogue)", ["python", "tests/test_standalone_services.py"], root_dir),
        ("Core Foundation & Security Hardening", ["python", "tests/test_foundation_hardening.py"], root_dir),
        ("API Performance & Latency SLAs", ["python", "tests/test_performance_and_latency.py"], root_dir),
        ("Security & Anti-Piracy Safeguards", ["python", "tests/test_security_and_anti_piracy.py"], root_dir),
        ("Background Worker & Mobile Integration", ["python", "tests/test_mobile_and_worker_integration.py"], root_dir),
        ("Document Pipeline 9-Step E2E", ["python", "tests/test_document_pipeline_e2e.py"], root_dir),
        ("Core Verification Flow E2E", ["python", "tests/e2e_verification_flow.py"], root_dir),
        ("Offline CLI Proof Verifier Demo", ["python", "tests/cli_proof_verifier.py", "--demo"], root_dir),
    ]

    results = []
    overall_start = time.time()

    for name, cmd, cwd in test_suites:
        passed = run_command(name, cmd, cwd)
        results.append((name, passed))

    overall_duration = time.time() - overall_start

    print("\n" + "=" * 80)
    print("DIGILOCKER X (DIGIIN) MONOREPO TEST SUMMARY REPORT")
    print("=" * 80)

    all_passed = True
    for name, passed in results:
        status_str = "[PASS]" if passed else "[FAIL]"
        if not passed:
            all_passed = False
        print(f"  {status_str:7} {name}")

    print("-" * 80)
    print(f"Total Test Time: {overall_duration:.2f}s")

    if all_passed:
        print("\n>>> ALL TEST SUITES PASSED (100% SUCCESS RATE) <<<")
        sys.exit(0)
    else:
        print("\n>>> ONE OR MORE TEST SUITES FAILED <<<")
        sys.exit(1)


if __name__ == "__main__":
    main()
