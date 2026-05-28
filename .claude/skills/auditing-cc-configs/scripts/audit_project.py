#!/usr/bin/env python3
"""
audit_project.py — Project-level walker and report aggregator.

Walks a project's .claude/ tree, dispatches each primitive to the appropriate
sub-skill auditor, runs cross-file checks, aggregates findings, and writes a
unified Markdown audit report.

This is the main entry point for the auditing-cc-configs family. The
coordinator skill's SKILL.md tells Claude to invoke this script.

Usage:
    python3 audit_project.py <project-root> [--with-runtime] [--managed]
                                            [--report PATH] [--json]

Options:
    --with-runtime   Pass to auditing-mcp for live server probing.
    --managed        Pass to auditing-settings for stricter enterprise lint.
    --report PATH    Where to write the Markdown report (default: project-audit-report.md
                     in the project root).
    --json           Also emit JSON sidecar at <report>.json.
"""
import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path


# Paths relative to the family root
FAMILY_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_PATHS = {
    "auditing-skills": FAMILY_ROOT / "auditing-skills" / "scripts" / "audit_skill.py",
    "auditing-context-files": FAMILY_ROOT / "auditing-context-files" / "scripts" / "audit_context_file.py",
    "auditing-subagents": FAMILY_ROOT / "auditing-subagents" / "scripts" / "audit_subagent.py",
    "auditing-hooks": FAMILY_ROOT / "auditing-hooks" / "scripts" / "audit_hooks.py",
    "auditing-settings": FAMILY_ROOT / "auditing-settings" / "scripts" / "audit_settings.py",
    "auditing-mcp": FAMILY_ROOT / "auditing-mcp" / "scripts" / "audit_mcp.py",
}
CROSS_FILE_SCRIPT = FAMILY_ROOT / "auditing-cc-configs" / "scripts" / "cross_file_checks.py"
VERDICT_SCRIPT = FAMILY_ROOT / "auditing-cc-configs" / "scripts" / "verdict_compute.py"

# Canonical-drift checks (CANON-1 = Python constants; CANON-2 = documents).
# Both live in auditing-shared and fold their findings into the cross-file
# dimension so they contribute to the project verdict.
CANON_CONST_DRIFT_SCRIPT = FAMILY_ROOT / "auditing-shared" / "scripts" / "audit_canonical_drift.py"
CANON_DOC_DRIFT_SCRIPT = FAMILY_ROOT / "auditing-shared" / "scripts" / "audit_canonical_doc_drift.py"


def run_script(path: Path, args: list[str], timeout: int = 60) -> dict:
    """Run an auditor script and return parsed JSON output (with error fallback)."""
    if not path.exists():
        return {"error": f"script not found: {path}", "findings": []}
    try:
        r = subprocess.run(
            [sys.executable, str(path)] + args,
            capture_output=True, text=True, timeout=timeout,
        )
        if not r.stdout:
            return {"error": r.stderr.strip(), "findings": []}
        try:
            return json.loads(r.stdout)
        except json.JSONDecodeError:
            return {"error": "non-JSON output", "raw": r.stdout, "findings": []}
    except subprocess.TimeoutExpired:
        return {"error": "timeout", "findings": []}


