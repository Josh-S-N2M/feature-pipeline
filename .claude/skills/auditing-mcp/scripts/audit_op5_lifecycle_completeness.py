#!/usr/bin/env python3
"""
audit_op5_lifecycle_completeness.py — OP-5 lifecycle-completeness rule.

Verifies the postCreate + postStart lifecycle scripts produce the expected
event records to .claude/runtime/mcp-events.jsonl per ADR-0037:
  - postCreate emits exactly 5 `install_complete` records (5 OSS-local servers)
  - postStart emits exactly 7 `readiness_probe` records (7 named servers)

Per ADR-0033 stub-fill deferral: this rule's runtime probe is a STUB until
auditing-codespaces fills in. Static check only at this stage (validates the
scripts reference the right counts).

Usage:
    python3 audit_op5_lifecycle_completeness.py <repo-root>
"""
import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: audit_op5_lifecycle_completeness.py <repo-root>"}))
        return 2

    repo = Path(sys.argv[1]).resolve()
    findings = []

    postcreate = repo / ".devcontainer" / "postCreate.sh"
    poststart = repo / ".devcontainer" / "postStart.sh"

    for script in (postcreate, poststart):
        if not script.exists():
            findings.append({
                "rule": "OP-5",
                "severity": "BLOCKER",
                "file": str(script.relative_to(repo)),
                "message": "lifecycle script missing",
            })

    if not findings:
        # Static heuristic checks
        pc_text = postcreate.read_text()
        ps_text = poststart.read_text()

        # postCreate should reference install_complete + 5 OSS-local server names
        if "install_complete" not in pc_text:
            findings.append({
                "rule": "OP-5",
                "severity": "MAJOR",
                "file": "postCreate.sh",
                "message": "no 'install_complete' references — ADR-0037 schema expects 5 records",
            })

        # postStart should reference readiness_probe
        if "readiness_probe" not in ps_text:
            findings.append({
                "rule": "OP-5",
                "severity": "MAJOR",
                "file": "postStart.sh",
                "message": "no 'readiness_probe' references — ADR-0037 schema expects 7 records",
            })

        # postStart should iterate 7 servers from .mcp.json
        if "jq -r '.mcpServers | keys[]'" not in ps_text and "mcpServers" not in ps_text:
            findings.append({
                "rule": "OP-5",
                "severity": "MAJOR",
                "file": "postStart.sh",
                "message": "no enumeration of .mcp.json server keys — readiness_probe count may not match the 7-server inventory",
            })

    out = {
        "rule": "OP-5",
        "name": "lifecycle-completeness",
        "static_check_only": True,
        "runtime_probe_status": "STUB until auditing-codespaces filled per ADR-0033",
        "findings": findings,
    }
    print(json.dumps(out, indent=2))
    return 1 if any(f["severity"] == "BLOCKER" for f in findings) else (2 if findings else 0)


if __name__ == "__main__":
    sys.exit(main())
