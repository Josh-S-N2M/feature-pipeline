#!/usr/bin/env python3
"""
audit_canonical_drift.py — CANON-1 drift detector.

Surfaces when an audit script under .claude/skills/auditing-*/ defines its
own copy of a constant whose canonical home is .claude/canonical/. Closes
the loophole that allowed three constants (SEVERITY_ORDER, NAME_PATTERN,
KNOWN_TOOLS) to silently drift before 2026-05-27.

Watched constants (per .claude/canonical/audit-rules.yaml drift_detection_rule):
  KNOWN_TOOLS, VALID_EVENTS, SEVERITY_ORDER, NAME_PATTERN,
  RECOGNIZED_FIELDS, KNOWN_FIELDS, GATED_DOC_TYPES, ISSUE_DOC_TYPES,
  ISSUE_STATES, GATED_STATES, ANALYSIS_STATES, ADR_STATES, EFFORT_ENUM

Exception: if a script's definition is on a line whose source also imports
from `canonical`, it is treated as a derived/alias assignment and not a
violation. Same for `frontmatter` import (the shared parser).

Usage:
    python3 audit_canonical_drift.py <repo-root>

Exits 0 always; emits findings via `{"findings": [...]}` on stdout.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def _find_repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / ".claude" / "canonical").is_dir():
            return p
    raise RuntimeError(f"Could not find repo root from {start}")


def main() -> int:
    if len(sys.argv) < 2:
        # Default to walking up from this file
        repo = _find_repo_root(Path(__file__).resolve())
    else:
        repo = Path(sys.argv[1]).resolve()

    # Bootstrap canonical accessor
    _shared = repo / ".claude" / "skills" / "auditing-shared" / "scripts"
    sys.path.insert(0, str(_shared))
    from canonical import audit_rules  # noqa: E402

    watched = audit_rules.DRIFT_DETECTION_WATCHED_NAMES
    findings: list[dict] = []

    audit_skills_dir = repo / ".claude" / "skills"
    for skill_dir in sorted(audit_skills_dir.glob("auditing-*")):
        scripts_dir = skill_dir / "scripts"
        if not scripts_dir.is_dir():
            continue
        for script in sorted(scripts_dir.glob("*.py")):
            text = script.read_text(encoding="utf-8", errors="replace")
            # Skip the canonical accessor itself and the drift-detector itself
            if script.name in ("canonical.py", "audit_canonical_drift.py"):
                continue
            # Does the script import from canonical or frontmatter?
            imports_canonical = bool(
                re.search(r"from\s+canonical\s+import\b", text)
                or re.search(r"^import\s+canonical\b", text, re.MULTILINE)
            )
            imports_frontmatter = bool(
                re.search(r"from\s+frontmatter\s+import\b", text)
            )
            # Scan for any watched-constant defined at module level
            for i, line in enumerate(text.split("\n"), start=1):
                m = re.match(r"^([A-Z][A-Z_0-9]+)\s*=", line)
                if not m:
                    continue
                name = m.group(1)
                if name not in watched:
                    continue
                # If the right-hand-side mentions `_tools.` / `_severity.` /
                # `_naming.` / `_ff.` / `_dt.` or `canonical.`, treat as derived
                # alias (not drift).
                if any(tok in line for tok in (
                    "_tools.", "_severity.", "_naming.", "_ff.", "_dt.",
                    "canonical.", "_severity.ORDER", "_ff.SKILL_RECOGNIZED",
                    "_ff.SUBAGENT_RECOGNIZED", "_dt.", "_tools.KNOWN_TOOLS",
                )):
                    continue
                # If the script imports canonical and this is on the same
                # line as an aliased name, also accept
                if imports_canonical and ("=" in line and line.split("=", 1)[1].strip().startswith("_")):
                    continue
                findings.append({
                    "rule": "CANON-1",
                    "severity": "BLOCKER",
                    "what": (
                        f"{script.relative_to(repo)} line {i} defines {name!r} locally; "
                        f"this constant has a canonical home in .claude/canonical/. "
                        f"Import from auditing-shared/scripts/canonical instead."
                    ),
                    "fix": (
                        f"Replace the local definition with `from canonical import …` "
                        f"and reference {name} via the shared accessor."
                    ),
                    "location": f"{script.relative_to(repo)}:{i}",
                    "where": f"{script.relative_to(repo)}:{i}",
                    "dimension": 1,
                })

    print(json.dumps({"rule": "CANON-1", "findings": findings}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