def discover_primitives(root: Path) -> dict:
    """Enumerate every auditable primitive under the project root."""
    primitives = {
        "skills": [],          # paths to skill directories
        "context_files": [],   # CLAUDE.md, rules/*, agent-memory-local/*/MEMORY.md
        "subagents": [],       # .claude/agents/*.md
        "subagent_memory_dirs": [],  # .claude/agent-memory/* and agent-memory-local/*
        "hooks_configs": [],   # settings.json (with hooks block) and hooks.json
        "hook_scripts": [],    # .claude/hooks/*
        "settings_files": [],  # all settings.json variants
        "output_styles": [],   # .claude/output-styles/*.md
        "mcp_configs": [],     # .mcp.json + settings.json with mcpServers
    }

    claude_dir = root / ".claude"

    # CLAUDE.md / context files
    for fname in ("CLAUDE.md", "CLAUDE.local.md"):
        p = root / fname
        if p.is_file():
            primitives["context_files"].append(p)
    p = claude_dir / "CLAUDE.md"
    if p.is_file():
        primitives["context_files"].append(p)
    rules_dir = claude_dir / "rules"
    if rules_dir.is_dir():
        primitives["context_files"].extend(sorted(rules_dir.glob("*.md")))

    # Skills
    skills_dir = claude_dir / "skills"
    if skills_dir.is_dir():
        primitives["skills"] = sorted([d for d in skills_dir.iterdir() if d.is_dir()])

    # Subagents
    agents_dir = claude_dir / "agents"
    if agents_dir.is_dir():
        primitives["subagents"] = sorted(agents_dir.glob("*.md"))

    # Subagent memory
    for kind in ("agent-memory", "agent-memory-local"):
        d = claude_dir / kind
        if d.is_dir():
            primitives["subagent_memory_dirs"].extend(sorted(x for x in d.iterdir() if x.is_dir()))

    # Settings (any file is also a hook config if it has hooks block,
    # and also an MCP config if it has mcpServers block; we route from inside)
    for name in ("settings.json", "settings.local.json"):
        p = claude_dir / name
        if p.is_file():
            primitives["settings_files"].append(p)
            # Detect if it carries hooks or MCP
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    if "hooks" in data:
                        primitives["hooks_configs"].append(p)
                    if "mcpServers" in data:
                        primitives["mcp_configs"].append(p)
            except Exception:
                pass

    # .mcp.json at project root
    p = root / ".mcp.json"
    if p.is_file():
        primitives["mcp_configs"].append(p)

    # Hook scripts
    hooks_dir = claude_dir / "hooks"
    if hooks_dir.is_dir():
        primitives["hook_scripts"] = sorted(p for p in hooks_dir.iterdir() if p.is_file())

    # Output styles
    osd = claude_dir / "output-styles"
    if osd.is_dir():
        primitives["output_styles"] = sorted(osd.glob("*.md"))

    return primitives


