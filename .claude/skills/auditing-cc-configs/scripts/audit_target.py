#!/usr/bin/env python3
"""
audit_target.py — Single-target dispatcher.

Examines a path and routes it to the appropriate sub-skill's auditor.
Memory-aware: distinguishes auto memory, subagent memory, and CLAUDE.md/rules
based on path patterns. Returns JSON describing the dispatch decision and,
when a sub-skill is available, the audit results.

This script is invoked by the coordinator and by `audit_project.py` (Phase 8).
For now it knows about:

  - SKILL.md / skill directory     → auditing-skills
  - .claude/commands/<name>.md     → auditing-skills (slash command variant)
  - CLAUDE.md, CLAUDE.local.md     → auditing-context-files
  - .claude/CLAUDE.md              → auditing-context-files
  - .claude/rules/*.md             → auditing-context-files
  - ~/.claude/projects/<id>/memory → auditing-context-files (auto memory)
  - .claude/agents/<name>.md       → auditing-subagents
  - .claude/agent-memory/...       → auditing-subagents (subagent memory)
  - .claude/agent-memory-local/... → auditing-subagents (subagent memory, gitignored)
  - settings.json variants         → auditing-settings
  - managed-settings.json          → auditing-settings (managed mode)
  - .claude/output-styles/*.md     → auditing-settings
  - hooks.json / hooks block       → auditing-hooks
  - .claude/hooks/*.sh             → auditing-hooks
  - .mcp.json, ~/.claude.json      → auditing-mcp

If a sub-skill is not yet installed in the same skills directory, returns
a "dispatch-only" result that the coordinator surfaces as a skipped component.

Usage:
    python3 audit_target.py <path>
"""
import json
import os
import sys
from pathlib import Path
from typing import Any


def find_sibling_skill(skill_name: str) -> Path | None:
    """Locate a sibling sub-skill by name. Searches up from this script's
    directory, then in standard skill installation locations.
    """
    here = Path(__file__).resolve().parent.parent  # coordinator dir
    # Sibling in same skills root
    candidate = here.parent / skill_name
    if (candidate / "SKILL.md").exists():
        return candidate
    # User-scope install
    user_skills = Path.home() / ".claude" / "skills" / skill_name
    if (user_skills / "SKILL.md").exists():
        return user_skills
    # Project-scope install (.claude/skills/<name>/)
    cwd_skill = Path.cwd() / ".claude" / "skills" / skill_name
    if (cwd_skill / "SKILL.md").exists():
        return cwd_skill
    return None


