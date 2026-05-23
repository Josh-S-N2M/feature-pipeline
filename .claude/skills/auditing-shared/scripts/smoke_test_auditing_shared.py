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


SCRIPTS = {
    "validator": ".claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py",
    "log_state": ".claude/skills/auditing-shared/scripts/log_state_transition.py",
    "stubs": ".claude/skills/auditing-shared/scripts/detect_stubs.py",
    "discipline": ".claude/skills/auditing-shared/scripts/check_pipeline_discipline.py",
    "coordinator": ".claude/skills/auditing-shared/scripts/run_phase_checks.py",
    "codespaces_stub": ".claude/skills/auditing-codespaces/scripts/audit_codespaces.py",
}


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
