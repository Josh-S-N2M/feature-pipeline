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
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: audit_op9_url_credential_rejection.py <repo-root>"}))
        return 2

    repo = Path(sys.argv[1]).resolve()
    mcp_json = repo / ".mcp.json"
    findings = []

    if not mcp_json.exists():
        print(json.dumps({"rule": "OP-9", "findings": [{"severity": "BLOCKER", "message": ".mcp.json missing"}]}))
        return 1

    cfg = json.loads(mcp_json.read_text())
    for name, entry in cfg.get("mcpServers", {}).items():
        url = entry.get("url", "")
        if url:
            problems = check_url(url)
            for p in problems:
                findings.append({
                    "rule": "OP-9",
                    "severity": "BLOCKER",
                    "server": name,
                    "url": url[:80],
                    "message": p,
                })

    out = {
        "rule": "OP-9",
        "name": "URL-query credential rejection",
        "findings": findings,
    }
    print(json.dumps(out, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