def audit_primitives(primitives: dict, options: dict) -> dict:
    """Run each sub-skill auditor against its primitives. Returns a dict of
    per-primitive-type findings."""
    results = {}

    # auditing-skills against each skill dir
    skill_findings = []
    for skill_dir in primitives["skills"]:
        r = run_script(SKILL_PATHS["auditing-skills"], [str(skill_dir)])
        # Normalize findings from the skill audit shape
        for src in ("frontmatter", "references", "security"):
            for f in r.get(src, {}).get("findings", []):
                sev = f.get("final_severity", f.get("severity", "INFO"))
                if sev == "INFO":
                    continue
                f["audited_by"] = "auditing-skills"
                f["primitive"] = str(skill_dir.name)
                f["dimension"] = f.get("dimension", 1)
                skill_findings.append(f)
    results["skills"] = skill_findings

    # auditing-context-files against each context file
    ctx_findings = []
    for cf in primitives["context_files"]:
        r = run_script(SKILL_PATHS["auditing-context-files"], [str(cf)])
        for f in r.get("findings", []):
            sev = f.get("final_severity", f.get("severity", "INFO"))
            if sev == "INFO":
                continue
            f["audited_by"] = "auditing-context-files"
            f["primitive"] = str(cf.name)
            ctx_findings.append(f)
    results["context_files"] = ctx_findings

    # auditing-subagents against each subagent file + memory dir
    sub_findings = []
    for sub in primitives["subagents"]:
        r = run_script(SKILL_PATHS["auditing-subagents"], [str(sub)])
        for f in r.get("findings", []):
            sev = f.get("final_severity", f.get("severity", "INFO"))
            if sev == "INFO":
                continue
            f["audited_by"] = "auditing-subagents"
            f["primitive"] = str(sub.name)
            sub_findings.append(f)
    for memdir in primitives["subagent_memory_dirs"]:
        r = run_script(SKILL_PATHS["auditing-subagents"], [str(memdir)])
        for f in r.get("findings", []):
            sev = f.get("final_severity", f.get("severity", "INFO"))
            if sev == "INFO":
                continue
            f["audited_by"] = "auditing-subagents"
            f["primitive"] = f"agent-memory/{memdir.name}"
            sub_findings.append(f)
    results["subagents"] = sub_findings

    # auditing-hooks against hook configs and hook scripts
    hook_findings = []
    for hc in primitives["hooks_configs"]:
        r = run_script(SKILL_PATHS["auditing-hooks"], [str(hc)])
        for f in r.get("findings", []):
            sev = f.get("final_severity", f.get("severity", "INFO"))
            if sev == "INFO":
                continue
            f["audited_by"] = "auditing-hooks"
            f["primitive"] = str(hc.name) + " (hooks)"
            hook_findings.append(f)
    for hs in primitives["hook_scripts"]:
        r = run_script(SKILL_PATHS["auditing-hooks"], [str(hs)])
        for f in r.get("findings", []):
            sev = f.get("final_severity", f.get("severity", "INFO"))
            if sev == "INFO":
                continue
            f["audited_by"] = "auditing-hooks"
            f["primitive"] = str(hs.name)
            hook_findings.append(f)
    results["hooks"] = hook_findings

    # auditing-settings against each settings file + output styles
    settings_findings = []
    managed_flag = ["--managed"] if options.get("managed") else []
    for sf in primitives["settings_files"]:
        r = run_script(SKILL_PATHS["auditing-settings"], [str(sf)] + managed_flag)
        for f in r.get("findings", []):
            sev = f.get("final_severity", f.get("severity", "INFO"))
            if sev == "INFO":
                continue
            f["audited_by"] = "auditing-settings"
            f["primitive"] = str(sf.name)
            settings_findings.append(f)
    for os_file in primitives["output_styles"]:
        r = run_script(SKILL_PATHS["auditing-settings"], [str(os_file)])
        for f in r.get("findings", []):
            sev = f.get("final_severity", f.get("severity", "INFO"))
            if sev == "INFO":
                continue
            f["audited_by"] = "auditing-settings"
            f["primitive"] = f"output-styles/{os_file.name}"
            settings_findings.append(f)
    results["settings"] = settings_findings

    # auditing-mcp against MCP configs
    mcp_findings = []
    runtime_flag = ["--with-runtime"] if options.get("with_runtime") else []
    for mc in primitives["mcp_configs"]:
        r = run_script(SKILL_PATHS["auditing-mcp"], [str(mc)] + runtime_flag)
        for f in r.get("findings", []):
            sev = f.get("final_severity", f.get("severity", "INFO"))
            if sev == "INFO":
                continue
            f["audited_by"] = "auditing-mcp"
            f["primitive"] = str(mc.name)
            mcp_findings.append(f)
    results["mcp"] = mcp_findings

    return results


def run_cross_file_checks(project_root: Path) -> list[dict]:
    r = run_script(CROSS_FILE_SCRIPT, [str(project_root)])
    findings = r.get("cross_file_findings", [])
    for f in findings:
        f["audited_by"] = "cross-file"
        f["primitive"] = f.get("check", "")
    return findings


