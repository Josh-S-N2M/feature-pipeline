#!/usr/bin/env python3
"""
audit_hooks.py — Orchestrator for hook audit.

Dispatches based on target type:
  - JSON file with hooks block (settings.json, .claude/hooks.json) → validate config
  - Hook script under .claude/hooks/ → analyze script

Aggregates JSON output for the coordinator.

Usage:
    python3 audit_hooks.py <path>
"""
import json
import os
import subprocess
import sys
from pathlib import Path


def run_script(name: str, args: list[str]) -> dict:
    here = Path(__file__).resolve().parent
    try:
        r = subprocess.run(
            [sys.executable, str(here / name)] + args,
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode != 0 and not r.stdout:
            return {"error": r.stderr.strip(), "findings": []}
        return json.loads(r.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        return {"error": str(e), "findings": []}


def classify(target: Path) -> str:
    name = target.name
    parts = target.parts

    if name in ("settings.json", "settings.local.json", "managed-settings.json", "hooks.json"):
        return "hooks-config"

    # Hook script under .claude/hooks/ or ~/.claude/hooks/
    if target.is_file():
        for i, p in enumerate(parts):
            if p == "hooks" and i > 0 and parts[i - 1] in (".claude", "claude"):
                return "hook-script"

    return "unknown"


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: audit_hooks.py <path>"}))
        return 2

    target = Path(sys.argv[1]).resolve()
    if not target.exists():
        print(json.dumps({"error": f"path does not exist: {target}"}))
        return 2

    kind = classify(target)
    report: dict = {"target": str(target), "target_kind": kind, "findings": []}

    if kind == "hooks-config":
        result = run_script("validate_hooks_config.py", [str(target)])
        report["config_check"] = result
        report["findings"].extend(result.get("findings", []))
    elif kind == "hook-script":
        result = run_script("analyze_hook_script.py", [str(target)])
        report["script_analysis"] = result
        report["findings"].extend(result.get("findings", []))
    else:
        report["error"] = f"Unclassified target: {target}"

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
