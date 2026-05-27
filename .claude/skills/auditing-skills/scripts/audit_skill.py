#!/usr/bin/env python3
"""
audit_skill.py — Orchestrator for deterministic skill audit checks.

Runs:
  - validate_frontmatter.py
  - lint_references.py
  - scan_security.py

Then aggregates results and emits a JSON summary that the agent can read
when scoring dimensions 2, 4, and 8.

Usage:
    python3 audit_skill.py <path-to-skill-dir>
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def run_check(script_path: Path, target: Path) -> dict:
    """Run one check script and return its parsed JSON output."""
    try:
        result = subprocess.run(
            [sys.executable, str(script_path), str(target)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0 and not result.stdout:
            return {
                "error": f"{script_path.name} exited {result.returncode}",
                "stderr": result.stderr.strip(),
            }
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        return {"error": f"{script_path.name} timed out after 30s"}
    except json.JSONDecodeError as e:
        return {
            "error": f"{script_path.name} produced invalid JSON: {e}",
            "stdout": result.stdout[:500] if 'result' in locals() else "",
        }


def line_count(path: Path) -> int:
    if not path.is_file():
        return 0
    return sum(1 for _ in path.open(encoding="utf-8", errors="replace"))


def find_orphans(skill_dir: Path, frontmatter_result: dict, refs_result: dict) -> list[str]:
    """Find files in the skill dir that aren't referenced from anywhere."""
    referenced = set(refs_result.get("referenced_paths", []))
    referenced.add("SKILL.md")  # always referenced by virtue of being the entry

    # Scripts that are invoked by other Python scripts (subprocess) are referenced indirectly.
    # If audit_skill.py is referenced from SKILL.md, treat all sibling .py files in scripts/
    # as transitively referenced.
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        any_script_referenced = any(r.startswith("scripts/") and r.endswith(".py") for r in referenced)
        if any_script_referenced:
            for f in scripts_dir.glob("*.py"):
                rel = str(f.relative_to(skill_dir))
                referenced.add(rel)

    # Directories whose contents are tooling-internal, not documentation. Files
    # under these paths are implementation details that don't need explicit
    # SKILL.md references. (Adding __pycache__ closes a class of false-positives
    # where the orphan check fires on Python bytecode caches.)
    IMPLICIT_DIRS = ("__pycache__", "test_fixtures", "smoke_fixtures",
                     "fixtures", "_corpus", "_data")
    IMPLICIT_SUFFIXES = (".pyc", ".pyo")

    all_files = []
    for p in skill_dir.rglob("*"):
        if not p.is_file():
            continue
        rel_parts = p.relative_to(skill_dir).parts
        if any(part.startswith(".") for part in rel_parts):
            continue
        if any(d in rel_parts for d in IMPLICIT_DIRS):
            continue
        if p.suffix in IMPLICIT_SUFFIXES:
            continue
        rel = str(p.relative_to(skill_dir))
        all_files.append(rel)

    # If any sibling file in the same directory is referenced, treat the whole
    # directory as expected. Supports fixture/corpus/example/sample directories
    # where the README and one or two main files are referenced explicitly but
    # the supporting data files (JSON, manifests, generated outputs, etc.) are
    # implied by the corpus structure rather than explicitly enumerated.
    referenced_dirs: set[str] = set()
    for r in referenced:
        parent = str(Path(r).parent)
        if parent and parent != ".":
            referenced_dirs.add(parent)

    orphans = []
    for f in all_files:
        if f in referenced:
            continue
        # Scripts/assets often referenced by basename or by execution path
        basename = Path(f).name
        if basename in referenced:
            continue
        # Files inside scripts/ are commonly executed via `python ... scripts/X.py`
        # so we consider any path containment a match
        if any(f in r or r in f for r in referenced):
            continue
        # If a sibling in the same directory is referenced, this file is implied
        f_parent = str(Path(f).parent)
        if f_parent in referenced_dirs:
            continue
        orphans.append(f)
    return sorted(orphans)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 audit_skill.py <path-to-skill-dir-or-slash-command-md>", file=sys.stderr)
        return 2

    target = Path(sys.argv[1]).expanduser().resolve()

    # Slash command mode: target is a .md file under a .claude/commands/ or
    # ~/.claude/commands/ directory.
    is_slash_command = False
    if target.is_file() and target.suffix == ".md":
        parts = target.parts
        for i, p in enumerate(parts):
            if p == "commands" and i > 0 and parts[i - 1] in (".claude", "claude"):
                is_slash_command = True
                break

    if is_slash_command:
        return audit_slash_command(target)

    # Skill mode: directory containing SKILL.md, or SKILL.md itself
    if target.is_file() and target.name == "SKILL.md":
        skill_dir = target.parent
    elif target.is_dir():
        skill_dir = target
    else:
        print(json.dumps({"error": f"not a skill directory or slash command: {target}"}))
        return 2

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        print(json.dumps({"error": f"SKILL.md not found in {skill_dir}"}))
        return 2

    script_dir = Path(__file__).parent

    frontmatter = run_check(script_dir / "validate_frontmatter.py", skill_md)
    refs = run_check(script_dir / "lint_references.py", skill_dir)
    security = run_check(script_dir / "scan_security.py", skill_dir)

    orphans = find_orphans(skill_dir, frontmatter, refs)

    # Run pedagogical-marker prefilter on the security scanner's findings.
    # This demotes findings inside declared pedagogical content and emits
    # marker-mismatch findings when authors use partial markers.
    security_findings = security.get("findings", [])
    if security_findings:
        try:
            marker_input = json.dumps({
                "target": str(skill_dir),
                "findings": security_findings,
            })
            r = subprocess.run(
                [sys.executable, str(script_dir / "pedagogical_marker_check.py"),
                 str(skill_dir), "-"],
                input=marker_input, capture_output=True, text=True, timeout=30,
            )
            if r.returncode == 0 and r.stdout:
                marker_result = json.loads(r.stdout)
                # Replace security findings with marker-aware versions
                security["findings"] = marker_result.get("findings", security_findings)
                security["marker_findings"] = marker_result.get("marker_findings", [])
                security["marker_summary"] = marker_result.get("marker_summary", {})
        except (subprocess.TimeoutExpired, json.JSONDecodeError):
            # Fail-open: keep original findings if marker check fails
            pass

    # v4.6.0 (T025): also run pedagogical-marker triage on REFERENCES findings
    # (broken-link findings from lint_references.py). KB documentation often
    # legitimately references canonical platform paths (`.claude/settings.json`,
    # `.devcontainer/devcontainer.json`) that the auditor flags as broken; these
    # are pedagogical references demote-able by the same pedagogical_sections
    # marker that already triages security findings.
    refs_findings = refs.get("findings", [])
    if refs_findings:
        try:
            marker_input = json.dumps({
                "target": str(skill_dir),
                "findings": refs_findings,
            })
            r = subprocess.run(
                [sys.executable, str(script_dir / "pedagogical_marker_check.py"),
                 str(skill_dir), "-"],
                input=marker_input, capture_output=True, text=True, timeout=30,
            )
            if r.returncode == 0 and r.stdout:
                marker_result = json.loads(r.stdout)
                refs["findings"] = marker_result.get("findings", refs_findings)
                refs["marker_findings"] = (refs.get("marker_findings", [])
                                            + marker_result.get("marker_findings", []))
        except (subprocess.TimeoutExpired, json.JSONDecodeError):
            pass

    report = {
        "target_type": "skill",
        "skill_path": str(skill_dir),
        "skill_name": skill_dir.name,
        "skill_md_lines": line_count(skill_md),
        "frontmatter": frontmatter,
        "references": refs,
        "security": security,
        "orphans": orphans,
        "deterministic_findings": [],
    }

    # Aggregate the deterministic findings into one list for easy agent consumption
    findings = []
    for f in frontmatter.get("findings", []):
        findings.append({"dimension": 2, **f})
    for f in refs.get("findings", []):
        findings.append({"dimension": 4, **f})
    for f in security.get("findings", []):
        # Use final_severity from marker check if present
        sev = f.get("final_severity", f.get("severity"))
        finding = {"dimension": 8, **f}
        finding["severity"] = sev
        findings.append(finding)
    # Marker-emitted findings (mismatched fences, missing declarations)
    for f in security.get("marker_findings", []):
        sev = f.get("final_severity", f.get("severity", "MINOR"))
        finding = {"dimension": 0, **f}
        finding["severity"] = sev
        findings.append(finding)
    if orphans:
        findings.append({
            "dimension": 4,
            "severity": "MAJOR",
            "what": f"Orphaned files (in skill dir but never referenced from SKILL.md): {orphans}",
            "fix": "Either link from SKILL.md or remove.",
        })
    # Per-skill-class line thresholds. Orchestrator recipes ("recipe-*") and
    # platform-knowledge bases ("KB-*-platform") are reference-heavy and may
    # legitimately exceed the default 500-line cap for short, model-invocable
    # routing skills. Thresholds are still bounded to keep model attention from
    # degrading on very long SKILL.md bodies.
    skill_name = report.get("skill_name", "")
    if skill_name.startswith("recipe-") or skill_name.startswith("KB-"):
        major_threshold, blocker_threshold = 1500, 3000
    else:
        major_threshold, blocker_threshold = 500, 1000
    if report["skill_md_lines"] > blocker_threshold:
        findings.append({
            "dimension": 4,
            "severity": "BLOCKER",
            "what": f"SKILL.md is {report['skill_md_lines']} lines (>{blocker_threshold}).",
            "fix": f"Split into reference files. Body should be under {major_threshold} lines.",
        })
    elif report["skill_md_lines"] > major_threshold:
        findings.append({
            "dimension": 4,
            "severity": "MAJOR",
            "what": f"SKILL.md is {report['skill_md_lines']} lines (>{major_threshold}).",
            "fix": "Move detailed content to references/ and link from SKILL.md.",
        })

    report["deterministic_findings"] = findings
    print(json.dumps(report, indent=2))
    return 0


