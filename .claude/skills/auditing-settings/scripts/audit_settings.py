#!/usr/bin/env python3
"""
audit_settings.py — Orchestrator for settings audit.

Dispatches based on target type:
  - settings.json / settings.local.json / managed-settings.json → schema + permissions + secrets
  - output-styles/*.md → output-style validator

Usage:
    python3 audit_settings.py <path> [--managed]
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
    if name in ("settings.json", "settings.local.json", "managed-settings.json"):
        return "settings"
    # Output style: under output-styles/
    if target.is_file() and target.suffix == ".md":
        for p in parts:
            if p == "output-styles":
                return "output-style"
    return "unknown"


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(json.dumps({"error": "Usage: audit_settings.py <path> [--managed]"}))
        return 2

    target = Path(args[0]).resolve()
    managed_mode = "--managed" in args
    if not target.exists():
        print(json.dumps({"error": f"path does not exist: {target}"}))
        return 2

    kind = classify(target)
    report: dict = {"target": str(target), "target_kind": kind, "managed_mode": managed_mode, "findings": []}

    if kind == "settings":
        schema = run_script("validate_settings_schema.py", [str(target)])
        report["schema"] = schema
        report["findings"].extend(schema.get("findings", []))

        perm_args = [str(target)]
        if managed_mode or target.name == "managed-settings.json":
            perm_args.append("--managed")
        perms = run_script("validate_permissions.py", perm_args)
        report["permissions"] = perms
        report["findings"].extend(perms.get("findings", []))

        secrets = {"findings": []}  # Stub elided per ADR-0067 + ADR-0068.
        report["secrets"] = secrets
        report["findings"].extend(secrets.get("findings", []))

    elif kind == "output-style":
        result = run_script("validate_output_styles.py", [str(target)])
        report["output_style"] = result
        report["findings"].extend(result.get("findings", []))

    else:
        report["error"] = f"Unclassified target: {target}"

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
