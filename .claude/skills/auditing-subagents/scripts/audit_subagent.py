#!/usr/bin/env python3
"""
audit_subagent.py — Orchestrator for subagent audit.

Dispatches based on target type:
  - Subagent definition file (.md under agents/) → frontmatter + body + safety scan
  - Subagent memory directory (agent-memory or agent-memory-local) → memory checks + secrets scan

Aggregates JSON output for the coordinator and report writer.

Usage:
    python3 audit_subagent.py <path>
"""
import json
import os
import subprocess
import sys
from pathlib import Path


def run_script(name: str, args: list[str], env_extra: dict | None = None) -> dict:
    here = Path(__file__).resolve().parent
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    try:
        r = subprocess.run(
            [sys.executable, str(here / name)] + args,
            capture_output=True, text=True, timeout=30, env=env,
        )
        if r.returncode != 0 and not r.stdout:
            return {"error": r.stderr.strip(), "findings": []}
        return json.loads(r.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        return {"error": str(e), "findings": []}


def classify(target: Path) -> str:
    target_str = str(target).replace("\\", "/")
    parts = target.parts
    if "agent-memory-local" in parts:
        return "memory-local"
    if "agent-memory" in parts:
        return "memory"
    # Subagent definition: under .claude/agents/ or ~/.claude/agents/
    if target.suffix == ".md":
        for i, p in enumerate(parts):
            if p == "agents" and i > 0 and parts[i - 1] in (".claude", "claude"):
                return "subagent-definition"
    return "unknown"


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: audit_subagent.py <path>"}))
        return 2

    target = Path(sys.argv[1]).resolve()
    if not target.exists():
        print(json.dumps({"error": f"path does not exist: {target}"}))
        return 2

    kind = classify(target)
    report: dict = {"target": str(target), "target_kind": kind, "findings": []}

    if kind == "subagent-definition":
        fm = run_script("validate_subagent_frontmatter.py", [str(target)],
                        env_extra={"AUDIT_TARGET_TYPE": "subagent"})
        report["frontmatter"] = fm
        report["findings"].extend(fm.get("findings", []))

        analyze = run_script("analyze_subagent.py", [str(target)])
        report["analysis"] = analyze
        report["findings"].extend(analyze.get("findings", []))

        scan = run_script("scan_subagent_body.py", [str(target)])
        report["body_scan"] = scan
        report["findings"].extend(scan.get("findings", []))

        # Apply pedagogical marker prefilter on body scan findings
        body_findings = scan.get("findings", [])
        if body_findings:
            skill_dir = target.parent.parent.parent  # walk up to skill root if applicable
            marker_input = json.dumps({"target": str(target), "findings": body_findings})
            r = run_script("pedagogical_marker_check.py",
                           [str(target.parent), "-"])
            # The marker check expects a different invocation — pipe stdin
            # Use subprocess directly
            here = Path(__file__).resolve().parent
            mp = subprocess.run(
                [sys.executable, str(here / "pedagogical_marker_check.py"),
                 str(target.parent), "-"],
                input=marker_input, capture_output=True, text=True, timeout=30,
            )
            if mp.returncode == 0 and mp.stdout:
                try:
                    mp_result = json.loads(mp.stdout)
                    report["body_scan"]["marker_summary"] = mp_result.get("marker_summary", {})
                    report["body_scan"]["marker_adjusted"] = mp_result.get("findings", body_findings)
                except json.JSONDecodeError:
                    pass

    elif kind in ("memory", "memory-local"):
        scope_arg = "local" if kind == "memory-local" else "project"
        # Heuristic: if target is in user home, scope is "user"
        if str(target).startswith(str(Path.home())):
            scope_arg = "user"

        mem = run_script("check_subagent_memory.py", [str(target), "--scope", scope_arg])
        report["memory_check"] = mem
        report["findings"].extend(mem.get("findings", []))

        secrets = run_script("scan_memory_secrets.py", [str(target)])
        report["secrets"] = secrets
        report["findings"].extend(secrets.get("findings", []))

    else:
        report["error"] = f"Unclassified target: {target} (kind={kind})"

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
