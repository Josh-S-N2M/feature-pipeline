#!/usr/bin/env python3
"""
audit_op10_argv_leakage.py — OP-10 argv-leaked credential REJECT rule.

Per ADR-0039. Any argv-passed credential in .mcp.json `args` arrays is a BLOCKER.
The augmented auditing-mcp Gate-6 check (per ADR-0043) HALTS the orchestrator
on any OP-10 BLOCKER.

Patterns flagged:
  - --api-key / --apikey / --api_key
  - --token / --auth / --bearer
  - positional args matching credential-shaped patterns (sk-..., eyJ..., ghp_..., etc.)

Usage:
    python3 audit_op10_argv_leakage.py <repo-root>
"""
import json
import re
import sys
from pathlib import Path


CRED_FLAG = re.compile(r'^--(api[-_]?key|token|auth|bearer|access[-_]?token|secret|password|credential)$', re.IGNORECASE)

CRED_VALUE = re.compile(
    r'\b(sk-[A-Za-z0-9_-]{16,}|eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}|'
    r'ghp_[A-Za-z0-9]{16,}|glpat-[A-Za-z0-9_-]{16,}|xox[bp]-[A-Za-z0-9-]{16,})'
)


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: audit_op10_argv_leakage.py <repo-root>"}))
        return 2

    repo = Path(sys.argv[1]).resolve()
    mcp_json = repo / ".mcp.json"
    findings = []

    if not mcp_json.exists():
        print(json.dumps({"rule": "OP-10", "findings": [{"severity": "BLOCKER", "message": ".mcp.json missing"}]}))
        return 1

    cfg = json.loads(mcp_json.read_text())
    for name, entry in cfg.get("mcpServers", {}).items():
        args = entry.get("args", []) or []
        for i, arg in enumerate(args):
            if not isinstance(arg, str):
                continue
            if CRED_FLAG.match(arg):
                findings.append({
                    "rule": "OP-10",
                    "severity": "BLOCKER",
                    "server": name,
                    "arg_index": i,
                    "arg": arg,
                    "message": "credential-shaped CLI flag in args (use env-block indirection instead)",
                })
            if CRED_VALUE.search(arg):
                findings.append({
                    "rule": "OP-10",
                    "severity": "BLOCKER",
                    "server": name,
                    "arg_index": i,
                    "message": "credential-shaped value in args (literal credential leakage)",
                })

    out = {
        "rule": "OP-10",
        "name": "argv-leaked credentials",
        "findings": findings,
    }
    print(json.dumps(out, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
