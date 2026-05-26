#!/usr/bin/env python3
"""End-to-end smoke test for auditing-shared scripts (T1.7).

Exercises T1.1 (validate_pipeline_frontmatter.py), T1.2 (log_state_transition.py),
T1.3 (detect_stubs.py), T1.4 (run_phase_checks.py), T1.5 (check_pipeline_discipline.py),
and T1.6 (audit_codespaces.py) end-to-end against curated test fixtures.

Verifies:
- Each script exits cleanly on `--help` (where applicable).
- Each script emits valid JSON on stdout (where applicable).
- The coordinator (run_phase_checks.py) correctly aggregates outputs into
  the 5-dimensional Contract 2 verdict.
- Q-CC-4 stub-vs-real distinction: audits_stub field is True when only the
  codespaces stub ran; False when real audits also ran.

Run as: `python3 .claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py`
Exit code 0 = all scenarios pass; non-zero = failure with diagnostic on stderr.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Validator imports — used by the issue-doc-type fixture scenarios (H–K).
sys.path.insert(0, str(Path(__file__).parent))
from validate_pipeline_frontmatter import (  # noqa: E402
    parse_frontmatter,
    validate_issue_artifact,
    validate_file,
    validate_pipeline_artifact,
)


SCRIPTS = {
    "validator": ".claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py",
    "log_state": ".claude/skills/auditing-shared/scripts/log_state_transition.py",
    "stubs": ".claude/skills/auditing-shared/scripts/detect_stubs.py",
    "discipline": ".claude/skills/auditing-shared/scripts/check_pipeline_discipline.py",
    "coordinator": ".claude/skills/auditing-shared/scripts/run_phase_checks.py",
    "codespaces_stub": ".claude/skills/auditing-codespaces/scripts/audit_codespaces.py",
    "adr_placement": ".claude/skills/auditing-shared/scripts/validate_adr_placement.py",
}

# Repo root — used by ADR placement tests to anchor paths.
REPO_ROOT = str(Path(__file__).resolve().parents[4])

# Corpus-fixture exemption is no longer required after the 2026-05-26 rename
# (per pipeline-quickwins-hardening-r1 user direction): the synthesize-skill
# replication corpus at
# .claude/skills/synthesize/references/task-08-replication-corpus/final-output/adrs/
# now holds files named adr-NNN-*.example.md (not ADR-NNN-*.md), so the
# validator's rglob('ADR-*.md') no longer matches them. The smoke tests
# below therefore invoke the validator without any --allowlist flag, matching
# the orchestrator surface's canonical-only posture per ADR-0054 + ADR-0056.


class SmokeFailure(Exception):
    pass


def run(cmd: list[str], stdin: str | None = None, cwd: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, input=stdin, capture_output=True, text=True, timeout=60, cwd=cwd
    )


def assert_eq(name: str, got, want):
    if got != want:
        raise SmokeFailure(f"{name}: got {got!r}, want {want!r}")


def assert_in(name: str, needle, haystack):
    if needle not in haystack:
        raise SmokeFailure(f"{name}: {needle!r} not in {haystack!r}")


# -----------------------------------------------------------------------------
# Scenario A — every script's --help works (where applicable).
# -----------------------------------------------------------------------------
def scenario_help() -> None:
    for name, path in SCRIPTS.items():
        if name == "codespaces_stub":
            continue  # no argparse on the trivial stub
        proc = run(["python3", path, "--help"])
        if proc.returncode != 0:
            raise SmokeFailure(f"{name} --help exited {proc.returncode}: {proc.stderr}")
        assert_in(f"{name} help banner", "usage:", proc.stdout)


# -----------------------------------------------------------------------------
# Scenario B — codespaces stub emits canonical {"stub": true, "findings": []}.
# -----------------------------------------------------------------------------
def scenario_codespaces_stub() -> None:
    proc = run(["python3", SCRIPTS["codespaces_stub"]])
    if proc.returncode != 0:
        raise SmokeFailure(f"codespaces stub exited {proc.returncode}: {proc.stderr}")
    data = json.loads(proc.stdout)
    assert_eq("codespaces stub: stub field", data.get("stub"), True)
    assert_eq("codespaces stub: findings", data.get("findings"), [])
    assert_eq("codespaces stub: field set", set(data.keys()), {"stub", "findings"})


# -----------------------------------------------------------------------------
# Scenario C — validator catches I-AA-601 invariants on a synthetic agent fixture.
# -----------------------------------------------------------------------------
def scenario_validator_agent_rules() -> None:
    with tempfile.TemporaryDirectory() as td:
        # Synthetic agent file with memory: none (invalid per I-AA-601).
        agents_dir = Path(td) / ".claude" / "agents"
        agents_dir.mkdir(parents=True)
        bad_agent = agents_dir / "bad-agent.md"
        bad_agent.write_text(
            "---\n"
            "name: bad-agent\n"
            "description: A bad agent\n"
            "tools: [Read, Write, Bash, Unknown]\n"
            "memory: none\n"
            "effort: gigantic\n"
            "---\n\n"
            "Body.\n"
        )
        proc = run(["python3", SCRIPTS["validator"], str(bad_agent)])
        if proc.returncode != 0:
            raise SmokeFailure(f"validator exited {proc.returncode}: {proc.stderr}")
        data = json.loads(proc.stdout)
        messages = " ; ".join(f["message"] for f in data["findings"])
        assert_in("validator: rejects memory:none", "memory: none is INVALID", messages)
        assert_in("validator: rejects bad effort", "effort value 'gigantic'", messages)
        assert_in("validator: flags Unknown tool", "Unknown", messages)


# -----------------------------------------------------------------------------
# Scenario D — discipline-check catches pipeline-stage-by-number references.
# -----------------------------------------------------------------------------
def scenario_discipline_check() -> None:
    with tempfile.TemporaryDirectory() as td:
        good = Path(td) / "good.md"
        good.write_text("This Plan has 7 phases. discipline 5 is OK. Phase 1 starts setup.\n")
        bad = Path(td) / "bad.md"
        bad.write_text("This pipeline runs through stage 12. Stage 5 is the early one.\n")
        bad_norm = Path(td) / "bad_normative.md"
        bad_norm.write_text("The validator MUST run at stage 7 per AC-FR-6-a.\n")

        proc = run(["python3", SCRIPTS["discipline"], str(good)])
        data = json.loads(proc.stdout)
        assert_eq("discipline: clean fixture", data["findings"], [])

        proc = run(["python3", SCRIPTS["discipline"], str(bad)])
        data = json.loads(proc.stdout)
        if len(data["findings"]) < 2:
            raise SmokeFailure(
                f"discipline: expected >=2 findings on bad fixture, got {len(data['findings'])}"
            )

        proc = run(["python3", SCRIPTS["discipline"], str(bad_norm)])
        data = json.loads(proc.stdout)
        if not any(f["severity"] == "major" for f in data["findings"]):
            raise SmokeFailure(
                "discipline: expected MAJOR finding in normative fixture, got "
                + json.dumps(data["findings"])
            )

        # Backtick-suppression: pedagogical patterns inside `backticks` should
        # NOT be flagged (per cycle-3+ refinement).
        backtick_ok = Path(td) / "backtick_pedagogical.md"
        backtick_ok.write_text(
            "Pedagogical example: the literal pattern `stage 12` is what the "
            "discipline-check detects, but quoting it here in code spans does "
            "NOT count as a real violation.\n"
        )
        proc = run(["python3", SCRIPTS["discipline"], str(backtick_ok)])
        data = json.loads(proc.stdout)
        if data["findings"]:
            raise SmokeFailure(
                "discipline: backtick-pedagogical fixture should produce zero "
                "findings; got " + json.dumps(data["findings"])
            )


# -----------------------------------------------------------------------------
# Scenario E — detect_stubs distinguishes impl-file blocker from test-file major.
# -----------------------------------------------------------------------------
def scenario_detect_stubs() -> None:
    with tempfile.TemporaryDirectory() as td:
        impl = Path(td) / "myimpl.py"
        impl.write_text(
            "def real():\n    return 1\n\ndef stubbed():\n    pass\n"
        )
        test = Path(td) / "tests" / "test_something.py"
        test.parent.mkdir()
        test.write_text(
            "def test_real():\n    assert 1 + 1 == 2\n\n"
            "def test_stubbed():\n    assert True\n"
        )
        clean = Path(td) / "clean.py"
        clean.write_text(
            "def f(x):\n    try:\n        return int(x)\n    except ValueError:\n        return 0\n"
        )

        proc = run(["python3", SCRIPTS["stubs"], str(impl), str(test), str(clean)])
        data = json.loads(proc.stdout)
        severities = {f["severity"] for f in data["findings"]}
        impls = [f for f in data["findings"] if "myimpl.py" in f["file_path"]]
        tests = [f for f in data["findings"] if "tests/" in f["file_path"]]
        cleans = [f for f in data["findings"] if "clean.py" in f["file_path"]]
        if not impls or not any(f["severity"] == "blocker" for f in impls):
            raise SmokeFailure(
                f"detect_stubs: expected blocker on impl stub, got {impls}"
            )
        if not tests or not any(f["severity"] == "major" for f in tests):
            raise SmokeFailure(
                f"detect_stubs: expected major on test stub, got {tests}"
            )
        if cleans:
            raise SmokeFailure(
                f"detect_stubs: false-positive on clean fixture: {cleans}"
            )


# -----------------------------------------------------------------------------
# Scenario F — log_state_transition appends JSONL line.
# -----------------------------------------------------------------------------
def scenario_log_state_transition() -> None:
    with tempfile.TemporaryDirectory() as td:
        payload = {
            "timestamp": "2026-05-22T23:00:00Z",
            "transition_name": "T0",
            "from_state": "INIT",
            "to_state": "pending",
            "trigger": "smoke-test",
            "invoking_agent": "execute-orchestrator",
        }
        proc = run(
            ["python3", SCRIPTS["log_state"], "--feature-slug", "smoke", "--log-root", td],
            stdin=json.dumps(payload),
        )
        if proc.returncode != 0:
            raise SmokeFailure(f"log_state exited {proc.returncode}: {proc.stderr}")
        log_path = Path(td) / "smoke" / "state-transitions.log"
        if not log_path.exists():
            raise SmokeFailure(f"log_state: log file not created at {log_path}")
        content = log_path.read_text().strip()
        line = json.loads(content)
        assert_eq("log_state: transition_name persisted", line["transition_name"], "T0")
        assert_eq("log_state: from_state persisted", line["from_state"], "INIT")


# -----------------------------------------------------------------------------
# Scenario H — 18 positive issue-doc-type fixtures each return zero findings.
# -----------------------------------------------------------------------------

FIXTURE_DIR = Path(__file__).parent / "test_fixtures" / "issue_doc_types"

POSITIVE_FIXTURES: dict[str, str] = {
    "positive-register-draft.md": "Issues/test-register-draft/register.md",
    "positive-register-open.md": "Issues/test-register-open/register.md",
    "positive-register-adopted.md": "Issues/test-register-adopted/register.md",
    "positive-register-complete.md": "Issues/test-register-complete/register.md",
    "positive-register-superseded.md": "Issues/test-register-superseded/register.md",
    "positive-register-wontfix.md": "Issues/test-register-wontfix/register.md",
    "positive-analysis-draft.md": "Issues/test-analysis-draft/analysis.md",
    "positive-analysis-open.md": "Issues/test-analysis-open/analysis.md",
    "positive-analysis-adopted.md": "Issues/test-analysis-adopted/analysis.md",
    "positive-analysis-complete.md": "Issues/test-analysis-complete/analysis.md",
    "positive-analysis-superseded.md": "Issues/test-analysis-superseded/analysis.md",
    "positive-analysis-wontfix.md": "Issues/test-analysis-wontfix/analysis.md",
    "positive-proposal-draft.md": "Issues/test-proposal-draft/proposal.md",
    "positive-proposal-open.md": "Issues/test-proposal-open/proposal.md",
    "positive-proposal-adopted.md": "Issues/test-proposal-adopted/proposal.md",
    "positive-proposal-complete.md": "Issues/test-proposal-complete/proposal.md",
    "positive-proposal-superseded.md": "Issues/test-proposal-superseded/proposal.md",
    "positive-proposal-wontfix.md": "Issues/test-proposal-wontfix/proposal.md",
}


def scenario_positive_fixtures() -> None:
    """18 positive fixtures must each produce zero findings from validate_issue_artifact."""
    for fixture_name, synthetic_path in POSITIVE_FIXTURES.items():
        fixture_file = FIXTURE_DIR / fixture_name
        text = fixture_file.read_text(encoding="utf-8")
        parsed = parse_frontmatter(text)
        if parsed is None:
            raise SmokeFailure(
                f"positive fixture {fixture_name}: no YAML frontmatter found"
            )
        fm, _ = parsed
        findings = validate_issue_artifact(fm, Path(synthetic_path))
        assert_eq(
            f"positive fixture {fixture_name}: zero findings",
            findings,
            [],
        )
        print(f"  PASS  positive fixture {fixture_name} → []", file=sys.stderr)


# -----------------------------------------------------------------------------
# Scenario I — 10 negative/advisory fixtures fire expected findings.
# -----------------------------------------------------------------------------

# Maps fixture filename → (synthetic_path, expected_field_in_message)
NEGATIVE_BLOCKER_FIELD_FIXTURES: dict[str, tuple[str, str]] = {
    "negative-missing-since-open.md": (
        "Issues/test-register-missing-since/register.md",
        "since",
    ),
    "negative-missing-adopted_at-adopted.md": (
        "Issues/test-analysis-missing-adopted_at/analysis.md",
        "adopted_at",
    ),
    "negative-missing-resolution_summary-complete.md": (
        "Issues/test-proposal-missing-resolution_summary/proposal.md",
        "resolution_summary",
    ),
    "negative-missing-superseded_by_issue_id-superseded.md": (
        "Issues/test-register-missing-superseded_by_issue_id/register.md",
        "superseded_by_issue_id",
    ),
    "negative-missing-wontfix_rationale-wontfix.md": (
        "Issues/test-analysis-missing-wontfix_rationale/analysis.md",
        "wontfix_rationale",
    ),
    "negative-missing-decided_at-wontfix.md": (
        "Issues/test-proposal-missing-decided_at/proposal.md",
        "decided_at",
    ),
}

INVALID_STATUS_FIXTURES: dict[str, str] = {
    "negative-invalid-status-register.md": "Issues/test-register-invalid-status/register.md",
    "negative-invalid-status-analysis.md": "Issues/test-analysis-invalid-status/analysis.md",
    "negative-invalid-status-proposal.md": "Issues/test-proposal-invalid-status/proposal.md",
}

ADVISORY_FIXTURES: dict[str, str] = {
    # Synthetic path topic slug matches the id in the fixture (PROPOSAL-test-proposal-no-pff)
    # so Check 5 (id vs path-derived id) does not fire a spurious blocker alongside the
    # advisory info finding we are testing.
    "advisory-proposal-no-proposes_future_feature.md": (
        "Issues/test-proposal-no-pff/proposal.md"
    ),
}


def scenario_negative_fixtures() -> None:
    """10 negative/advisory fixtures fire exactly the expected findings."""
    # Group 1: missing per-state required field → 1 blocker containing the field name.
    for fixture_name, (synthetic_path, expected_field) in NEGATIVE_BLOCKER_FIELD_FIXTURES.items():
        fixture_file = FIXTURE_DIR / fixture_name
        text = fixture_file.read_text(encoding="utf-8")
        parsed = parse_frontmatter(text)
        if parsed is None:
            raise SmokeFailure(
                f"negative fixture {fixture_name}: no YAML frontmatter found"
            )
        fm, _ = parsed
        findings = validate_issue_artifact(fm, Path(synthetic_path))
        assert_eq(
            f"negative fixture {fixture_name}: exactly 1 finding",
            len(findings),
            1,
        )
        assert_eq(
            f"negative fixture {fixture_name}: severity=blocker",
            findings[0]["severity"],
            "blocker",
        )
        assert_in(
            f"negative fixture {fixture_name}: message contains field name",
            expected_field,
            findings[0]["message"],
        )
        print(
            f"  PASS  negative fixture {fixture_name} → 1 blocker [{expected_field}]",
            file=sys.stderr,
        )

    # Group 2: invalid status → 1 blocker containing "vocabulary".
    for fixture_name, synthetic_path in INVALID_STATUS_FIXTURES.items():
        fixture_file = FIXTURE_DIR / fixture_name
        text = fixture_file.read_text(encoding="utf-8")
        parsed = parse_frontmatter(text)
        if parsed is None:
            raise SmokeFailure(
                f"invalid-status fixture {fixture_name}: no YAML frontmatter found"
            )
        fm, _ = parsed
        findings = validate_issue_artifact(fm, Path(synthetic_path))
        assert_eq(
            f"invalid-status fixture {fixture_name}: exactly 1 finding",
            len(findings),
            1,
        )
        assert_eq(
            f"invalid-status fixture {fixture_name}: severity=blocker",
            findings[0]["severity"],
            "blocker",
        )
        assert_in(
            f"invalid-status fixture {fixture_name}: message contains 'vocabulary'",
            "vocabulary",
            findings[0]["message"],
        )
        print(
            f"  PASS  invalid-status fixture {fixture_name} → 1 blocker [vocabulary]",
            file=sys.stderr,
        )

    # Group 3: advisory (info) — missing proposes_future_feature.
    for fixture_name, synthetic_path in ADVISORY_FIXTURES.items():
        fixture_file = FIXTURE_DIR / fixture_name
        text = fixture_file.read_text(encoding="utf-8")
        parsed = parse_frontmatter(text)
        if parsed is None:
            raise SmokeFailure(
                f"advisory fixture {fixture_name}: no YAML frontmatter found"
            )
        fm, _ = parsed
        findings = validate_issue_artifact(fm, Path(synthetic_path))
        assert_eq(
            f"advisory fixture {fixture_name}: exactly 1 finding",
            len(findings),
            1,
        )
        assert_eq(
            f"advisory fixture {fixture_name}: severity=info",
            findings[0]["severity"],
            "info",
        )
        assert_in(
            f"advisory fixture {fixture_name}: message contains 'proposes_future_feature'",
            "proposes_future_feature",
            findings[0]["message"],
        )
        print(
            f"  PASS  advisory fixture {fixture_name} → 1 info [proposes_future_feature]",
            file=sys.stderr,
        )


# -----------------------------------------------------------------------------
# Scenario J — AC-BE-10: evidence/ path early-return fires → returns [].
# -----------------------------------------------------------------------------

def scenario_ac_be_10_evidence_path() -> None:
    """AC-BE-10: validate_file on a path under Issues/<topic>/evidence/ MUST
    return [] regardless of frontmatter (path-prefix early-return per ADR-0044
    §4 + spec §2.3)."""
    fixture_path = (
        FIXTURE_DIR
        / "evidence-path-fixtures"
        / "Issues"
        / "per-agent-design-evaluation-gap"
        / "evidence"
        / "agent-roster-impact-matrix.md"
    )
    result = validate_file(fixture_path)
    assert_eq("ac-be-10: evidence/ path early-return", result, [])
    print("  PASS  ac-be-10: evidence/ path early-return → []", file=sys.stderr)


# -----------------------------------------------------------------------------
# Scenario K — positive control: non-Issues unknown doc_type produces minor finding.
# -----------------------------------------------------------------------------

def scenario_positive_control_non_issues_unknown_doctype() -> None:
    """Positive control per Blueprint §Verification Strategy: the path-prefix
    skip MUST NOT over-silence. A non-Issues file with an unknown doc_type still
    produces a minor 'not in known category' finding."""
    fm = {
        "doc_type": "not-a-known-type",
        "feature_slug": "test",
        "status": "whatever",
    }
    # Use a synthetic path under working/feature/ (NOT Issues/) so the
    # path-prefix early-return does not fire.
    findings = validate_pipeline_artifact(
        fm, Path("working/feature/test-not-issues/some-file.md")
    )
    minor_findings = [
        f for f in findings
        if f["severity"] == "minor" and "not in known category" in f["message"]
    ]
    if len(minor_findings) != 1:
        raise SmokeFailure(
            f"positive control: expected 1 minor finding for unknown doc_type; got {findings}"
        )
    print(
        "  PASS  positive control: unknown doc_type → minor finding", file=sys.stderr
    )


# -----------------------------------------------------------------------------
# Scenario L — validate_adr_placement positive: clean repo → exit 0 / PASS / [].
# -----------------------------------------------------------------------------
def scenario_adr_placement_positive() -> None:
    """Positive test (AT-046): validate_adr_placement against the full repo
    returns exit 0, verdict PASS, and an empty findings array.  This exercises
    the post-Phase-3 clean-repo state.  No --allowlist flag is passed — after
    the 2026-05-26 corpus-fixture rename (see CORPUS_ALLOWLIST removal note
    above), the canonical-only posture holds without any exemption."""
    proc = run(
        [
            "python3",
            SCRIPTS["adr_placement"],
            REPO_ROOT,
        ],
        cwd=REPO_ROOT,
    )
    if proc.returncode != 0:
        raise SmokeFailure(
            f"adr_placement positive: expected exit 0, got {proc.returncode}; "
            f"stderr={proc.stderr!r}; stdout={proc.stdout!r}"
        )
    data = json.loads(proc.stdout)
    assert_eq("adr_placement positive: verdict", data.get("verdict"), "PASS")
    assert_eq("adr_placement positive: findings empty", data.get("findings"), [])


# -----------------------------------------------------------------------------
# Scenario M — validate_adr_placement negative: feature-scoped ADR triggers BLOCK.
# -----------------------------------------------------------------------------
def scenario_adr_placement_negative() -> None:
    """Negative test (AT-052): placing an ADR under working/feature/test-fixture/adrs/
    (a non-canonical location) must produce exit 2, verdict BLOCK, and a finding
    whose adr_file references the transient fixture path.  Fixture is cleaned up
    after assertion."""
    fixture_dir = Path(REPO_ROOT) / "working" / "feature" / "test-fixture" / "adrs"
    fixture_file = fixture_dir / "ADR-9999-fixture-canonical-only-test.md"

    # Create transient fixture.
    fixture_dir.mkdir(parents=True, exist_ok=True)
    fixture_file.write_text(
        "---\n"
        "id: ADR-9999\n"
        "title: Fixture ADR — canonical-only test\n"
        "status: proposed\n"
        "---\n\n"
        "Transient fixture for smoke_test_auditing_shared.py negative test case.\n"
        "This file must not persist after the test run.\n"
    )

    try:
        proc = run(
            [
                "python3",
                SCRIPTS["adr_placement"],
                REPO_ROOT,
            ],
            cwd=REPO_ROOT,
        )
        if proc.returncode != 2:
            raise SmokeFailure(
                f"adr_placement negative: expected exit 2, got {proc.returncode}; "
                f"stdout={proc.stdout!r}"
            )
        data = json.loads(proc.stdout)
        assert_eq("adr_placement negative: verdict", data.get("verdict"), "BLOCK")
        findings = data.get("findings", [])
        if not findings:
            raise SmokeFailure(
                "adr_placement negative: expected at least one finding, got empty findings"
            )
        # At least one finding must reference the fixture path.
        fixture_rel = "working/feature/test-fixture/adrs/ADR-9999-fixture-canonical-only-test.md"
        matching = [f for f in findings if fixture_rel in f.get("adr_file", "")]
        if not matching:
            raise SmokeFailure(
                f"adr_placement negative: no finding references {fixture_rel!r}; "
                f"findings={findings}"
            )
    finally:
        # Always cleanup — even on assertion failure.
        if fixture_file.exists():
            fixture_file.unlink()
        if fixture_dir.exists():
            try:
                fixture_dir.rmdir()  # removes only if empty
            except OSError:
                pass
        # Remove parent working/feature/test-fixture if empty.
        test_fixture_dir = Path(REPO_ROOT) / "working" / "feature" / "test-fixture"
        if test_fixture_dir.exists():
            try:
                test_fixture_dir.rmdir()
            except OSError:
                pass
        # Verify cleanup.
        if fixture_file.exists():
            raise SmokeFailure(
                f"adr_placement negative: cleanup failed — fixture still exists at {fixture_file}"
            )


# -----------------------------------------------------------------------------
# Scenario G — coordinator returns 5-dimensional verdict; stub field correct.
# -----------------------------------------------------------------------------
def scenario_coordinator_dimensional_verdict() -> None:
    proc = run(
        [
            "python3", SCRIPTS["coordinator"],
            "--feature-slug", "smoke-test",
            "--phase", "phase-smoke",
            "--layers", "claude-code",
            "--no-write",
        ]
    )
    if proc.returncode != 0:
        raise SmokeFailure(f"coordinator exited {proc.returncode}: {proc.stderr}")
    data = json.loads(proc.stdout)
    required_dims = {"tests", "audits", "validator", "discipline", "scope_deviations"}
    if set(data["per_dimension_status"].keys()) != required_dims:
        raise SmokeFailure(
            f"coordinator: per_dimension_status keys mismatch — got {set(data['per_dimension_status'].keys())}"
        )
    if not isinstance(data.get("audits_stub"), bool):
        raise SmokeFailure(f"coordinator: missing audits_stub bool field")
    if data["verdict"] not in {"PASS", "NEEDS_RECONCILIATION", "BLOCKER"}:
        raise SmokeFailure(f"coordinator: invalid overall verdict {data['verdict']}")


# -----------------------------------------------------------------------------
# Runner.
# -----------------------------------------------------------------------------
SCENARIOS = [
    ("help banners", scenario_help),
    ("codespaces stub canonical output", scenario_codespaces_stub),
    ("validator agent rules (I-AA-601)", scenario_validator_agent_rules),
    ("discipline check (clean + bad + normative)", scenario_discipline_check),
    ("detect_stubs (impl blocker + test major + false-positive suppression)", scenario_detect_stubs),
    ("log_state_transition append", scenario_log_state_transition),
    ("coordinator 5-dimensional verdict + stub field", scenario_coordinator_dimensional_verdict),
    ("H: 18 positive issue-doc-type fixtures → zero findings", scenario_positive_fixtures),
    ("I: 10 negative/advisory fixtures → expected findings", scenario_negative_fixtures),
    ("J: AC-BE-10 evidence/ path early-return → []", scenario_ac_be_10_evidence_path),
    ("K: positive control — non-Issues unknown doc_type → minor finding", scenario_positive_control_non_issues_unknown_doctype),
    ("L: validate_adr_placement positive — clean repo → exit 0 / PASS / []", scenario_adr_placement_positive),
    ("M: validate_adr_placement negative — feature-scoped ADR → exit 2 / BLOCK / finding", scenario_adr_placement_negative),
]


def main() -> int:
    failed: list[tuple[str, str]] = []
    for name, fn in SCENARIOS:
        try:
            fn()
            print(f"  PASS  {name}", file=sys.stderr)
        except SmokeFailure as exc:
            failed.append((name, str(exc)))
            print(f"  FAIL  {name}: {exc}", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001 — smoke test should keep going
            failed.append((name, f"unexpected error: {exc}"))
            print(f"  ERROR {name}: {exc}", file=sys.stderr)
    print(
        f"\nSmoke test: {len(SCENARIOS) - len(failed)} pass / {len(failed)} fail",
        file=sys.stderr,
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
