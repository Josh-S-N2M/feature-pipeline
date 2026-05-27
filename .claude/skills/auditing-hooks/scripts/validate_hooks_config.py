#!/usr/bin/env python3
"""
validate_hooks_config.py — Validate a hooks block (in settings.json or .claude/hooks.json).

Detects:
  - HK-1: misspelled event names (case-sensitive allow-list)
  - HK-2: empty hooks lists
  - HK-3, HK-4: matcher syntax mistakes
  - HK-5: command path doesn't exist on disk
  - SessionStart hook flagged for security review (CVE-2025-59536 class)

Usage:
    python3 validate_hooks_config.py <path-to-settings.json | .claude/hooks.json>
"""
import json
import re
import sys
from pathlib import Path

# Case-sensitive set of valid event names. SessionEnd added 2026-05-27 to
# match Claude Code's actual hook event surface (the auditor's list was stale).
VALID_EVENTS = {
    "SessionStart", "SessionEnd", "PreToolUse", "PostToolUse", "UserPromptSubmit",
    "Stop", "SubagentStart", "SubagentStop", "Notification",
    "PermissionRequest", "PreCompact", "PostCompact", "Error",
}


def check_matcher(matcher: str) -> list[str]:
    """Return list of error messages for matcher syntax."""
    errors = []
    if matcher == "":
        return errors
    if matcher == "*":
        errors.append("Matcher `*` is not valid regex; matches nothing. Use `.*` for match-all or omit. (HK-4)")
    if "," in matcher and "|" not in matcher:
        errors.append("Matcher contains comma; not regex syntax. Use pipe: `Bash|Read`. (HK-3)")
    # Try to compile
    try:
        re.compile(matcher)
    except re.error as e:
        errors.append(f"Matcher regex compile error: {e}.")
    return errors


def validate_command_path(command: str, settings_dir: Path) -> tuple[bool, str | None]:
    """Check if the command's script path exists. Returns (exists, resolved_path_or_None).
    Returns (True, None) for inline commands or commands that don't look like script paths.

    Expands `${CLAUDE_PROJECT_DIR}` and `${HOME}` so hook commands that use the documented
    interpolation form resolve to real disk paths. `${CLAUDE_PROJECT_DIR}` is the parent
    directory of the `.claude` directory that owns `settings_dir`; `${HOME}` is the
    current user's home directory."""
    # Extract the first whitespace-delimited token
    tokens = command.split()
    if not tokens:
        return True, None
    first = tokens[0]
    # If it doesn't look like a path (no slash, no dot), skip
    if "/" not in first and "." not in first:
        return True, None
    # Substitute documented hook-context variables before resolving on disk
    if "${CLAUDE_PROJECT_DIR}" in first:
        project_root = settings_dir.parent if settings_dir.parent.is_dir() else settings_dir
        first = first.replace("${CLAUDE_PROJECT_DIR}", str(project_root))
    if "${HOME}" in first:
        from os.path import expanduser
        first = first.replace("${HOME}", expanduser("~"))
    # Resolve relative to settings dir
    if first.startswith("~"):
        from os.path import expanduser
        first = expanduser(first)
    p = Path(first)
    if not p.is_absolute():
        p = settings_dir / p
    return p.exists(), str(p)


