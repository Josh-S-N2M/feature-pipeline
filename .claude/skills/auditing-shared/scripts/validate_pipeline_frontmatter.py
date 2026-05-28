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

# Bootstrap canonical accessor (single source of truth — see .claude/canonical/).
_here = Path(__file__).resolve()
for _p in _here.parents:
    if (_p / ".claude" / "canonical").is_dir():
        sys.path.insert(0, str(_p / ".claude" / "skills" / "auditing-shared" / "scripts"))
        break
from canonical import doc_types as _dt, tools as _tools  # noqa: E402

GATED_DOC_TYPES = _dt.GATED_DOC_TYPES
ANALYSIS_DOC_TYPES = _dt.ANALYSIS_DOC_TYPES
ANALYSIS_DOC_TYPE_SUFFIXES = ("-design", "-report", "-log", "-issues", "-result", "-summary")

GATED_STATES = _dt.GATED_STATES
ANALYSIS_STATES = _dt.ANALYSIS_STATES
ADR_STATES = _dt.ADR_STATES

# ---- Issue artifact constants (canonical: .claude/canonical/doc-types.yaml) ----

ISSUE_DOC_TYPES = _dt.ISSUE_DOC_TYPES
ISSUE_STATES = _dt.ISSUE_STATES   # canonical already includes legacy `wontfix-with-rationale` alias
# Convert canonical's list-of-fields to a tuple-of-fields keyed by state.
ISSUE_PER_STATE_REQUIRED_FIELDS = {
    state: tuple(_dt.ISSUE_PER_STATE_REQUIRED_FIELDS.get(state, []))
    for state in _dt.ISSUE_STATES
}

ISSUE_NON_VALIDATED_PATH_PREFIXES = (
    "Issues/*/evidence/",
    "Issues/*/updates/",
)

EFFORT_ENUM = _dt.EFFORT_ENUM
KNOWN_TOOLS = _tools.KNOWN_TOOLS

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
    if doc_type in ISSUE_DOC_TYPES:           # v2 addition per ADR-0050 §Decision §1
        return "issue"
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


# Per issue-doctypes-spec.md §7 (post-7b56248 fix): id derivation uses the
# SHORT form — uppercase BASE doctype (issue- prefix stripped) + hyphen +
# kebab-case topic slug. The regex matches the same form.
_ISSUE_ID_PATTERN = re.compile(r"^(REGISTER|ANALYSIS|PROPOSAL)-[a-z][a-z0-9-]*$")


def is_valid_issue_id_syntax(value: str) -> bool:
    """True if `value` matches the SHORT-form Issues/ ID convention per
    issue-doctypes-spec.md §7: `<UPPERCASE-BASE-DOCTYPE>-<kebab-topic-slug>`
    where BASE is one of REGISTER / ANALYSIS / PROPOSAL."""
    return isinstance(value, str) and bool(_ISSUE_ID_PATTERN.match(value))