def audit_slash_command(cmd_path: Path) -> int:
    """Audit a slash command file. Same frontmatter checks as skills, but
    no references/ subdir to lint, no orphan check, and the security scan
    only covers the single file."""
    script_dir = Path(__file__).parent

    # Frontmatter validation works the same — the validator just sees a .md
    # with YAML frontmatter. We pass the slash command flag via env so the
    # validator knows to skip a small number of skill-only checks.
    import os
    env = os.environ.copy()
    env["AUDIT_TARGET_TYPE"] = "slash-command"

    try:
        r = subprocess.run(
            [sys.executable, str(script_dir / "validate_frontmatter.py"), str(cmd_path)],
            capture_output=True, text=True, timeout=30, env=env,
        )
        frontmatter = json.loads(r.stdout) if r.stdout else {"error": "no output"}
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        frontmatter = {"error": str(e)}

    # Security scan on the single file
    try:
        r = subprocess.run(
            [sys.executable, str(script_dir / "scan_security.py"), str(cmd_path)],
            capture_output=True, text=True, timeout=30,
        )
        security = json.loads(r.stdout) if r.stdout else {"error": "no output"}
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        security = {"error": str(e)}

    report = {
        "target_type": "slash-command",
        "command_path": str(cmd_path),
        "command_name": cmd_path.stem,
        "lines": line_count(cmd_path),
        "frontmatter": frontmatter,
        "security": security,
        "deterministic_findings": [],
    }

    findings = []
    for f in frontmatter.get("findings", []):
        findings.append({"dimension": 2, **f})
    for f in security.get("findings", []):
        findings.append({"dimension": 8, **f})

    # Slash commands are typically short — flag oversized ones
    if report["lines"] > 200:
        findings.append({
            "dimension": 4,
            "severity": "MAJOR",
            "what": f"Slash command is {report['lines']} lines (>200).",
            "fix": "Slash commands should be concise prompt templates. Consider whether this should be a skill instead.",
        })

    report["deterministic_findings"] = findings
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