def run_canonical_drift_checks(project_root: Path) -> list[dict]:
    """Run CANON-1 (Python-constant drift) and CANON-2 (document drift).

    Both emit {"rule": ..., "findings": [...]}; their findings are normalized
    into the cross-file finding shape so they contribute to the project verdict
    alongside the cross_file_checks output.
    """
    findings: list[dict] = []
    for script, rule in (
        (CANON_CONST_DRIFT_SCRIPT, "CANON-1"),
        (CANON_DOC_DRIFT_SCRIPT, "CANON-2"),
    ):
        r = run_script(script, [str(project_root)])
        for f in r.get("findings", []):
            f.setdefault("rule", rule)
            f["audited_by"] = "canonical-drift"
            f["primitive"] = f.get("rule", rule)
            f.setdefault("message", f.get("what", ""))
            findings.append(f)
    return findings


def compute_verdict(per_primitive: dict, cross_file: list[dict]) -> dict:
    """Call verdict_compute.py with aggregated findings."""
    all_per_primitive = []
    for findings in per_primitive.values():
        all_per_primitive.extend(findings)

    dims = [{"number": i, "name": f"d{i}", "applicable": True} for i in range(1, 11)]
    payload = {
        "target": "project",
        "mode": "project",
        "findings": all_per_primitive,
        "cross_file_findings": cross_file,
        "dimensions": dims,
    }
    try:
        r = subprocess.run(
            [sys.executable, str(VERDICT_SCRIPT), "-"],
            input=json.dumps(payload),
            capture_output=True, text=True, timeout=20,
        )
        if r.stdout:
            return json.loads(r.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return {"score": 0, "verdict": "ERROR", "error": "verdict_compute failed"}


def format_report(project_root: Path, primitives: dict, per_primitive: dict,
                  cross_file: list[dict], verdict: dict, options: dict) -> str:
    """Render the aggregated audit as Markdown."""
    lines: list[str] = []
    lines.append(f"# Claude Code Configuration Audit — {project_root.name}")
    lines.append("")
    lines.append(f"**Audited:** `{project_root}`")
    lines.append(f"**Score:** {verdict.get('score', 'n/a')}/100")
    lines.append(f"**Verdict:** {verdict.get('verdict', 'unknown')}")
    if verdict.get("security_block"):
        lines.append("**SECURITY-BLOCK in effect** — at least one CRITICAL finding confirmed.")
    lines.append("")

    # Primitive inventory
    lines.append("## Inventory")
    lines.append("")
    inv = {
        "skills": len(primitives["skills"]),
        "context files": len(primitives["context_files"]),
        "subagents": len(primitives["subagents"]),
        "subagent memory dirs": len(primitives["subagent_memory_dirs"]),
        "hook scripts": len(primitives["hook_scripts"]),
        "settings files": len(primitives["settings_files"]),
        "output styles": len(primitives["output_styles"]),
        "MCP configs": len(primitives["mcp_configs"]),
    }
    for k, v in inv.items():
        lines.append(f"- {k}: {v}")
    lines.append("")

    # Summary of findings by severity
    all_findings = []
    for f in per_primitive.values():
        all_findings.extend(f)
    all_findings.extend(cross_file)
    by_sev = Counter(f.get("final_severity", f.get("severity", "INFO")) for f in all_findings)

    lines.append("## Summary")
    lines.append("")
    lines.append(f"Total findings: {len(all_findings)}")
    for sev in ("BLOCKER", "MAJOR", "MINOR", "NIT"):
        count = by_sev.get(sev, 0)
        if count:
            lines.append(f"- **{sev}**: {count}")
    lines.append("")

    # Per-skill sections
    section_order = [
        ("skills", "Skills"),
        ("context_files", "Context files (CLAUDE.md, rules)"),
        ("subagents", "Subagents and their memory"),
        ("hooks", "Hooks"),
        ("settings", "Settings"),
        ("mcp", "MCP servers"),
    ]

    for key, header in section_order:
        findings = per_primitive.get(key, [])
        if not findings:
            continue
        lines.append(f"## {header}")
        lines.append("")
        # Group by primitive
        by_prim: dict = {}
        for f in findings:
            by_prim.setdefault(f.get("primitive", "?"), []).append(f)
        for prim, fs in sorted(by_prim.items()):
            lines.append(f"### {prim}")
            lines.append("")
            for f in fs:
                sev = f.get("final_severity", f.get("severity", "INFO"))
                what = f.get("what", "").strip()
                fix = f.get("fix", "").strip()
                lines.append(f"- **[{sev}]** {what}")
                if fix:
                    lines.append(f"  - *Fix:* {fix}")
            lines.append("")

    # Cross-file findings
    if cross_file:
        lines.append("## Cross-file checks")
        lines.append("")
        by_check: dict = {}
        for f in cross_file:
            by_check.setdefault(f.get("check", "?"), []).append(f)
        for check_id, fs in sorted(by_check.items()):
            for f in fs:
                sev = f.get("severity", "INFO")
                what = f.get("what", "").strip()
                fix = f.get("fix", "").strip()
                lines.append(f"- **[{sev}] {check_id}** — {what}")
                if fix:
                    lines.append(f"  - *Fix:* {fix}")
        lines.append("")

    # Footer
    lines.append("## How to read this report")
    lines.append("")
    lines.append("Severity meanings:")
    lines.append("")
    lines.append("- **BLOCKER** — file won't load, security issue, or breaks core functionality. Fix before shipping.")
    lines.append("- **MAJOR** — works but degrades behavior or security.")
    lines.append("- **MINOR** — deviates from best practice.")
    lines.append("- **NIT** — taste or polish.")
    lines.append("")
    lines.append("Verdict bands: PASS≥95 · PASS-WITH-MINOR-FIXES 85–94 · NEEDS-WORK 70–84 · FAIL<70. SECURITY-BLOCK overrides on confirmed CRITICAL.")
    lines.append("")
    if options.get("managed"):
        lines.append("*Audited in `--managed` mode: stricter lint applied to settings.*")
    if options.get("with_runtime"):
        lines.append("*Audited with `--with-runtime`: MCP servers probed live.*")
    lines.append("")
    lines.append("Report-only: this audit does not modify any audited file.")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a Claude Code project end-to-end")
    parser.add_argument("project_root", help="Path to project root (containing .claude/)")
    parser.add_argument("--with-runtime", action="store_true",
                        help="Probe MCP servers live (off by default)")
    parser.add_argument("--managed", action="store_true",
                        help="Apply stricter lint for managed-settings deployment")
    parser.add_argument("--report", default=None,
                        help="Output Markdown report path (default: <root>/project-audit-report.md)")
    parser.add_argument("--json", action="store_true",
                        help="Also write JSON sidecar at <report>.json")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if not project_root.is_dir():
        print(json.dumps({"error": f"not a directory: {project_root}"}))
        return 2

    options = {"with_runtime": args.with_runtime, "managed": args.managed}

    primitives = discover_primitives(project_root)
    per_primitive = audit_primitives(primitives, options)
    cross_file = run_cross_file_checks(project_root)
    cross_file.extend(run_canonical_drift_checks(project_root))
    verdict = compute_verdict(per_primitive, cross_file)

    report_text = format_report(project_root, primitives, per_primitive,
                                  cross_file, verdict, options)

    report_path = Path(args.report) if args.report else (project_root / "project-audit-report.md")
    report_path.write_text(report_text, encoding="utf-8")

    summary = {
        "project_root": str(project_root),
        "verdict": verdict,
        "report_path": str(report_path),
        "primitives_audited": {
            k: len(v) if isinstance(v, list) else 0
            for k, v in primitives.items()
        },
        "finding_counts": {
            k: len(v) for k, v in per_primitive.items()
        },
        "cross_file_findings": len(cross_file),
    }

    if args.json:
        sidecar = report_path.with_suffix(".json")
        sidecar.write_text(json.dumps({
            "summary": summary,
            "per_primitive": per_primitive,
            "cross_file": cross_file,
        }, indent=2), encoding="utf-8")
        summary["json_path"] = str(sidecar)

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
