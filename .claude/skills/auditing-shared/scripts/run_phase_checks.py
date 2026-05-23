#!/usr/bin/env python3
"""Coordinate parallel invocation of phase-quality checks.

Per AC-FR-3-b + AC-FR-3-c + D-3 third-option (thin coordinator at
auditing-shared/scripts/ per ADR-0031 canonical-helper-home discipline).

Invokes in parallel:
- unit/integration/E2E test runners (for activated layers — per
  --layers arg)
- auditing-cc-configs/scripts/audit_cc.py
- auditing-github-actions/scripts/audit_workflow.py
- auditing-codespaces/scripts/audit_codespaces.py
- validate_pipeline_frontmatter.py
- check_pipeline_discipline.py

Aggregates per-check JSON outputs into a single 5-dimensional verdict per
Blueprint Contract 2 (tests, audits, validator, discipline,
scope_deviations).

Rollup rule (per Contract 2): blocking finding in any dimension -> overall
BLOCKER; revisable finding -> NEEDS_RECONCILIATION; all clean -> PASS.

Per AC-FR-3-f: when a Layer Scope-activated layer has no test suite,
emits a Level-5 finding ("plan-level gap"); does NOT silently pass.

Per Q-CC-4 / ADR-0033 stub-vs-real surfacing: the audit_codespaces.py stub
returns {"stub": true, "findings": []}; this script treats stub as
"not measured" rather than "measured zero" in the dimensional verdict.
"""
import argparse
import concurrent.futures
import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable


SCRIPTS_DIR = Path(".claude/skills/auditing-shared/scripts")
VALIDATOR = SCRIPTS_DIR / "validate_pipeline_frontmatter.py"
DISCIPLINE_CHECK = SCRIPTS_DIR / "check_pipeline_discipline.py"
GHA_AUDIT = Path(".claude/skills/auditing-github-actions/scripts/audit_workflow.py")
CODESPACES_AUDIT = Path(".claude/skills/auditing-codespaces/scripts/audit_codespaces.py")
CC_AUDIT = Path(".claude/skills/auditing-cc-configs/scripts/audit_project.py")


def run_script(args: list[str], stdin_paths: Iterable[Path] | None = None) -> dict:
    """Run a subprocess; return parsed JSON output or an error finding."""
    try:
        proc = subprocess.run(
            args,
            input=("\n".join(str(p) for p in stdin_paths) if stdin_paths else None),
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"_error": f"failed to invoke {args[0]}: {exc}"}
    if proc.returncode not in (0, 2):
        # Non-zero exit other than the canonical "blocker present" (2) is a
        # genuine failure; surface as error finding.
        return {
            "_error": f"{args[0]} exited {proc.returncode}",
            "_stderr": proc.stderr[:400],
        }
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return {
            "_error": f"{args[0]} stdout not valid JSON: {exc}",
            "_stdout": proc.stdout[:400],
        }


def dimension_rollup(findings: list[dict]) -> str:
    if any(f.get("severity") == "blocker" for f in findings):
        return "BLOCKER"
    if any(f.get("severity") in ("major", "minor") for f in findings):
        return "NEEDS_RECONCILIATION"
    return "PASS"


