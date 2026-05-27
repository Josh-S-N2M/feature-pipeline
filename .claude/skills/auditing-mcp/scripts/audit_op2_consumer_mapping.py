#!/usr/bin/env python3
"""
audit_op2_consumer_mapping.py — OP-2 per-agent consumer-mapping rule.

For each consumer agent (per Blueprint Sub-Agents table), verify the agent
file's `tools:` array includes EXACTLY the prescribed `mcp__<server>__*`
entries — no more, no less.

The canonical mapping (per Blueprint v3.0.2 + ADR-0040 5-agent Serena narrowing
+ ADR-0066 gitnexus removal 2026-05-27):

  design-cicd                      → mcp__actionlint-mcp__lint_workflow,
                                       mcp__actionlint-mcp__check_all_workflows,
                                       mcp__serena__*
  design-iac                       → mcp__terraform-mcp__*
  discovery-external-researcher    → mcp__context7__resolve-library-id,
                                       mcp__context7__query-docs,
                                       mcp__exa__web_search_exa,
                                       mcp__exa__company_research_exa,
                                       mcp__exa__crawling_exa
  discovery-codebase-researcher    → mcp__serena__*
  review-architecture-auditor      → mcp__serena__*
  design-claude-code               → mcp__serena__*
  design-codespaces                → mcp__serena__*

Usage:
    python3 audit_op2_consumer_mapping.py <repo-root>
"""
import json
import re
import sys
from pathlib import Path


CANONICAL = {
    "design-cicd": {
        "mcp__actionlint-mcp__lint_workflow",
        "mcp__actionlint-mcp__check_all_workflows",
        "mcp__serena__*",
    },
    "design-iac": {"mcp__terraform-mcp__*"},
    "discovery-external-researcher": {
        "mcp__context7__resolve-library-id",
        "mcp__context7__query-docs",
        "mcp__exa__web_search_exa",
        "mcp__exa__company_research_exa",
        "mcp__exa__crawling_exa",
    },
    "discovery-codebase-researcher": {"mcp__serena__*"},
    "review-architecture-auditor": {"mcp__serena__*"},
    "design-claude-code": {"mcp__serena__*"},
    "design-codespaces": {"mcp__serena__*"},
}

TOOLS_LINE_RE = re.compile(r'^tools:\s*\[(.*)\]\s*$')
MCP_ENTRY_RE = re.compile(r'mcp__[A-Za-z0-9_-]+__[A-Za-z0-9_*-]+')


def extract_mcp_entries(agent_path: Path) -> set[str]:
    entries: set[str] = set()
    for line in agent_path.read_text().splitlines()[:20]:
        m = TOOLS_LINE_RE.match(line)
        if m:
            entries.update(MCP_ENTRY_RE.findall(m.group(1)))
            break
    return entries


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: audit_op2_consumer_mapping.py <repo-root>"}))
        return 2

    repo = Path(sys.argv[1]).resolve()
    agents_dir = repo / ".claude" / "agents"

    if not agents_dir.is_dir():
        print(json.dumps({"error": f"agents dir missing: {agents_dir}"}))
        return 2

    findings = []
    for agent_name, expected in CANONICAL.items():
        path = agents_dir / f"{agent_name}.md"
        if not path.exists():
            findings.append({
                "rule": "OP-2",
                "severity": "BLOCKER",
                "agent": agent_name,
                "message": f"agent file missing: {path}",
            })
            continue
        actual = extract_mcp_entries(path)
        missing = expected - actual
        extra = actual - expected
        if missing:
            findings.append({
                "rule": "OP-2",
                "severity": "MAJOR",
                "agent": agent_name,
                "message": f"missing mcp__ entries: {sorted(missing)}",
            })
        if extra:
            findings.append({
                "rule": "OP-2",
                "severity": "MAJOR",
                "agent": agent_name,
                "message": f"extra mcp__ entries (not in canonical mapping): {sorted(extra)}",
            })

    out = {
        "rule": "OP-2",
        "name": "consumer-mapping",
        "target": str(agents_dir),
        "findings": findings,
        "agents_checked": len(CANONICAL),
    }
    print(json.dumps(out, indent=2))
    return 1 if any(f.get("severity") == "BLOCKER" for f in findings) else (2 if findings else 0)


if __name__ == "__main__":
    sys.exit(main())
