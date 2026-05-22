#!/usr/bin/env python3
"""
validate_settings_schema.py — Validate top-level settings.json schema.

Detects:
  - ST-5: scope-mismatched field
  - ST-6: unrecognized field
  - JSON parse errors

Usage:
    python3 validate_settings_schema.py <path-to-settings.json> [--scope managed|local|project|user]
"""
import json
import re
import sys
from pathlib import Path

# Known top-level fields and their scope restrictions
# Scope: 'any', 'managed', 'user' — or a set
KNOWN_FIELDS = {
    "model": "any",
    "permissions": "any",
    "env": "any",
    "hooks": "any",
    "outputStyles": "any",
    "subagents": "any",
    "maxOutputTokens": "any",
    "verbose": "any",
    "alwaysThinkingEnabled": "any",
    "spinnerTipsEnabled": "any",
    "mcpServers": "any",
    "autoMemoryDirectory": "user",
    "disableBypassPermissionsMode": "managed",
    "disableAllPlugins": "managed",
    "disableMcpServers": "managed",
    "disableExternalConnectors": "managed",
    "disableTelemetry": "managed",
    "claudeMd": "managed",
    # Additional known fields per code.claude.com docs
    "permissionMode": "any",
    "disableSpinnerTips": "any",
    "promptCaching": "any",
}


def infer_scope(path: Path) -> str:
    s = str(path).replace("\\", "/")
    if "managed-settings" in path.name:
        return "managed"
    if "settings.local" in path.name:
        return "local"
    if "/.claude/" in s and path.name == "settings.json":
        return "project"
    if s.startswith(str(Path.home())) and path.name == "settings.json":
        return "user"
    return "unknown"


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(json.dumps({"error": "Usage: validate_settings_schema.py <path> [--scope SCOPE]"}))
        return 2

    path = Path(args[0]).resolve()
    scope = "unknown"
    if "--scope" in args:
        idx = args.index("--scope")
        if idx + 1 < len(args):
            scope = args[idx + 1]
    if scope == "unknown":
        scope = infer_scope(path)

    if not path.is_file():
        print(json.dumps({"error": f"not a file: {path}"}))
        return 2

    findings: list[dict] = []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        findings.append({
            "dimension": 1, "severity": "BLOCKER",
            "what": f"JSON parse error: {e}",
            "fix": "Fix JSON syntax.",
            "location": str(path), "where": str(path),
        })
        print(json.dumps({"target": str(path), "scope": scope, "findings": findings}))
        return 0

    if not isinstance(data, dict):
        findings.append({
            "dimension": 1, "severity": "BLOCKER",
            "what": "Top-level value is not a JSON object.",
            "fix": "settings.json must be a JSON object.",
            "location": str(path), "where": str(path),
        })
        print(json.dumps({"target": str(path), "scope": scope, "findings": findings}))
        return 0

    # Check each field
    for field, value in data.items():
        if field not in KNOWN_FIELDS:
            findings.append({
                "dimension": 1, "severity": "MINOR",
                "what": f"Unrecognized field '{field}'. (ST-6) Will be silently ignored.",
                "fix": "Check spelling, or remove the field. Schema: " + ", ".join(sorted(KNOWN_FIELDS)),
                "location": str(path), "where": str(path),
            })
            continue

        required_scope = KNOWN_FIELDS[field]
        if required_scope == "any":
            continue

        # Scope check
        if scope != "unknown" and scope != required_scope:
            findings.append({
                "dimension": 2, "severity": "MAJOR",
                "what": f"Field '{field}' only takes effect at {required_scope} scope; current scope is {scope}. Silently ignored. (ST-5)",
                "fix": f"Move to {required_scope} scope, or remove.",
                "location": str(path), "where": str(path),
            })

    print(json.dumps({
        "target": str(path),
        "scope": scope,
        "top_level_fields": list(data.keys()),
        "findings": findings,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
