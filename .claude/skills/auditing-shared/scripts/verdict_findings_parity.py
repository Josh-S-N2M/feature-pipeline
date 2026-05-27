#!/usr/bin/env python3
"""verdict_findings_parity.py — FR-1 verdict-vs-findings parity check.

Detects the structural contradiction where a reviewer declares an approving
verdict while the findings list contains a blocking-severity entry. This
situation is a parity error: the verdict and the evidence are inconsistent.

CLI usage:
    python3 verdict_findings_parity.py <reviewer-output-path> <agent-name>
    python3 verdict_findings_parity.py --selftest

Exit codes:
    0 — pass-through (verdict-findings shape is consistent).
    1 — REJECT (approving verdict + blocking finding present).
    2 — internal error (malformed JSON, file not found, missing CLI args, etc.).

Blocking-severity set (case-insensitive): BLOCKER, CRITICAL.

Per-agent approving-verdict lookup (case-sensitive per cc-design v0.2.0
I-DR-002):
    shared-document-reviewer:       pass, approved, approved_with_conditions
    review-architecture-auditor:    pass, approved, approved_with_conditions
    review-cross-artifact-auditor:  pass, approved, conditional_pass
    execute-phase-quality-reviewer: PASS
    execute-task-quality-handler:   APPROVED
"""
import json
import sys
from pathlib import Path


# Authoritative per-agent approving-verdict sets.
# Lookup is case-sensitive (cc-design v0.2.0 I-DR-002).
APPROVING_VERDICTS: dict[str, frozenset[str]] = {
    "shared-document-reviewer": frozenset({"pass", "approved", "approved_with_conditions"}),
    "review-architecture-auditor": frozenset({"pass", "approved", "approved_with_conditions"}),
    "review-cross-artifact-auditor": frozenset({"pass", "approved", "conditional_pass"}),
    "execute-phase-quality-reviewer": frozenset({"PASS"}),
    "execute-task-quality-handler": frozenset({"APPROVED"}),
}

# Blocking severities compared case-insensitively.
BLOCKING_SEVERITIES: frozenset[str] = frozenset({"blocker", "critical"})


def is_blocking(severity: str) -> bool:
    """Return True if severity (any case) is in the blocking set."""
    return severity.lower() in BLOCKING_SEVERITIES


def check_parity(reviewer_output_path: str, agent_name: str) -> int:
    """Apply the FR-1 parity check.

    Returns 0 (pass-through), 1 (reject), or 2 (internal error).
    Diagnostic on exit 1 is written to stderr.
    """
    path = Path(reviewer_output_path)

    # --- Load and parse ---
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        sys.stderr.write(
            json.dumps({
                "mechanism": "FR-1 verdict-vs-findings parity check",
                "error": f"could not read file: {exc}",
            })
            + "\n"
        )
        return 2

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.stderr.write(
            json.dumps({
                "mechanism": "FR-1 verdict-vs-findings parity check",
                "error": f"malformed JSON in {reviewer_output_path}: {exc}",
            })
            + "\n"
        )
        return 2

    if not isinstance(data, dict):
        sys.stderr.write(
            json.dumps({
                "mechanism": "FR-1 verdict-vs-findings parity check",
                "error": f"expected a JSON object at top level, got {type(data).__name__}",
            })
            + "\n"
        )
        return 2

    # --- Extract fields ---
    verdict = data.get("verdict")
    findings = data.get("findings")

    if not isinstance(verdict, str):
        sys.stderr.write(
            json.dumps({
                "mechanism": "FR-1 verdict-vs-findings parity check",
                "error": f"'verdict' field missing or not a string in {reviewer_output_path}",
            })
            + "\n"
        )
        return 2

    if not isinstance(findings, list):
        sys.stderr.write(
            json.dumps({
                "mechanism": "FR-1 verdict-vs-findings parity check",
                "error": f"'findings' field missing or not an array in {reviewer_output_path}",
            })
            + "\n"
        )
        return 2

    # --- Resolve approving set for this agent ---
    approving_set = APPROVING_VERDICTS.get(agent_name)
    if approving_set is None:
        # Unknown agent: cannot determine approving verdicts. Treat as pass-through
        # rather than silently blocking every unknown agent's output.
        sys.stderr.write(
            json.dumps({
                "mechanism": "FR-1 verdict-vs-findings parity check",
                "warning": (
                    f"agent '{agent_name}' is not in the known-agent table; "
                    "passing through without parity check"
                ),
            })
            + "\n"
        )
        return 0

    # --- Parity check ---
    is_approving = verdict in approving_set

    if not is_approving:
        # Non-approving verdict — parity is fine regardless of finding severities.
        return 0

    # Approving verdict: scan findings for any blocking severity.
    blocking_finding = None
    for entry in findings:
        if not isinstance(entry, dict):
            continue
        sev = entry.get("severity", "")
        if isinstance(sev, str) and is_blocking(sev):
            blocking_finding = entry
            break

    if blocking_finding is None:
        # Approving verdict, no blocking findings — consistent.
        return 0

    # Reject: emit structured diagnostic to stderr.
    offending_severity = blocking_finding.get("severity", "unknown")
    sys.stderr.write(
        json.dumps(
            {
                "mechanism": "FR-1 verdict-vs-findings parity check",
                "offending_artifact": reviewer_output_path,
                "rule_violated": (
                    f"agent {agent_name} declared approving verdict '{verdict}' "
                    f"alongside finding with severity '{offending_severity}'"
                ),
                "remedial_hint": (
                    f"reviewer {agent_name} must either downgrade verdict to "
                    f"non-approving OR escalate/remove the blocking finding "
                    f"before re-submission"
                ),
            },
            indent=2,
        )
        + "\n"
    )
    return 1


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

