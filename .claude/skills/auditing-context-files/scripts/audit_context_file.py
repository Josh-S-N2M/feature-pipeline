#!/usr/bin/env python3
"""
audit_context_file.py — Single-target dispatcher for context files.

Determines the file type (CLAUDE.md, rules file, auto memory) and runs
the appropriate deterministic checks. Returns aggregated JSON.

Usage:
    python3 audit_context_file.py <path>
"""
import json
import subprocess
import sys
from pathlib import Path


def classify(target: Path) -> str:
    """Return one of: claude-md, rules-file, auto-memory-dir, auto-memory-file, unknown."""
    name = target.name
    if name in ("CLAUDE.md", "CLAUDE.local.md"):
        return "claude-md"
    if target.is_dir() and "memory" in target.parts and ".claude/projects" in str(target).replace("\\", "/"):
        return "auto-memory-dir"
    if target.is_file() and "/memory/" in str(target).replace("\\", "/"):
        return "auto-memory-file"
    # Rules file: under .claude/rules/
    parts = target.parts
    for i, p in enumerate(parts):
        if p == "rules" and i > 0 and parts[i - 1] in (".claude", "claude"):
            return "rules-file"
    return "unknown"


def run_script(script_name: str, args: list[str]) -> dict:
    here = Path(__file__).resolve().parent
    try:
        r = subprocess.run(
            [sys.executable, str(here / script_name)] + args,
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode != 0 and not r.stdout:
            return {"error": r.stderr.strip(), "findings": []}
        return json.loads(r.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        return {"error": str(e), "findings": []}


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: audit_context_file.py <path>"}))
        return 2

    target = Path(sys.argv[1]).resolve()
    if not target.exists():
        print(json.dumps({"error": f"path does not exist: {target}"}))
        return 2

    kind = classify(target)
    report = {"target": str(target), "target_kind": kind, "findings": []}

    if kind == "claude-md":
        analyze = run_script("analyze_claude_md.py", [str(target)])
        report["analyze"] = analyze
        report["findings"].extend(analyze.get("findings", []))
        imports = run_script("validate_at_imports.py", [str(target)])
        report["imports"] = imports
        report["findings"].extend(imports.get("findings", []))
        secrets = run_script("scan_memory_secrets.py", [str(target)])
        report["secrets"] = secrets
        report["findings"].extend(secrets.get("findings", []))
    elif kind == "rules-file":
        gv = run_script("glob_validator.py", [str(target)])
        report["glob_validator"] = gv
        report["findings"].extend(gv.get("findings", []))
        analyze = run_script("analyze_claude_md.py", [str(target)])
        report["analyze"] = analyze
        report["findings"].extend(analyze.get("findings", []))
    elif kind in ("auto-memory-dir", "auto-memory-file"):
        if kind == "auto-memory-file":
            target_dir = target.parent
        else:
            target_dir = target
        am = run_script("check_auto_memory.py", [str(target_dir)])
        report["check_auto_memory"] = am
        report["findings"].extend(am.get("findings", []))
        secrets = run_script("scan_memory_secrets.py", [str(target_dir)])
        report["secrets"] = secrets
        report["findings"].extend(secrets.get("findings", []))
    else:
        report["error"] = f"Unknown target kind for {target}"

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
