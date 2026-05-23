#!/usr/bin/env python3
"""
audit_op3_zero_mcp_invariant.py — OP-3 zero-mcp invariant on untouched agents (C-0445).

For each agent file NOT in the 8-consumer canonical set, verify zero
`mcp__*` entries in the `tools:` array. Per blueprint Fact Disposition C-0445.

Usage:
    python3 audit_op3_zero_mcp_invariant.py <repo-root>
"""
import json
import re
import sys
from pathlib import Path


TOUCHED = {
    "design-api", "design-cicd", "design-iac",
    "discovery-external-researcher", "discovery-codebase-researcher",
    "review-architecture-auditor",
    "design-claude-code", "design-codespaces",
}

TOOLS_LINE_RE = re.compile(r'^tools:\s*\[(.*)\]\s*$')


def has_mcp_entry(agent_path: Path) -> bool:
    for line in agent_path.read_text().splitlines()[:20]:
        m = TOOLS_LINE_RE.match(line)
        if m and "mcp__" in m.group(1):
            return True
    return False


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: audit_op3_zero_mcp_invariant.py <repo-root>"}))
        return 2

    repo = Path(sys.argv[1]).resolve()
    agents_dir = repo / ".claude" / "agents"

    if not agents_dir.is_dir():
        print(json.dumps({"error": f"agents dir missing: {agents_dir}"}))
        return 2

    findings = []
    untouched_checked = 0
    total_files = 0

    for agent_file in sorted(agents_dir.glob("*.md")):
        total_files += 1
        name = agent_file.stem
        if name in TOUCHED:
            continue
        untouched_checked += 1
        if has_mcp_entry(agent_file):
            findings.append({
                "rule": "OP-3",
                "severity": "BLOCKER",
                "agent": name,
                "message": f"agent has mcp__ entries but is NOT in the canonical consumer set (C-0445 violation)",
            })

    out = {
        "rule": "OP-3",
        "name": "zero-mcp invariant on 28 untouched agents",
        "target": str(agents_dir),
        "total_agent_files": total_files,
        "untouched_checked": untouched_checked,
        "expected_untouched": total_files - len(TOUCHED),
        "findings": findings,
    }
    print(json.dumps(out, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