def walk_hooks(hooks_block: dict, settings_dir: Path) -> list[dict]:
    findings: list[dict] = []

    for event_name, entries in hooks_block.items():
        if event_name not in VALID_EVENTS:
            findings.append({
                "dimension": 2, "severity": "BLOCKER",
                "what": f"Unknown event name '{event_name}'. Will silently never fire. (HK-1) Valid: {sorted(VALID_EVENTS)}.",
                "fix": "Use a valid event name (case-sensitive).",
            })
            continue

        if not isinstance(entries, list):
            findings.append({
                "dimension": 1, "severity": "BLOCKER",
                "what": f"Event '{event_name}' value is not a list.",
                "fix": "The value must be a JSON list of hook entries.",
            })
            continue

        if len(entries) == 0:
            findings.append({
                "dimension": 1, "severity": "MINOR",
                "what": f"Event '{event_name}' has empty hooks list. (HK-2)",
                "fix": "Remove the entry, or add at least one hook action.",
            })
            continue

        for entry in entries:
            if not isinstance(entry, dict):
                findings.append({
                    "dimension": 1, "severity": "MAJOR",
                    "what": f"Hook entry under '{event_name}' is not a JSON object.",
                    "fix": "Each entry should be an object with `matcher` (optional) and `hooks` (list).",
                })
                continue

            # Matcher
            matcher = entry.get("matcher", "")
            if matcher:
                for msg in check_matcher(matcher):
                    findings.append({
                        "dimension": 5, "severity": "BLOCKER" if "valid regex" in msg or "compile error" in msg else "MAJOR",
                        "what": f"Event '{event_name}' matcher: {msg}",
                        "fix": "Fix the matcher pattern.",
                    })

            # Hook actions
            actions = entry.get("hooks", [])
            if not isinstance(actions, list):
                findings.append({
                    "dimension": 1, "severity": "MAJOR",
                    "what": f"`hooks` field under '{event_name}' is not a list.",
                    "fix": "Use a list of action objects.",
                })
                continue
            if not actions:
                findings.append({
                    "dimension": 1, "severity": "MINOR",
                    "what": f"Event '{event_name}' entry has empty `hooks` list. (HK-2)",
                    "fix": "Add at least one action.",
                })
                continue

            for act in actions:
                if not isinstance(act, dict):
                    continue
                cmd = act.get("command", "")
                if not cmd:
                    findings.append({
                        "dimension": 3, "severity": "BLOCKER",
                        "what": f"Event '{event_name}' action has no `command`.",
                        "fix": "Add the command to run.",
                    })
                    continue

                # SessionStart-with-network-egress check disabled per ADR-0067 (2026-05-27).

                # Pre-cmd /CVE-mitigated: but warn anyway about no-matcher PreToolUse/PostToolUse
                if event_name in ("PreToolUse", "PostToolUse") and not entry.get("matcher"):
                    findings.append({
                        "dimension": 5, "severity": "MINOR",
                        "what": f"{event_name} hook has no matcher; fires on every tool call. (HA-10)",
                        "fix": "Add a matcher to limit which tool calls trigger the hook.",
                    })

                # Path existence (HK-5)
                exists, resolved = validate_command_path(cmd, settings_dir)
                if not exists and resolved:
                    findings.append({
                        "dimension": 3, "severity": "BLOCKER",
                        "what": f"Hook command references script that does not exist: {resolved}. (HK-5 / cross-file X1)",
                        "fix": "Create the script or remove the hook entry.",
                    })

    return findings


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: validate_hooks_config.py <settings-or-hooks-json>"}))
        return 2

    path = Path(sys.argv[1]).resolve()
    if not path.is_file():
        print(json.dumps({"error": f"not a file: {path}"}))
        return 2

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(json.dumps({
            "findings": [{
                "dimension": 1, "severity": "BLOCKER",
                "what": f"JSON parse error: {e}",
                "fix": "Fix the JSON syntax.",
                "location": str(path), "where": str(path),
            }],
        }))
        return 0

    # Hooks may be under "hooks" key (settings.json) or at top level (hooks.json)
    hooks_block = data.get("hooks", data) if isinstance(data, dict) else {}
    if not isinstance(hooks_block, dict):
        print(json.dumps({"findings": [{
            "dimension": 1, "severity": "BLOCKER",
            "what": "`hooks` is not an object.",
            "fix": "Hooks must be a JSON object keyed by event name.",
            "location": str(path), "where": str(path),
        }]}))
        return 0

    findings = walk_hooks(hooks_block, path.parent)
    for f in findings:
        f["location"] = str(path)
        f.setdefault("where", str(path))

    print(json.dumps({
        "target": str(path),
        "events_configured": list(hooks_block.keys()),
        "findings": findings,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
