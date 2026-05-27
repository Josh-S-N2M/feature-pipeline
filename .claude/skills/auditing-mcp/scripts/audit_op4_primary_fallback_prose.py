#!/usr/bin/env python3
"""
audit_op4_primary_fallback_prose.py — OP-4 extraction-method prose preservation.

Verifies that the canonical prose references to the code-graph fallback
discipline in discovery-codebase-researcher.md and KB-codebase-research/SKILL.md
are present. Per ADR-0066 (2026-05-27), gitnexus was removed; the canonical
posture is now Read+Grep+Glob plus serena symbol tools, with `extraction_method`
recorded in `codebase-analysis.json`.

Per Plan T1.5 — the audit checks by content substring, not by exact line number.

Usage:
    python3 audit_op4_primary_fallback_prose.py <repo-root>
"""
import json
import sys
from pathlib import Path


REQUIRED_SUBSTRINGS = [
    # Extraction-method discipline tokens (any of these are sufficient per occurrence-count check)
    "serena",
    "extraction_method",
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
