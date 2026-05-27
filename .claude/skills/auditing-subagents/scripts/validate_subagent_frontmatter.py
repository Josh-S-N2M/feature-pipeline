#!/usr/bin/env python3
"""
validate_subagent_frontmatter.py — Validate subagent YAML frontmatter.

Subagent schema differs from skills:
  - tools (NOT allowed-tools) — comma-separated or YAML list
  - model — alias or full ID, falls back silently to 'inherit'
  - memory — project | local | user
  - permissionMode — default | acceptEdits | bypassPermissions | plan
  - skills — list of skill names
  - disallowedTools — tools the subagent must NOT have
  - name, description — required

Detects:
  - allowed-tools used instead of tools (SA-1)
  - Unrecognized model alias (SA-6)
  - Vague description (SA-2 hint; full check in analyze_subagent.py)
  - Invalid memory scope
  - Invalid permissionMode
  - Unrecognized fields (warn)

Usage:
    python3 validate_subagent_frontmatter.py <path-to-subagent.md>
"""
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print(json.dumps({"error": "PyYAML not installed", "findings": []}))
    sys.exit(0)


RECOGNIZED_FIELDS = {
    "name", "description", "tools", "model", "memory",
    "permissionMode", "skills", "disallowedTools", "effort",
    "pedagogical_sections",  # audit-family marker
}

VALID_MODEL_ALIASES = {"sonnet", "opus", "haiku", "inherit"}
# Full IDs also accepted — pattern match
FULL_MODEL_ID_RE = re.compile(r"^claude-[\w\-]+\d$")

VALID_MEMORY_SCOPES = {"project", "local", "user"}
VALID_PERMISSION_MODES = {"default", "acceptEdits", "bypassPermissions", "plan"}

NAME_PATTERN = re.compile(r"^[a-z0-9-]+$")