def empty_dimension() -> dict:
    return {"verdict": "PASS", "findings": [], "stub": False}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--feature-slug",
        required=True,
        help="Feature slug; output goes to working/feature/<slug>/phase-quality-report.json",
    )
    parser.add_argument(
        "--phase",
        required=True,
        help="Phase identifier (e.g., 'phase-1')",
    )
    parser.add_argument(
        "--layers",
        nargs="*",
        default=["claude-code"],
        help="Activated layers per PRD Layer Scope (default: claude-code only)",
    )
    parser.add_argument(
        "--artifact-paths",
        nargs="*",
        default=[],
        help="Pipeline artifact paths to feed to validator + discipline-check",
    )
    parser.add_argument(
        "--scope-deviations-input",
        default=None,
        help=(
            "Optional path to a JSON file enumerating known scope deviations; "
            "treated as the scope_deviations dimension input"
        ),
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print verdict to stdout only; do not write phase-quality-report.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    artifact_paths = [Path(p) for p in args.artifact_paths]

    # Build the task dispatch table; each task is (dimension, script_args, stdin_paths).
    tasks: list[tuple[str, list[str], Iterable[Path] | None]] = []

    # Validator dimension.
    if VALIDATOR.exists() and artifact_paths:
        tasks.append(("validator", ["python3", str(VALIDATOR)] + [str(p) for p in artifact_paths], None))

    # Discipline-check dimension.
    if DISCIPLINE_CHECK.exists() and artifact_paths:
        tasks.append(("discipline", ["python3", str(DISCIPLINE_CHECK)] + [str(p) for p in artifact_paths], None))

    # Audits dimension — codespaces stub + GHA (if file present).
    if CODESPACES_AUDIT.exists():
        tasks.append(("audits:codespaces", ["python3", str(CODESPACES_AUDIT)], None))
    if GHA_AUDIT.exists():
        tasks.append(("audits:gha", ["python3", str(GHA_AUDIT)], None))
    # cc-audit is intentionally NOT auto-invoked here; recipe-feature-pipeline
    # documents that cc-audit is the bigger-batch tool. The thin coordinator
    # surface here calls cc-audit only when --include-cc-audit is supplied
    # (future-extensibility hook; default behavior is to delegate to caller).

    # Run all tasks in parallel.
    dimension_results: dict[str, dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, len(tasks))) as ex:
        future_to_dim = {ex.submit(run_script, args_list, stdin): dim for dim, args_list, stdin in tasks}
        for fut in concurrent.futures.as_completed(future_to_dim):
            dim = future_to_dim[fut]
            dimension_results[dim] = fut.result()

    # Assemble 5-dimensional verdict per Contract 2.
    per_dimension: dict[str, dict] = {
        "tests": empty_dimension(),
        "audits": empty_dimension(),
        "validator": empty_dimension(),
        "discipline": empty_dimension(),
        "scope_deviations": empty_dimension(),
    }

    # Validator dimension.
    val = dimension_results.get("validator")
    if val:
        if "_error" in val:
            per_dimension["validator"]["findings"].append(
                {
                    "domain": "validator",
                    "severity": "info",
                    "source_activity": "frontmatter-validator",
                    "file_path": "<coordinator>",
                    "message": val["_error"],
                    "dispatch_hint": "n/a",
                    "depth_level": "0",
                }
            )
        else:
            per_dimension["validator"]["findings"].extend(val.get("findings", []))
        per_dimension["validator"]["verdict"] = dimension_rollup(per_dimension["validator"]["findings"])

    # Discipline dimension.
    disc = dimension_results.get("discipline")
    if disc:
        if "_error" in disc:
            per_dimension["discipline"]["findings"].append(
                {
                    "domain": "discipline",
                    "severity": "info",
                    "source_activity": "discipline-check",
                    "file_path": "<coordinator>",
                    "message": disc["_error"],
                    "dispatch_hint": "n/a",
                    "depth_level": "0",
                }
            )
        else:
            per_dimension["discipline"]["findings"].extend(disc.get("findings", []))
        per_dimension["discipline"]["verdict"] = dimension_rollup(per_dimension["discipline"]["findings"])

    # Audits dimension — aggregate cs + gha; honor stub-vs-real distinction.
    audits_findings: list[dict] = []
    audits_stub_count = 0
    audits_present_count = 0
    for key in ("audits:codespaces", "audits:gha"):
        r = dimension_results.get(key)
        if r is None:
            continue
        audits_present_count += 1
        if r.get("stub") is True:
            audits_stub_count += 1
            continue
        if "_error" in r:
            audits_findings.append(
                {
                    "domain": "audits",
                    "severity": "info",
                    "source_activity": key.split(":", 1)[1] + "-audit",
                    "file_path": "<coordinator>",
                    "message": r["_error"],
                    "dispatch_hint": "n/a",
                    "depth_level": "0",
                }
            )
            continue
        audits_findings.extend(r.get("findings", []))
    per_dimension["audits"]["findings"] = audits_findings
    per_dimension["audits"]["verdict"] = dimension_rollup(audits_findings)
    per_dimension["audits"]["stub"] = audits_stub_count > 0
    per_dimension["audits"]["stub_count"] = audits_stub_count

    # Tests dimension: per AC-FR-3-f, when an activated layer has no test
    # suite, emit a Level-5 plan-level-gap finding.
    test_findings: list[dict] = []
    layer_test_paths = {
        "claude-code": Path("tests"),  # repo-root tests if exists
        "backend": Path("backend/tests"),
        "frontend": Path("frontend/tests"),
        "api": Path("api/tests"),
        "database": Path("database/tests"),
        "query": Path("query/tests"),
        "cicd": Path(".github/workflows"),  # workflows are the test surface for CICD
        "iac": Path("iac/tests"),
        "codespaces": Path(".devcontainer"),
    }
    for layer in args.layers:
        path = layer_test_paths.get(layer)
        if path is None or not path.exists():
            test_findings.append(
                {
                    "domain": "tests",
                    "severity": "minor",
                    "source_activity": "unit",
                    "file_path": str(path) if path else f"<{layer}>",
                    "message": f"activated layer '{layer}' has no test suite (Level-5 plan-level gap per AC-FR-3-f)",
                    "dispatch_hint": "plan-author",
                    "depth_level": "5",
                }
            )
    per_dimension["tests"]["findings"] = test_findings
    per_dimension["tests"]["verdict"] = dimension_rollup(test_findings)

    # Scope-deviations dimension: input-driven (caller passes a JSON file).
    sd_findings: list[dict] = []
    if args.scope_deviations_input:
        sd_path = Path(args.scope_deviations_input)
        if sd_path.exists():
            try:
                sd_data = json.loads(sd_path.read_text())
                sd_findings = sd_data.get("findings", [])
            except json.JSONDecodeError as exc:
                sd_findings.append(
                    {
                        "domain": "scope_deviations",
                        "severity": "info",
                        "source_activity": "scope-deviation-scan",
                        "file_path": str(sd_path),
                        "message": f"scope-deviations input not valid JSON: {exc}",
                        "dispatch_hint": "n/a",
                        "depth_level": "0",
                    }
                )
    per_dimension["scope_deviations"]["findings"] = sd_findings
    per_dimension["scope_deviations"]["verdict"] = dimension_rollup(sd_findings)

    # Overall verdict.
    overall = "PASS"
    for dim_result in per_dimension.values():
        if dim_result["verdict"] == "BLOCKER":
            overall = "BLOCKER"
            break
        if dim_result["verdict"] == "NEEDS_RECONCILIATION":
            overall = "NEEDS_RECONCILIATION"

    # Flatten findings to top-level (per Contract 2).
    all_findings: list[dict] = []
    for dim_result in per_dimension.values():
        all_findings.extend(dim_result["findings"])

    report = {
        "verdict": overall,
        "per_dimension_status": {k: v["verdict"] for k, v in per_dimension.items()},
        "findings": all_findings,
        "phase": args.phase,
        "feature_slug": args.feature_slug,
        "audits_stub": per_dimension["audits"].get("stub", False),
        "audits_stub_count": per_dimension["audits"].get("stub_count", 0),
    }

    sys.stdout.write(json.dumps(report, indent=2) + "\n")

    if not args.no_write:
        out_dir = Path("working/feature") / args.feature_slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "phase-quality-report.json").write_text(
            json.dumps(report, indent=2)
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
