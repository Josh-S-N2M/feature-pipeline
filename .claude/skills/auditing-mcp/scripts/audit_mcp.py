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

    # OP-1..OP-10 augmented audit rules (per ADR-0042 family graduation +
    # ADR-0043 hard-gate Gate-6 check). Per the devcontainer-mcp-provisioning-r1
    # Phase 4 T4.3 augmentation, each OP rule is a separate script. The
    # orchestrator dispatches all 10 and aggregates findings.
    #
    # OP-1 / OP-9 / OP-10 take <.mcp.json> path directly (they parse the file).
    # OP-2..OP-8 take <repo-root> (they walk the repo structure: agents,
    # devcontainer scripts, runtime logs, etc.).
    repo_root = target.parent if target.is_file() and target.name == ".mcp.json" else target
    op_rules = [
        ("audit_op1_env_block_coverage.py", [str(target)]),
        ("audit_op2_consumer_mapping.py", [str(repo_root)]),
        ("audit_op3_zero_mcp_invariant.py", [str(repo_root)]),
        ("audit_op4_primary_fallback_prose.py", [str(repo_root)]),
        ("audit_op5_lifecycle_completeness.py", [str(repo_root)]),
        ("audit_op6_runtime_log_redaction.py", [str(repo_root)]),
        ("audit_op7_events_schema.py", [str(repo_root)]),
        ("audit_op8_gitnexus.py", [str(repo_root)]),
        ("audit_op9_url_credential_rejection.py", [str(repo_root)]),
        ("audit_op10_argv_leakage.py", [str(repo_root)]),
    ]
    op_results: dict = {}
    for script_name, args in op_rules:
        result = run_script(script_name, args)
        op_results[script_name] = result
        report["findings"].extend(result.get("findings", []))
    report["op_rules"] = op_results

    print(json.dumps(report, indent=2))

    # ADR-0043 hard-gate semantics: exit 1 if any BLOCKER finding (this is the
    # signal the orchestrator's Gate-6 phase-validator reads to halt or proceed).
    if any(f.get("severity") == "BLOCKER" for f in report["findings"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
