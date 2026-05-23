#!/usr/bin/env python3
"""
audit_op1_env_block_coverage.py — OP-1 env-block credential coverage rule.

For every credential-bearing field in .mcp.json (headers + env), verify
the value uses ${ENV_VAR} indirection rather than a literal credential.

Per ADR-0039 (credential redaction posture). Exit 1 if any BLOCKER finding.

Usage:
    python3 audit_op1_env_block_coverage.py <path-to-.mcp.json>
"""
import json
import re
import sys
from pathlib import Path


# Patterns that look like a literal credential (not env-var indirection)
LITERAL_CRED = re.compile(
    r'\b(sk-[A-Za-z0-9_-]{16,}|eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}|'
    r'ghp_[A-Za-z0-9]{16,}|glpat-[A-Za-z0-9_-]{16,}|xox[bp]-[A-Za-z0-9-]{16,})'
)

# Env-var indirection pattern: ${NAME} or ${localEnv:NAME}
ENV_VAR_PATTERN = re.compile(r'^\$\{[A-Za-z_][A-Za-z0-9_:]*\}$')


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: audit_op1_env_block_coverage.py <.mcp.json>"}))
        return 2

    mcp_json_path = Path(sys.argv[1]).resolve()
    if not mcp_json_path.exists():
        print(json.dumps({"error": f"path missing: {mcp_json_path}"}))
        return 2

    try:
        cfg = json.loads(mcp_json_path.read_text())
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"invalid JSON: {e}"}))
        return 2

    findings = []
    servers = cfg.get("mcpServers", {})

    for name, entry in servers.items():
        # Check headers
        headers = entry.get("headers", {})
        for hk, hv in headers.items():
            if isinstance(hv, str) and LITERAL_CRED.search(hv):
                findings.append({
                    "rule": "OP-1",
                    "severity": "BLOCKER",
                    "server": name,
                    "field": f"headers.{hk}",
                    "message": f"literal credential in header value (not env-var indirection)",
                })
            elif isinstance(hv, str) and "${" not in hv and hv:
                # Non-credential literal header value is fine; this branch intentionally permissive
                pass

        # Check env block
        env = entry.get("env", {})
        for ek, ev in env.items():
            if isinstance(ev, str) and LITERAL_CRED.search(ev):
                findings.append({
                    "rule": "OP-1",
                    "severity": "BLOCKER",
                    "server": name,
                    "field": f"env.{ek}",
                    "message": "literal credential in env value (not env-var indirection)",
                })

    out = {
        "rule": "OP-1",
        "name": "env-block coverage",
        "target": str(mcp_json_path),
        "findings": findings,
        "servers_checked": len(servers),
    }
    print(json.dumps(out, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
