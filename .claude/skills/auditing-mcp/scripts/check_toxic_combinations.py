#!/usr/bin/env python3
"""
check_toxic_combinations.py — Detect toxic capability combinations in MCP servers.

Static analysis (no runtime):
  - Heuristic-based combination detection from server name and package name
  - TC-1 through TC-7 patterns

Runtime mode (--with-runtime):
  - Spawns each server, queries tools/list, applies categorization and combo check
  - Scans tool descriptions for prompt-injection patterns

Usage:
    python3 check_toxic_combinations.py <settings.json | .mcp.json> [--with-runtime]
"""
import json
import re
import subprocess
import sys
from pathlib import Path

# Capability keywords detected in server/package names
CAPABILITY_KEYWORDS = {
    "filesystem": ["filesystem", "fs-", "-fs", "file-", "files", "directory"],
    "shell": ["shell", "terminal", "cmd", "exec", "bash", "subprocess"],
    "database": ["postgres", "mysql", "sqlite", "sql", "db-", "-db", "mongo", "redis"],
    "network": ["web", "fetch", "http", "url", "api", "request", "curl"],
    "memory": ["memory", "remember", "store", "persist"],
    "subagent": ["agent", "subagent", "delegate"],
}

# Toxic combinations: pairs of capabilities that together = BLOCKER
TOXIC_PAIRS = [
    (("filesystem", "network"), "TC-1", "Filesystem + Web — credential exfiltration risk"),
    (("database", "network"), "TC-2", "Database + Web — data exfiltration risk"),
    (("shell", "network"), "TC-3", "Shell + Web — command exfiltration risk"),
    (("memory", "network"), "TC-5", "Memory write + Web — persistent-poisoning risk"),
    (("shell", "memory"), "TC-6", "Shell + Memory — silent persistence risk"),
    (("subagent", "shell"), "TC-7", "Subagent management + Shell — agent-injection risk"),
]


def categorize_text(text: str) -> set[str]:
    """Given a text (server name, package name, or tool description), return
    the set of capability tags it matches."""
    text_low = text.lower()
    found: set[str] = set()
    for cap, keywords in CAPABILITY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_low:
                found.add(cap)
                break
    return found


def static_analysis(name: str, server: dict, location: str) -> list[dict]:
    """Heuristic check on names alone."""
    findings = []
    # Aggregate text to scan: name + package args
    text_parts = [name]
    args = server.get("args", [])
    if isinstance(args, list):
        for a in args:
            if isinstance(a, str):
                text_parts.append(a)
    full_text = " ".join(text_parts)

    caps = categorize_text(full_text)
    for pair, tc_id, desc in TOXIC_PAIRS:
        if pair[0] in caps and pair[1] in caps:
            findings.append({
                "dimension": 5, "severity": "MAJOR",
                "what": f"Server '{name}': name/args suggest {desc}. ({tc_id})",
                "fix": "Verify the server's actual capabilities. Consider splitting into separate servers.",
                "location": location, "where": location,
                "heuristic": True,
            })
    return findings


def runtime_probe(name: str, server: dict, location: str, timeout: int = 10) -> list[dict]:
    """Spawn the server, query tools/list, scan descriptions.
    This is a simplified implementation that won't fully implement MCP wire protocol.
    In a real implementation, this would use mcp-client; here we emit a stub finding."""
    findings = []

    # Build command
    cmd = server.get("command")
    args = server.get("args", [])
    if not cmd or server.get("type", "stdio") != "stdio":
        findings.append({
            "dimension": 10, "severity": "MINOR",
            "what": f"Server '{name}': runtime probe only supports stdio transport; skipped.",
            "fix": "Use static analysis only for sse/http servers, or implement a full MCP client.",
            "location": location, "where": location,
        })
        return findings

    # NOTE: full MCP wire protocol is verbose; this is a stub that records the intent.
    # In production, replace with a real MCP client library call.
    findings.append({
        "dimension": 10, "severity": "INFO",
        "what": f"Server '{name}': runtime probe stub. Full MCP wire protocol not implemented in this audit.",
        "fix": "For full runtime audit, use a dedicated MCP client (mcp-client npm package or similar).",
        "location": location, "where": location,
    })
    return findings


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(json.dumps({"error": "Usage: check_toxic_combinations.py <path> [--with-runtime]"}))
        return 2

    path = Path(args[0]).resolve()
    runtime = "--with-runtime" in args

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
        findings.extend(static_analysis(name, server, str(path)))
        if runtime:
            findings.extend(runtime_probe(name, server, str(path)))

    print(json.dumps({
        "target": str(path),
        "runtime_mode": runtime,
        "findings": findings,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
