#!/usr/bin/env python3
"""
audit_mcp.py — Orchestrator for MCP audit.

Usage:
    python3 audit_mcp.py <path-to-settings.json | .mcp.json> [--with-runtime]
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
            capture_output=True, text=True, timeout=60,
        )
        if r.returncode != 0 and not r.stdout:
            return {"error": r.stderr.strip(), "findings": []}
        return json.loads(r.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        return {"error": str(e), "findings": []}


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(json.dumps({"error": "Usage: audit_mcp.py <path> [--with-runtime]"}))
        return 2

    target = Path(args[0]).resolve()
    runtime_mode = "--with-runtime" in args

    if not target.exists():
        print(json.dumps({"error": f"path does not exist: {target}"}))
        return 2

    report: dict = {"target": str(target), "runtime_mode": runtime_mode, "findings": []}

    # Schema/config validation
    config = run_script("validate_mcp_config.py", [str(target)])
    report["config_check"] = config
    report["findings"].extend(config.get("findings", []))

    # Credential scan
    secrets = run_script("scan_mcp_secrets.py", [str(target)])
    report["secrets"] = secrets
    report["findings"].extend(secrets.get("findings", []))

    # Toxic combinations
    toxic_args = [str(target)]
    if runtime_mode:
        toxic_args.append("--with-runtime")
    toxic = run_script("check_toxic_combinations.py", toxic_args)
    report["toxic_combinations"] = toxic
    report["findings"].extend(toxic.get("findings", []))

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
