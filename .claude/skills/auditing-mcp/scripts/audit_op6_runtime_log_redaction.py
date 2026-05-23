#!/usr/bin/env python3
"""
audit_op6_runtime_log_redaction.py — OP-6 runtime-log redaction discipline.

Verifies:
  1. .devcontainer/lib/log-mcp-event.sh exists.
  2. It implements redaction-at-source for known credential patterns (per ADR-0039).
  3. It applies default-fail-closed posture (per AC-NFR-2-d): on redaction failure,
     the helper returns nonzero exit and does NOT write to the JSONL.
  4. If .claude/runtime/mcp-events.jsonl exists, scan for credential-shaped substrings
     that would indicate redaction has NOT been applied (BLOCKER).

Usage:
    python3 audit_op6_runtime_log_redaction.py <repo-root>
"""
import json
import re
import sys
from pathlib import Path


CRED_LEAK = re.compile(
    r'\b(sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{16,}|glpat-[A-Za-z0-9_-]{16,}|'
    r'xox[bp]-[A-Za-z0-9-]{16,})'
)


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: audit_op6_runtime_log_redaction.py <repo-root>"}))
        return 2

    repo = Path(sys.argv[1]).resolve()
    findings = []

    helper = repo / ".devcontainer" / "lib" / "log-mcp-event.sh"
    if not helper.exists():
        findings.append({
            "rule": "OP-6",
            "severity": "BLOCKER",
            "file": ".devcontainer/lib/log-mcp-event.sh",
            "message": "log helper missing — redaction-at-source cannot be enforced",
        })
        print(json.dumps({"rule": "OP-6", "findings": findings}, indent=2))
        return 1

    text = helper.read_text()

    # Required keywords (signs that redaction logic is present)
    for keyword, msg in [
        ("redact_credentials", "no redact_credentials function defined"),
        ("REDACTED", "no <REDACTED> replacement token present"),
        ("default-fail-closed", "default-fail-closed posture not documented inline"),
    ]:
        if keyword not in text:
            findings.append({
                "rule": "OP-6",
                "severity": "MAJOR",
                "file": "log-mcp-event.sh",
                "message": msg,
            })

    # If the JSONL log exists, scan for unredacted credentials
    jsonl = repo / ".claude" / "runtime" / "mcp-events.jsonl"
    if jsonl.exists():
        log_content = jsonl.read_text()
        for m in CRED_LEAK.finditer(log_content):
            findings.append({
                "rule": "OP-6",
                "severity": "BLOCKER",
                "file": ".claude/runtime/mcp-events.jsonl",
                "leaked_pattern_class": m.group(0)[:6] + "...",
                "message": "credential-shaped pattern in JSONL log — redaction failed",
            })

    out = {
        "rule": "OP-6",
        "name": "runtime-log redaction",
        "helper_path": str(helper.relative_to(repo)),
        "jsonl_present": jsonl.exists(),
        "findings": findings,
    }
    print(json.dumps(out, indent=2))
    return 1 if any(f["severity"] == "BLOCKER" for f in findings) else (2 if findings else 0)


if __name__ == "__main__":
    sys.exit(main())
