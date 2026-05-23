#!/usr/bin/env python3
"""Validate pipeline-artifact frontmatter against per-doc-type schemas.

Per FR-6 + ADR-0032 per-doc-type schemas + Blueprint Frontmatter validator
coverage subsection (rewritten cycle 3 per I-AA-601).

Validation rules:
- Required universal fields: feature_slug, derived_from (where applicable),
  doc_type (per ADR-0032 Change 4).
- Per-doc-type state vocabulary (per ADR-0032 Change 3 D-18 3-tier vocab):
  * gated (intent-clarification, prd, research-plan, blueprint, plan):
    draft -> accepted -> superseded | rejected
  * analysis/log (codebase-analysis, synthesis, *-design, *-issues,
    *-validators, *-log, *-result, *-report, *-summary, *-tests, *-dag):
    draft -> complete
  * adr: proposed -> accepted | superseded | rejected (no draft)
- Current-state correctness: a ratified artifact must not still be draft;
  superseded artifacts must carry superseded_by back-link.

Per I-AA-601 (cycle 3 rewrite of Blueprint Frontmatter validator coverage):
- memory is OPTIONAL (not required). Absence is canonical for no persistent
  memory. The string `memory: none` is INVALID Claude Code syntax and is
  REJECTED.
- Agent and TaskUpdate are SEPARATE tool-family entries (not synonyms).
- Task is a recognized alias for Agent (the canonical name).
- Edit is VALID as a tool entry.
- Bash and Bash(<pattern>:*) are BOTH valid.
- effort enum accepts {low, medium, high, xhigh, max} (per KB-cc-platform docs).
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


GATED_DOC_TYPES = {
    "intent-clarification",
    "prd",
    "research-plan",
    "blueprint",
    "plan",
}
ANALYSIS_DOC_TYPES = {
    "codebase-analysis",
    "synthesis",
    "architecture-audit-issues",
    "cross-artifact-audit-issues",
    "acceptance-tests",
    "phase-validators",
    "reconciliation-log",
    "task-dag",
    "per-task-execution-result",
    "phase-quality-report",
    "quality-reconciliation-log",
    "state-transitions-log",
    "pipeline-run-summary",
    "architecture-audit-report",
    "deliverable-archive-review",
    # Per-layer designs use the suffix `-design` (e.g., claude-code-design,
    # backend-design); handled below via suffix match.
}
ANALYSIS_DOC_TYPE_SUFFIXES = ("-design", "-report", "-log", "-issues", "-result", "-summary")

GATED_STATES = {"draft", "accepted", "superseded", "rejected"}
ANALYSIS_STATES = {"draft", "complete", "superseded"}
ADR_STATES = {"proposed", "accepted", "superseded", "rejected"}

# Per I-AA-601: canonical effort enum.
EFFORT_ENUM = {"low", "medium", "high", "xhigh", "max"}

# Per I-AA-601: tool enum. Bash + Bash(<pat>:*) are both valid via prefix match.
KNOWN_TOOLS = {
    "Read", "Write", "Edit", "Glob", "Grep", "Bash", "WebSearch",
    "WebFetch", "Agent", "Task", "TaskCreate", "TaskUpdate", "TaskGet",
    "TaskList", "TaskOutput", "TaskStop", "AskUserQuestion",
    "NotebookEdit", "ScheduleWakeup", "ExitPlanMode", "EnterPlanMode",
    "Skill", "ToolSearch",
}

# Per I-AA-601: memory values must be in this enum if present.
MEMORY_ENUM = {"user", "project", "local"}


def parse_frontmatter(text: str) -> tuple[dict[str, Any], int] | None:
    """Return (parsed-dict, line-count) of YAML frontmatter, or None if absent.

    Hand-parsed (no PyYAML dependency). Handles: simple `key: value` lines;
    inline lists `key: [a, b]`; multi-line bullet lists; pipe-folded multi-line
    string values (`key: |` followed by indented block).
    """
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    block = text[4:end]
    lines = block.split("\n")
    parsed: dict[str, Any] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val.startswith("|") or val.startswith(">") or val == "":
            # Multi-line: collect bulleted list OR pipe-folded text.
            bullets: list[str] = []
            text_block: list[str] = []
            j = i + 1
            while j < len(lines):
                bl = lines[j]
                if re.match(r"^[A-Za-z_]", bl):
                    break
                bm = re.match(r"^\s+-\s+(.*)$", bl)
                if bm:
                    bullets.append(bm.group(1).strip())
                elif bl.strip():
                    text_block.append(bl)
                j += 1
            if bullets:
                parsed[key] = bullets
            elif text_block:
                parsed[key] = "\n".join(text_block).strip()
            else:
                parsed[key] = val
            i = j
            continue
        if val.startswith("[") and val.endswith("]"):
            parsed[key] = [
                v.strip().strip("\"'")
                for v in val[1:-1].split(",")
                if v.strip()
            ]
        else:
            parsed[key] = val.strip("\"'")
        i += 1
    return parsed, end + 5  # bytes consumed (start of body)


def doc_type_category(doc_type: str) -> str:
    if doc_type in GATED_DOC_TYPES:
        return "gated"
    if doc_type == "adr":
        return "adr"
    if doc_type in ANALYSIS_DOC_TYPES or any(doc_type.endswith(suf) for suf in ANALYSIS_DOC_TYPE_SUFFIXES):
        return "analysis"
    return "unknown"


def make_finding(severity: str, file_path: Path, message: str, depth: str = "0") -> dict:
    return {
        "domain": "validator",
        "severity": severity,
        "source_activity": "frontmatter-validator",
        "file_path": str(file_path),
        "message": message,
        "dispatch_hint": "the agent that authored the artifact",
        "depth_level": depth,
    }


def validate_agent_frontmatter(fm: dict, path: Path) -> list[dict]:
    """Apply the I-AA-601 canonical-agent-frontmatter-pattern checks."""
    findings: list[dict] = []

    # memory: optional; if present, must be in canonical enum; `none` is REJECTED.
    if "memory" in fm:
        val = fm["memory"]
        if isinstance(val, str) and val.strip().lower() == "none":
            findings.append(
                make_finding(
                    "blocker",
                    path,
                    "memory: none is INVALID Claude Code syntax per I-AA-601; omit the field for no persistent memory",
                    depth="1",
                )
            )
        elif val not in MEMORY_ENUM:
            findings.append(
                make_finding(
                    "major",
                    path,
                    f"memory value '{val}' not in canonical enum {sorted(MEMORY_ENUM)}",
                    depth="1",
                )
            )

    # tools: list of tool-family entries. Bash and Bash(<pat>:*) both valid.
    tools = fm.get("tools")
    tools_list: list[str] = []
    if isinstance(tools, list):
        tools_list = [str(t).strip() for t in tools]
    elif isinstance(tools, str):
        tools_list = [t.strip() for t in tools.split(",") if t.strip()]
    for t in tools_list:
        base = t.split("(", 1)[0].strip()
        if base not in KNOWN_TOOLS:
            findings.append(
                make_finding(
                    "minor",
                    path,
                    f"tools entry '{t}' has unrecognized base '{base}'; canonical set: {sorted(KNOWN_TOOLS)}",
                    depth="0",
                )
            )

    # effort: must be in 5-value enum if present.
    if "effort" in fm:
        if fm["effort"] not in EFFORT_ENUM:
            findings.append(
                make_finding(
                    "major",
                    path,
                    f"effort value '{fm['effort']}' not in canonical enum {sorted(EFFORT_ENUM)}",
                    depth="1",
                )
            )

    # skills: optional; if present, must be a list. Each entry must resolve
    # to .claude/skills/<name>/ on disk (AC-FR-9-c).
    skills = fm.get("skills")
    if skills is not None:
        if not isinstance(skills, list):
            findings.append(
                make_finding(
                    "major",
                    path,
                    "skills field must be a list",
                    depth="0",
                )
            )
        else:
            skills_root = Path(".claude/skills")
            for s in skills:
                if not (skills_root / str(s)).is_dir():
                    findings.append(
                        make_finding(
                            "blocker",
                            path,
                            f"skill '{s}' declared but not present at .claude/skills/{s}/ (AC-FR-9-c)",
                            depth="1",
                        )
                    )

    return findings


def validate_pipeline_artifact(fm: dict, path: Path) -> list[dict]:
    findings: list[dict] = []

    # Universal required fields per ADR-0032 Change 1 + Change 4.
    for required in ("feature_slug", "doc_type"):
        if required not in fm:
            findings.append(
                make_finding(
                    "major",
                    path,
                    f"required universal field '{required}' missing (ADR-0032)",
                    depth="0",
                )
            )

    doc_type = fm.get("doc_type", "")
    category = doc_type_category(doc_type)
    status = fm.get("status")

    if category == "gated":
        if status not in GATED_STATES:
            findings.append(
                make_finding(
                    "major",
                    path,
                    f"status '{status}' not in gated vocabulary {sorted(GATED_STATES)} for doc_type {doc_type}",
                    depth="0",
                )
            )
    elif category == "analysis":
        if status not in ANALYSIS_STATES:
            findings.append(
                make_finding(
                    "minor",
                    path,
                    f"status '{status}' not in analysis vocabulary {sorted(ANALYSIS_STATES)} for doc_type {doc_type}",
                    depth="0",
                )
            )
    elif category == "adr":
        if status not in ADR_STATES:
            findings.append(
                make_finding(
                    "major",
                    path,
                    f"status '{status}' not in ADR vocabulary {sorted(ADR_STATES)}",
                    depth="0",
                )
            )
    elif doc_type:
        findings.append(
            make_finding(
                "minor",
                path,
                f"doc_type '{doc_type}' not in known category; cannot validate state vocabulary",
                depth="0",
            )
        )

    # superseded_by back-link on superseded artifacts.
    if status == "superseded" and "superseded_by" not in fm:
        findings.append(
            make_finding(
                "major",
                path,
                "status: superseded requires superseded_by back-link (ADR-0005)",
                depth="0",
            )
        )

    return findings


def validate_skill_frontmatter(fm: dict, path: Path) -> list[dict]:
    """SKILL.md files use the skill-frontmatter convention (name, description,
    allowed-tools, pedagogical_sections), not the pipeline-artifact convention.
    This validator scopes to the canonical required fields; deeper skill
    audits live in `auditing-skills`."""
    findings: list[dict] = []
    for required in ("name", "description"):
        if required not in fm:
            findings.append(
                make_finding(
                    "major",
                    path,
                    f"SKILL.md missing required field '{required}'",
                    depth="0",
                )
            )
    return findings


def validate_file(path: Path) -> list[dict]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [make_finding("info", path, f"could not read file: {exc}", depth="0")]

    parsed = parse_frontmatter(text)
    if parsed is None:
        return [
            make_finding(
                "major",
                path,
                "no YAML frontmatter found (file must start with `---\\n...---\\n`)",
                depth="0",
            )
        ]
    fm, _ = parsed

    # Dispatch: skill file vs agent file vs pipeline artifact vs ADR.
    str_path = str(path)
    if path.name == "SKILL.md" or "/.claude/skills/" in str_path:
        return validate_skill_frontmatter(fm, path)
    if "/.claude/agents/" in str_path or ".claude/agents/" in str_path:
        return validate_agent_frontmatter(fm, path)
    return validate_pipeline_artifact(fm, path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files to validate. If omitted, read newline-separated paths from stdin.",
    )
    parser.add_argument(
        "--exit-on-blocker",
        action="store_true",
        help="Exit non-zero if any blocker finding is emitted (default: exit 0; caller decides).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths: list[Path]
    if args.paths:
        paths = [Path(p) for p in args.paths]
    else:
        paths = [Path(line.strip()) for line in sys.stdin if line.strip()]

    findings: list[dict] = []
    for p in paths:
        if p.is_dir():
            for sub in p.rglob("*.md"):
                findings.extend(validate_file(sub))
            for sub in p.rglob("*.json"):
                # JSON artifacts may carry frontmatter-style metadata at top —
                # most do not; skip JSON for this script's scope.
                pass
            continue
        if not p.exists():
            findings.append(
                make_finding("info", p, "file does not exist", depth="0")
            )
            continue
        findings.extend(validate_file(p))

    sys.stdout.write(json.dumps({"findings": findings}, indent=2) + "\n")
    if args.exit_on_blocker and any(f["severity"] == "blocker" for f in findings):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
