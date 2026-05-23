#!/usr/bin/env python3
"""
audit_op4_primary_fallback_prose.py — OP-4 primary/fallback prose preservation.

Verifies that the four canonical prose references to GitNexus primary + codebase-memory-mcp
fallback policy in discovery-codebase-researcher.md are present (per ADR-0007 v2.2.0).
Per Plan T1.5 — preserve lines 3, 20, 29, 156 verbatim (the OP-4 audit rule depends on them).

Note: line numbers in the plan refer to KB-codebase-research/SKILL.md and
discovery-codebase-researcher.md collectively. After T1.5 cycle-3-aware updates
("ADR-0018 + ADR-0038"), the line numbers shift; the audit checks by content
substring, not by exact line number.

Usage:
    python3 audit_op4_primary_fallback_prose.py <repo-root>
"""
import json
import sys
from pathlib import Path


REQUIRED_SUBSTRINGS = [
    # Primary/fallback policy mentions (any of these are sufficient per occurrence-count check)
    "GitNexus",
    "codebase-memory-mcp",
    "primary",
    "fallback",
]

CHECKED_FILES = [
    ".claude/agents/discovery-codebase-researcher.md",
    ".claude/skills/KB-codebase-research/SKILL.md",
]


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: audit_op4_primary_fallback_prose.py <repo-root>"}))
        return 2

    repo = Path(sys.argv[1]).resolve()

    findings = []
    files_checked = []

    for rel in CHECKED_FILES:
        path = repo / rel
        if not path.exists():
            findings.append({
                "rule": "OP-4",
                "severity": "BLOCKER",
                "file": rel,
                "message": f"required file missing: {path}",
            })
            continue

        text = path.read_text()
        files_checked.append(rel)

        # Each required substring must appear at least once
        for needle in REQUIRED_SUBSTRINGS:
            if needle not in text:
                findings.append({
                    "rule": "OP-4",
                    "severity": "MAJOR",
                    "file": rel,
                    "message": f"required primary/fallback prose token '{needle}' not found",
                })

    out = {
        "rule": "OP-4",
        "name": "primary/fallback prose preservation",
        "files_checked": files_checked,
        "required_substrings": REQUIRED_SUBSTRINGS,
        "findings": findings,
    }
    print(json.dumps(out, indent=2))
    return 1 if any(f["severity"] == "BLOCKER" for f in findings) else (2 if findings else 0)


if __name__ == "__main__":
    sys.exit(main())