def validate_issue_artifact(fm: dict, path: Path) -> list[dict]:
    """Validate an Issues/<topic>/<doctype>.md file per ADR-0052 + ADR-0050 +
    issue-doctypes-spec.md. Called from validate_pipeline_artifact when
    doc_type_category returns "issue"."""
    findings: list[dict] = []
    doc_type = fm.get("doc_type")
    status = fm.get("status")

    # Check 1 — status must be in the 5-state vocabulary (per ADR-0050 §3, spec §3.3).
    # Short-circuit if invalid; per-state rules below require a known state.
    if status not in ISSUE_STATES:
        findings.append(make_finding(
            severity="blocker",
            file_path=path,
            message=f"status '{status}' not in issue vocabulary {sorted(ISSUE_STATES)}",
        ))
        return findings  # short-circuit

    # Check 2 — per-state required companion fields (spec §4.2, ADR-0050 §4).
    # Uses the actual codebase idiom `field in fm` (cf. lines 314-323 in the
    # ADR-0005 superseded_by check).
    for field in ISSUE_PER_STATE_REQUIRED_FIELDS.get(status, ()):
        if field not in fm:
            findings.append(make_finding(
                severity="blocker",
                file_path=path,
                message=f"status:{status} requires companion field '{field}'",
            ))

    # Check 3 — proposes_future_feature advisory (spec §6, ADR-0050 §6).
    # When doc_type is issue-proposal and field is absent, emit info-severity.
    if doc_type == "issue-proposal" and "proposes_future_feature" not in fm:
        findings.append(make_finding(
            severity="info",
            file_path=path,
            message="issue-proposal recommends a 'proposes_future_feature' slug",
        ))

    # Check 4 — optional cross-link fields syntactic validation (spec §5, ADR-0046).
    # Validate when present; never required. Regex matches the
    # <UPPERCASE-BASE-DOCTYPE>-<kebab-topic-slug> form per spec §7 (SHORT form,
    # post-7b56248 fix).
    for field in ("escalates_from", "escalated_to", "rolled_into_register"):
        value = fm.get(field)
        if value is not None:
            # Support list values per ADR-0050 §5: "Optional fields support list
            # values where multiple evolution events touch the same file."
            values = value if isinstance(value, list) else [value]
            for v in values:
                if not is_valid_issue_id_syntax(v):
                    findings.append(make_finding(
                        severity="minor",
                        file_path=path,
                        message=f"field '{field}' value '{v}' does not match expected ID syntax "
                                f"<UPPERCASE-BASE-DOCTYPE>-<kebab-topic-slug> (spec §7)",
                    ))

    # Check 5 (per spec §7) — id MUST match path-derived expected id:
    # Expected = <UPPERCASE-BASE-DOCTYPE>-<kebab-topic-slug-from-path>
    # where topic-slug is the parent directory name of the file under Issues/.
    fm_id = fm.get("id")
    if fm_id and doc_type:
        base = doc_type.removeprefix("issue-").upper()  # issue-analysis → ANALYSIS
        # Topic slug is the parent directory name. Robustly handle both relative
        # and absolute paths (mirror the T2.2 path-prefix handling pattern).
        parts = path.parts
        if "Issues" in parts:
            idx = parts.index("Issues")
            if idx + 1 < len(parts):
                topic_slug = parts[idx + 1]
                expected_id = f"{base}-{topic_slug}"
                if fm_id != expected_id:
                    findings.append(make_finding(
                        severity="blocker",
                        file_path=path,
                        message=f"id '{fm_id}' does not match path-derived expected id '{expected_id}' "
                                f"(spec §7: <UPPERCASE-BASE-DOCTYPE>-<kebab-topic-slug>)",
                    ))

    return findings


def validate_pipeline_artifact(fm: dict, path: Path) -> list[dict]:
    findings: list[dict] = []

    # v3 addition (per I-AA-002 honoring ADR-0051 §Decision §4 + spec §2.3):
    # path-prefix early-return for non-validated Issues/ subdirectories.
    # Returns BEFORE any other validation logic — evidence/ and updates/
    # files carry no doctype constraint.
    path_str = str(path)
    if ("/Issues/" in path_str or path_str.startswith("Issues/")) and (
        "/evidence/" in path_str or "/updates/" in path_str
    ):
        return []  # ADR-0051 §Decision §4: evidence/ and updates/ excluded

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
    elif category == "issue":             # v2 per ADR-0050; body in T2.3
        findings.extend(validate_issue_artifact(fm, path))
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
    # Per ADR-0051 §Decision §4 + spec §2.3 + ISSUE_NON_VALIDATED_PATH_PREFIXES:
    # Issues/<topic>/evidence/ and Issues/<topic>/updates/ files are non-validated.
    # The early-return MUST sit here (not in validate_pipeline_artifact) so that
    # files in these subdirs that legitimately have no YAML frontmatter (plain
    # markdown evidence files) do not trip the "no YAML frontmatter found" guard.
    # Discovered as a placement defect during T2.3 quality review; relocated from
    # validate_pipeline_artifact (where T2.2 originally placed it) to here.
    path_str = str(path)
    if ("/Issues/" in path_str or path_str.startswith("Issues/")) and (
        "/evidence/" in path_str or "/updates/" in path_str
    ):
        return []

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
