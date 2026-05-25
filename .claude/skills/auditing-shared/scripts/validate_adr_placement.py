#!/usr/bin/env python3
"""validate_adr_placement.py — Canonical helper for ADR placement validation per ADR-0036.

Walks a scan_path (default: cwd), finds every ADR-*.md file via rglob, and
verifies each is located at the canonical adrs/ directory (or the structural
exception adrs/superseded/). Files anywhere else trigger BLOCK findings.

Used at three surfaces per ADR-0054:
  (a) Orchestrator stage gate (recipe-feature-pipeline Step 8)
  (b) Phase-quality dispatch (run_phase_checks.py)
  (c) Deliverable packager (finalize-deliverable-packager)

Exit codes per ADR-0035:
  0 = PASS (zero findings)
  2 = BLOCK (one or more findings)
  1 = unexpected error (catch-all)

NFR-2: elapsed_ms < 5000 for full-repo scan.
NFR-8: Python 3 stdlib only.
"""

import argparse
import json
import sys
import time
from pathlib import Path


def main() -> int:
    start = time.monotonic()
    parser = argparse.ArgumentParser(description="Validate ADR placement per ADR-0036.")
    parser.add_argument("scan_path", nargs="?", default=".", help="Path to scan (default: cwd)")
    parser.add_argument(
        "--allowlist",
        action="append",
        default=[],
        help="Additional allowed parent-directory glob(s). May be repeated. "
             "E.g., '--allowlist output/synthesis-*/adrs/'. ADR-0054 commitment 2.",
    )
    args = parser.parse_args()

    scan_root = Path(args.scan_path).resolve()
    if not scan_root.exists():
        result = {
            "validator": "validate_adr_placement",
            "verdict": "BLOCK",
            "findings": [{"severity": "BLOCKER", "message": f"scan_path does not exist: {scan_root}"}],
            "scan_path": str(scan_root),
            "elapsed_ms": int((time.monotonic() - start) * 1000),
        }
        print(json.dumps(result, indent=2))
        return 2

    # Find every ADR-*.md file.
    findings = []
    canonical_dir = (scan_root / "adrs").resolve()
    canonical_superseded_dir = (scan_root / "adrs" / "superseded").resolve()

    # Compile allowlist into resolved directory roots
    allowed_dirs = [canonical_dir, canonical_superseded_dir]
    for pattern in args.allowlist:
        for matched in scan_root.glob(pattern):
            if matched.is_dir():
                allowed_dirs.append(matched.resolve())

    for adr_path in scan_root.rglob("ADR-*.md"):
        # Skip .git/ paths
        if ".git" in adr_path.parts:
            continue
        parent = adr_path.parent.resolve()
        if parent in allowed_dirs:
            continue  # canonical or allowlisted location
        findings.append({
            "severity": "BLOCKER",
            "adr_file": str(adr_path.relative_to(scan_root)),
            "found_in": str(parent.relative_to(scan_root)),
            "expected_in": "adrs/ (or adrs/superseded/ for archived bodies; or an --allowlist'd location)",
            "message": f"ADR file at non-canonical location: {adr_path.relative_to(scan_root)}",
        })

    elapsed_ms = int((time.monotonic() - start) * 1000)
    verdict = "PASS" if not findings else "BLOCK"
    result = {
        "validator": "validate_adr_placement",
        "verdict": verdict,
        "findings": findings,
        "scan_path": str(scan_root),
        "elapsed_ms": elapsed_ms,
    }
    print(json.dumps(result, indent=2))
    return 0 if verdict == "PASS" else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 — top-level catch-all per ADR-0035
        err = {
            "validator": "validate_adr_placement",
            "verdict": "ERROR",
            "findings": [{"severity": "BLOCKER", "message": f"unexpected error: {type(exc).__name__}: {exc}"}],
        }
        print(json.dumps(err, indent=2), file=sys.stderr)
        sys.exit(1)