def classify_path(target: Path) -> dict[str, Any]:
    """Determine target type and which sub-skill should audit it.

    Returns a dict with keys: target_type, sub_skill, route_reason.
    """
    target = target.resolve()
    parts = target.parts

    # Directory containing SKILL.md → skill
    if target.is_dir() and (target / "SKILL.md").exists():
        return {
            "target_type": "skill",
            "sub_skill": "auditing-skills",
            "route_reason": "Directory contains SKILL.md",
        }

    name = target.name
    name_lower = name.lower()

    # File: SKILL.md
    if name == "SKILL.md" and target.is_file():
        return {
            "target_type": "skill",
            "sub_skill": "auditing-skills",
            "route_reason": "File is SKILL.md",
        }

    # CLAUDE.md / CLAUDE.local.md / .claude/CLAUDE.md
    if name in ("CLAUDE.md", "CLAUDE.local.md"):
        return {
            "target_type": "claude-md",
            "sub_skill": "auditing-context-files",
            "route_reason": "CLAUDE.md or CLAUDE.local.md",
        }

    # Auto memory: ~/.claude/projects/<id>/memory/MEMORY.md (or any file under that dir)
    target_str = str(target)
    if (".claude/projects/" in target_str.replace("\\", "/") and
            "/memory/" in target_str.replace("\\", "/")):
        return {
            "target_type": "auto-memory",
            "sub_skill": "auditing-context-files",
            "route_reason": "Path under ~/.claude/projects/<id>/memory/ — auto memory",
        }

    # Subagent memory: agent-memory or agent-memory-local
    if "agent-memory-local" in parts:
        return {
            "target_type": "subagent-memory-local",
            "sub_skill": "auditing-subagents",
            "route_reason": "Path under .claude/agent-memory-local/ — local subagent memory",
        }
    if "agent-memory" in parts:
        return {
            "target_type": "subagent-memory",
            "sub_skill": "auditing-subagents",
            "route_reason": "Path under .claude/agent-memory/ or ~/.claude/agent-memory/ — subagent memory",
        }

    # Subagent definition: .claude/agents/<name>.md or ~/.claude/agents/<name>.md
    if "agents" in parts and target.suffix == ".md":
        # Be a bit careful — must be in a .claude/agents/ directory
        for i, p in enumerate(parts):
            if p == "agents" and i > 0 and parts[i - 1] in (".claude", "claude"):
                return {
                    "target_type": "subagent",
                    "sub_skill": "auditing-subagents",
                    "route_reason": ".claude/agents/<name>.md",
                }

    # Slash command: .claude/commands/<name>.md
    if "commands" in parts and target.suffix == ".md":
        for i, p in enumerate(parts):
            if p == "commands" and i > 0 and parts[i - 1] in (".claude", "claude"):
                return {
                    "target_type": "slash-command",
                    "sub_skill": "auditing-skills",
                    "route_reason": ".claude/commands/<name>.md — slash command variant",
                }

    # Rules: .claude/rules/<anything>.md
    if "rules" in parts and target.suffix == ".md":
        for i, p in enumerate(parts):
            if p == "rules" and i > 0 and parts[i - 1] in (".claude", "claude"):
                return {
                    "target_type": "rules-file",
                    "sub_skill": "auditing-context-files",
                    "route_reason": ".claude/rules/<name>.md",
                }

    # Output styles: .claude/output-styles/<name>.md
    if "output-styles" in parts and target.suffix == ".md":
        return {
            "target_type": "output-style",
            "sub_skill": "auditing-settings",
            "route_reason": ".claude/output-styles/<name>.md",
        }

    # Settings files
    if name == "settings.json":
        # Could be project or user scope based on path
        return {
            "target_type": "settings",
            "sub_skill": "auditing-settings",
            "route_reason": "settings.json",
        }
    if name == "settings.local.json":
        return {
            "target_type": "settings-local",
            "sub_skill": "auditing-settings",
            "route_reason": "settings.local.json (local scope)",
        }
    if name == "managed-settings.json":
        return {
            "target_type": "managed-settings",
            "sub_skill": "auditing-settings",
            "route_reason": "managed-settings.json",
        }

    # Hooks
    if name == "hooks.json":
        return {
            "target_type": "hooks-config",
            "sub_skill": "auditing-hooks",
            "route_reason": "hooks.json",
        }
    if "hooks" in parts and target.is_file():
        # Hook script under .claude/hooks/
        for i, p in enumerate(parts):
            if p == "hooks" and i > 0 and parts[i - 1] in (".claude", "claude"):
                return {
                    "target_type": "hook-script",
                    "sub_skill": "auditing-hooks",
                    "route_reason": ".claude/hooks/<script>",
                }

    # MCP
    if name == ".mcp.json":
        return {
            "target_type": "mcp-project",
            "sub_skill": "auditing-mcp",
            "route_reason": ".mcp.json (project scope)",
        }
    if name == ".claude.json":
        return {
            "target_type": "mcp-user",
            "sub_skill": "auditing-mcp",
            "route_reason": "~/.claude.json (user scope MCP)",
        }

    # Fallback
    return {
        "target_type": "unknown",
        "sub_skill": None,
        "route_reason": f"Could not classify path: {target}",
    }


def dispatch(target: Path) -> dict[str, Any]:
    """Dispatch the target to its sub-skill. Returns the audit result, or
    a stub if the sub-skill is unavailable."""
    classification = classify_path(target)

    result = {
        "target": str(target),
        "classification": classification,
    }

    sub_skill = classification.get("sub_skill")
    if sub_skill is None:
        result["status"] = "unclassified"
        result["audit"] = None
        return result

    sub_skill_path = find_sibling_skill(sub_skill)
    if sub_skill_path is None:
        result["status"] = "sub-skill-not-installed"
        result["audit"] = None
        result["note"] = (
            f"Sub-skill `{sub_skill}` not found in sibling, user-scope, "
            "or project-scope skill directories. Install it to enable auditing "
            f"of this target type ({classification['target_type']})."
        )
        return result

    # Sub-skill exists — for now we record the dispatch decision.
    # Phase 1+ will implement actual sub-skill invocation here. v1.1 of
    # auditing-skills has its own audit_skill.py at scripts/audit_skill.py,
    # so we can shell out to it for skills specifically.
    if sub_skill == "auditing-skills":
        sub_script = sub_skill_path / "scripts" / "audit_skill.py"
        if sub_script.exists():
            # Determine the dir we hand it: for SKILL.md files, pass the parent;
            # for skill dirs, pass the dir
            target_for_sub = target.parent if (target.is_file() and target.name == "SKILL.md") else target
            result["status"] = "dispatched"
            result["audit"] = {
                "subskill_script": str(sub_script),
                "argument": str(target_for_sub),
                "note": "Coordinator will invoke this script and integrate results.",
            }
            return result

    # Other sub-skills not yet built
    result["status"] = "sub-skill-not-yet-built"
    result["audit"] = None
    result["note"] = (
        f"Sub-skill `{sub_skill}` is installed but its audit script is not "
        "yet implemented in this v2 build. Phase 2+ will add it."
    )
    return result


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: audit_target.py <path>", file=sys.stderr)
        return 2

    target = Path(sys.argv[1]).resolve()
    if not target.exists():
        print(json.dumps({
            "error": f"Path does not exist: {target}",
        }, indent=2))
        return 1

    result = dispatch(target)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