# Maps fixture filename to (agent_name, expected_exit_code).
# Fixtures live adjacent to this script under
# working/feature/pipeline-quickwins-hardening-r1/fixtures/fr1/ relative to
# the repository root. The selftest locates the repo root via this file's
# ancestry.
_SELFTEST_CASES: list[tuple[str, str, int]] = [
    # Core fixtures
    ("pass_clean.json",                         "shared-document-reviewer",       0),
    ("pass_with_minor.json",                    "shared-document-reviewer",       0),
    ("fail_blocker.json",                       "shared-document-reviewer",       1),
    ("fail_critical.json",                      "shared-document-reviewer",       1),
    ("non_approving_with_blocker.json",         "shared-document-reviewer",       0),
    ("malformed.json",                          "shared-document-reviewer",       2),
    # Per-agent case-sensitive lookup fixtures
    (
        "agent_execute_phase_quality_reviewer_pass.json",
        "execute-phase-quality-reviewer",
        0,
    ),
    (
        # lowercase "pass" is NOT approving for execute-phase-quality-reviewer;
        # blocker present but verdict is non-approving for this agent -> exit 0.
        "agent_execute_phase_quality_reviewer_case_wrong.json",
        "execute-phase-quality-reviewer",
        0,
    ),
    (
        "agent_execute_task_quality_handler_pass.json",
        "execute-task-quality-handler",
        0,
    ),
    (
        "agent_execute_task_quality_handler_fail.json",
        "execute-task-quality-handler",
        1,
    ),
    (
        "agent_review_cross_artifact_auditor_conditional_pass.json",
        "review-cross-artifact-auditor",
        0,
    ),
]


def run_selftest() -> int:
    """Run all fixture cases and report results. Returns 0 if all pass."""
    # Locate fixtures directory relative to repository root.
    repo_root = Path(__file__).resolve()
    # Walk up until we find the working/ directory (repo root marker).
    for parent in repo_root.parents:
        if (parent / "working").is_dir():
            repo_root = parent
            break
    else:
        sys.stderr.write(
            "selftest: could not locate repository root (no 'working/' ancestor found)\n"
        )
        return 2

    fixtures_dir = (
        repo_root
        / "working"
        / "feature"
        / "pipeline-quickwins-hardening-r1"
        / "fixtures"
        / "fr1"
    )

    passed = 0
    failed = 0

    for filename, agent, expected in _SELFTEST_CASES:
        fixture_path = fixtures_dir / filename
        actual = check_parity(str(fixture_path), agent)
        if actual == expected:
            sys.stdout.write(f"  PASS  {filename} ({agent}) -> exit {actual}\n")
            passed += 1
        else:
            sys.stdout.write(
                f"  FAIL  {filename} ({agent}) -> expected exit {expected}, got {actual}\n"
            )
            failed += 1

    total = passed + failed
    sys.stdout.write(f"\n{passed}/{total} cases passed\n")
    return 0 if failed == 0 else 1


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    args = sys.argv[1:]

    if args == ["--selftest"]:
        return run_selftest()

    if len(args) != 2:
        sys.stderr.write(
            "usage: verdict_findings_parity.py <reviewer-output-path> <agent-name>\n"
            "       verdict_findings_parity.py --selftest\n"
        )
        return 2

    reviewer_output_path, agent_name = args
    return check_parity(reviewer_output_path, agent_name)


if __name__ == "__main__":
    sys.exit(main())
