#!/usr/bin/env python3
"""
scan_mcp_secrets.py — Scan MCP server configs for literal credentials.

Detects:
  - MC-1: literal credential in env block
  - MC-7: literal credential in headers

Uses FAKE_CREDENTIAL_INDICATORS allow-list.

Usage:
    python3 scan_mcp_secrets.py <path-to-settings.json | .mcp.json>
"""
import json
import re
import sys
from pathlib import Path

FAKE_CREDENTIAL_INDICATORS = [
    "EXAMPLE", "FAKE", "PLACEHOLDER", "XXXXXX",
    "YOUR_", "REPLACE_ME", "1234567890", "ABCDEFGH",
]

PATTERNS = [
    ("SEC-AWS-AKIA",
     re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
     "AWS access key ID"),
    ("SEC-GITHUB-PAT",
     re.compile(r"\bghp_[A-Za-z0-9]{36}\b"),
     "GitHub classic PAT"),
    ("SEC-GITHUB-FINE",
     re.compile(r"\bgithub_pat_[A-Za-z0-9_]{82}\b"),
     "GitHub fine-grained PAT"),
    ("SEC-ANTHROPIC",
     re.compile(r"\bsk-ant-api03-[A-Za-z0-9_\-]{80,}\b"),
     "Anthropic API key"),
    ("SEC-OPENAI",
     re.compile(r"\bsk-proj-[A-Za-z0-9_\-]{40,}\b"),
     "OpenAI API key"),
    ("SEC-GENERIC",
     re.compile(r"\b[A-Za-z0-9_+/=]{32,}\b"),
     "High-entropy string (possible credential)"),
]


def is_fake(s: str) -> bool:
    return any(ind in s.upper() for ind in FAKE_CREDENTIAL_INDICATORS)


def is_env_ref(s: str) -> bool:
    return isinstance(s, str) and bool(re.match(r"^\$\{[A-Z_][A-Z0-9_]*\}$", s.strip()))


def scan_dict(d: dict, name: str, location: str, dim: int) -> list[dict]:
    findings = []
    for k, v in d.items():
        if not isinstance(v, str):
            continue
        if is_env_ref(v):
            continue
        # For Authorization header, check for Bearer pattern
        bearer = re.match(r"^Bearer\s+(.+)$", v, re.I)
        scan_val = bearer.group(1) if bearer else v
        for pid, pattern, desc in PATTERNS:
            for m in pattern.finditer(scan_val):
                if is_fake(m.group(0)):
                    continue
                findings.append({
                    "dimension": dim, "severity": "BLOCKER",
                    "is_security_critical": True,
                    "pattern_id": pid,
                    "what": f"Literal credential in {name}.{k}: {desc}. ({'MC-7' if 'header' in name.lower() else 'MC-1'})",
                    "fix": f"Replace with `${{...}}` reference: `\"{k}\": \"${{{k.upper()}}}\"`.",
                    "location": location, "where": location,
                })
                break
    return findings


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: scan_mcp_secrets.py <path>"}))
        return 2

    path = Path(sys.argv[1]).resolve()
    if not path.is_file():
        print(json.dumps({"error": f"not a file: {path}"}))
        return 2

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(json.dumps({"findings": []}))
        return 0

    mcp_servers = data.get("mcpServers", data) if isinstance(data, dict) else {}
    if not isinstance(mcp_servers, dict):
        print(json.dumps({"findings": []}))
        return 0

    findings = []
    for name, server in mcp_servers.items():
        if not isinstance(server, dict):
            continue
        env = server.get("env", {})
        if isinstance(env, dict):
            findings.extend(scan_dict(env, f"servers.{name}.env", str(path), 3))
        headers = server.get("headers", {})
        if isinstance(headers, dict):
            findings.extend(scan_dict(headers, f"servers.{name}.headers", str(path), 3))

    print(json.dumps({"target": str(path), "findings": findings}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