def split_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith("---"):
        return None, text
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return None, text
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:])
    return None, text


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: validate_subagent_frontmatter.py <path>"}))
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(json.dumps({"error": f"not a file: {path}"}))
        return 2

    text = path.read_text(encoding="utf-8", errors="replace")
    findings: list[dict] = []

    if text.startswith("\ufeff"):
        findings.append({
            "dimension": 1, "severity": "BLOCKER",
            "what": "File starts with UTF-8 BOM. Frontmatter `---` must be the very first bytes.",
            "fix": "Re-save as UTF-8 without BOM.",
        })
        text = text.lstrip("\ufeff")

    fm_text, body = split_frontmatter(text)
    if fm_text is None:
        findings.append({
            "dimension": 1, "severity": "BLOCKER",
            "what": "Frontmatter missing or unclosed; subagent will be silently dropped.",
            "fix": "Ensure file starts with `---`, has YAML, and closes with `---`.",
        })
        print(json.dumps({"findings": findings, "frontmatter": None, "body": body}))
        return 0

    if "\t" in fm_text:
        findings.append({
            "dimension": 1, "severity": "BLOCKER",
            "what": "Tab characters in frontmatter; YAML requires spaces only.",
            "fix": "Replace tabs with spaces.",
        })

    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError as e:
        findings.append({
            "dimension": 1, "severity": "BLOCKER",
            "what": f"Frontmatter YAML parse error: {e}",
            "fix": "Fix the YAML syntax.",
        })
        print(json.dumps({"findings": findings, "frontmatter": None, "body": body}))
        return 0

    if not isinstance(fm, dict):
        findings.append({
            "dimension": 1, "severity": "BLOCKER",
            "what": "Frontmatter is not a mapping.",
            "fix": "Frontmatter must be YAML mapping with fields like `name:` and `description:`.",
        })
        print(json.dumps({"findings": findings, "frontmatter": None, "body": body}))
        return 0

    # SA-1: allowed-tools used (skills field) instead of tools (subagent field)
    if "allowed-tools" in fm and "tools" not in fm:
        findings.append({
            "dimension": 3, "severity": "BLOCKER",
            "what": "Field `allowed-tools:` is used — this is the SKILLS field. Subagents use `tools:`. The current value is silently ignored; the subagent inherits the parent's full tool set. (SA-1)",
            "fix": "Rename `allowed-tools:` to `tools:`.",
        })

    # Name validation
    name = fm.get("name")
    if name is None:
        findings.append({
            "dimension": 1, "severity": "BLOCKER",
            "what": "No `name` field.",
            "fix": "Add `name:` matching the filename (without .md).",
        })
    elif not isinstance(name, str):
        findings.append({
            "dimension": 1, "severity": "BLOCKER",
            "what": "`name` is not a string.",
            "fix": "Use a kebab-case string for `name:`.",
        })
    elif not NAME_PATTERN.match(name):
        findings.append({
            "dimension": 1, "severity": "BLOCKER",
            "what": f"`name` '{name}' contains characters other than a-z 0-9 hyphen.",
            "fix": "Use kebab-case: lowercase letters, digits, hyphens only.",
        })

    # Description
    desc = fm.get("description")
    if desc is None:
        findings.append({
            "dimension": 2, "severity": "MAJOR",
            "what": "No `description` field. Subagent will not get delegated tasks.",
            "fix": "Add a description that explains what task this subagent handles.",
        })
    elif not isinstance(desc, str):
        findings.append({
            "dimension": 2, "severity": "BLOCKER",
            "what": "`description` is not a string.",
            "fix": "Make `description:` a string.",
        })
    else:
        if len(desc) > 1024:
            findings.append({
                "dimension": 2, "severity": "BLOCKER",
                "what": f"Description is {len(desc)} characters (>1024). Will be truncated.",
                "fix": "Shorten to <1024 chars. Move detail to the body.",
            })

    # Model validation
    model = fm.get("model")
    if model is not None:
        if not isinstance(model, str):
            findings.append({
                "dimension": 8, "severity": "BLOCKER",
                "what": "`model` is not a string.",
                "fix": "Use one of: sonnet, opus, haiku, inherit, or a full model ID.",
            })
        elif model not in VALID_MODEL_ALIASES and not FULL_MODEL_ID_RE.match(model):
            findings.append({
                "dimension": 8, "severity": "MAJOR",
                "what": f"`model: {model}` is not a recognized alias or Claude model ID. Will silently fall back to 'inherit'. (SA-6)",
                "fix": "Use one of: sonnet, opus, haiku, inherit, or a full Claude model ID.",
            })

    # Memory validation
    memory = fm.get("memory")
    if memory is not None:
        if not isinstance(memory, str):
            findings.append({
                "dimension": 5, "severity": "BLOCKER",
                "what": "`memory` is not a string.",
                "fix": "Use one of: project, local, user.",
            })
        elif memory not in VALID_MEMORY_SCOPES:
            findings.append({
                "dimension": 5, "severity": "BLOCKER",
                "what": f"`memory: {memory}` is not a valid scope.",
                "fix": "Use one of: project, local, user.",
            })

    # PermissionMode validation
    pmode = fm.get("permissionMode")
    if pmode is not None:
        if pmode not in VALID_PERMISSION_MODES:
            findings.append({
                "dimension": 6, "severity": "MAJOR",
                "what": f"`permissionMode: {pmode}` is not valid.",
                "fix": "Use one of: default, acceptEdits, bypassPermissions, plan.",
            })

    # Tools field validation
    tools = fm.get("tools")
    if tools is not None:
        if isinstance(tools, str):
            tools_list = [t.strip() for t in tools.split(",")]
        elif isinstance(tools, list):
            tools_list = [str(t).strip() for t in tools]
        else:
            tools_list = []
            findings.append({
                "dimension": 3, "severity": "MAJOR",
                "what": f"`tools` is {type(tools).__name__}; should be comma-separated string or YAML list.",
                "fix": "Use 'tools: Read, Grep, Bash(git diff *)' or YAML list syntax.",
            })

        # SA-3 (wildcard-Bash check) disabled per ADR-0067 (2026-05-27).

    # SA-13: skills field references non-existent skills
    # Policy per references/subagent-spec.md: "Each skill must actually exist in a discoverable
    # location → otherwise BLOCKER". Missing skill references are silently skipped by Claude Code's
    # loader, so the subagent claims a capability it doesn't have.
    skills_field = fm.get("skills")
    if skills_field is not None:
        if isinstance(skills_field, str):
            skills_list = [s.strip() for s in skills_field.split(",") if s.strip()]
        elif isinstance(skills_field, list):
            skills_list = [str(s).strip() for s in skills_field if str(s).strip()]
        else:
            skills_list = []
        # Resolve project-scope skill discovery: walk up from the subagent file to find
        # a .claude/ directory, then look for .claude/skills/<name>/SKILL.md.
        project_skills_dir = None
        for parent in path.resolve().parents:
            candidate = parent / ".claude" / "skills"
            if candidate.is_dir():
                project_skills_dir = candidate
                break
            if parent.name == ".claude":
                candidate = parent / "skills"
                if candidate.is_dir():
                    project_skills_dir = candidate
                    break
        for skill_name in skills_list:
            if not skill_name:
                continue
            resolved = False
            if project_skills_dir is not None:
                if (project_skills_dir / skill_name / "SKILL.md").is_file():
                    resolved = True
            if not resolved:
                user_skill = Path.home() / ".claude" / "skills" / skill_name / "SKILL.md"
                if user_skill.is_file():
                    resolved = True
            if not resolved:
                findings.append({
                    "dimension": 9, "severity": "BLOCKER",
                    "what": f"Skills field references skill `{skill_name}` but no SKILL.md found at any discoverable location (project `.claude/skills/{skill_name}/SKILL.md` or user `~/.claude/skills/{skill_name}/SKILL.md`). Claude Code silently skips missing references at load time; the subagent claims a capability it doesn't have. (SA-13)",
                    "fix": f"Either author the skill at .claude/skills/{skill_name}/SKILL.md, remove `{skill_name}` from the `skills:` array, or correct the spelling if it's a typo for an existing skill.",
                })

    # Unrecognized fields
    unrecognized = [k for k in fm if k not in RECOGNIZED_FIELDS]
    if unrecognized:
        findings.append({
            "dimension": 1, "severity": "MINOR",
            "what": f"Unrecognized frontmatter field(s): {unrecognized}. These are silently ignored.",
            "fix": "Remove or rename them. Recognized fields: " + ", ".join(sorted(RECOGNIZED_FIELDS)),
        })

    # Add file path to each finding location
    for f in findings:
        f["location"] = str(path)
        f.setdefault("where", str(path))

    print(json.dumps({"findings": findings, "frontmatter": fm, "body": body}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
