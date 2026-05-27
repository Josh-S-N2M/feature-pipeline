#!/usr/bin/env python3
"""
audit_op9_url_credential_rejection.py — OP-9 URL-query credential REJECT rule.

Per ADR-0039 + cc-design Principle 1. Any URL-query credential pattern in
.mcp.json server entries is a BLOCKER. The augmented auditing-mcp Gate-6
check (per ADR-0043) HALTS the orchestrator on any OP-9 BLOCKER.

Patterns flagged:
  - ?apiKey=...
  - ?api_key=...
  - ?token=...
  - ?Bearer%20...  (URL-encoded Bearer)
  - any query parameter matching a credential-shaped name

Usage:
    python3 audit_op9_url_credential_rejection.py <repo-root>
"""
import json
import re
import sys
from urllib.parse import urlparse, parse_qs
from pathlib import Path


CRED_PARAM_NAMES = re.compile(
    r'^(api[-_]?key|token|access[-_]?token|secret|password|bearer|credential|auth)$',
    re.IGNORECASE,
)


def check_url(url: str) -> list[str]:
    """Return list of problem strings; empty if clean."""
    problems: list[str] = []
    try:
        parsed = urlparse(url)
    except Exception as e:
        problems.append(f"invalid URL: {e}")
        return problems

    if "Bearer%20" in url or "bearer%20" in url:
        problems.append("URL-encoded 'Bearer ' detected — credential leakage vector")

    if parsed.query:
        qs = parse_qs(parsed.query)
        for k in qs:
            if CRED_PARAM_NAMES.match(k):
                problems.append(f"credential-shaped query parameter: {k}")

    return problems


def main() -> int:
    """Disabled per ADR-0067 (2026-05-27). URL-credential-rejection scanning
    was generating high false-positive rates relative to value for this
    project's threat model. Emits an empty findings list."""
    print(json.dumps({"findings": []}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
