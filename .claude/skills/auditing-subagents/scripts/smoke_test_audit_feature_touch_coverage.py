#!/usr/bin/env python3
"""smoke_test_audit_feature_touch_coverage.py — Smoke tests for audit_feature_touch_coverage.py.

Exercises the SA-14 hard gate against five synthetic fixture scenarios per
ADR-0064 Clause 2 + FR-10 of pipeline-design-time-discipline-r1.
Gates PV-7.C1 and PV-7.C2.

Scenarios:
    A  predicate did NOT fire → not_applicable + PASS + exit 0
    B  predicate fired + matrix present + compliant → clean + PASS + exit 0
    C  predicate fired + matrix missing → findings + FAIL + exit 1 (BLOCKER)
    D  predicate fired + matrix present + bare-no-change cell → findings + FAIL + exit 1 (MAJOR)
    E  predicate fired + matrix present + row count mismatch → findings + FAIL + exit 1 (MAJOR)
    F  predicate fired + matrix present with MULTIPLE tables (preamble table before the canonical
       5-column matrix) → parser finds canonical table → clean + PASS + exit 0

Each scenario constructs a synthetic fixture directory, writes a predicate JSON
stub, and invokes audit_feature_touch_coverage.py via subprocess with
--predicate-output pointing at the stub.  No real git repo required; all
predicate output is supplied as a pre-computed JSON file.

Run as:
    python3 .claude/skills/auditing-subagents/scripts/smoke_test_audit_feature_touch_coverage.py
Exit 0 = all five scenarios pass; non-zero = at least one failure (diagnostic on stderr).

References:
  ADR-0064 — Agent-Roster Impact Matrix Contract (Clause 2)
  FR-10    — pipeline-design-time-discipline-r1 PRD (SA-14)
  ADR-0061 — Severity vocabulary bridge (BLOCKER / MAJOR)
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_SCRIPTS_DIR = Path(__file__).parent.resolve()
AUDIT_SCRIPT = str(_SCRIPTS_DIR / "audit_feature_touch_coverage.py")
FEATURE_SLUG = "synthetic-sa14-fixture"


# ---------------------------------------------------------------------------
# Assertion helpers
# ---------------------------------------------------------------------------

class SmokeFailure(Exception):
    pass


def _eq(label: str, got, want) -> None:
    if got != want:
        raise SmokeFailure(f"{label}: got {got!r}, want {want!r}")


def _contains(label: str, needle: str, haystack: str) -> None:
    if needle not in haystack:
        raise SmokeFailure(f"{label}: {needle!r} not found in output")


def _true(label: str, val) -> None:
    if not val:
        raise SmokeFailure(f"{label}: expected truthy, got {val!r}")


def _false(label: str, val) -> None:
    if val:
        raise SmokeFailure(f"{label}: expected falsy, got {val!r}")


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------

def _write_predicate_stub(
    fixture_dir: Path,
    predicate_fired: bool,
    feature_slug: str = FEATURE_SLUG,
) -> Path:
    """Write a synthetic predicate JSON output file; return its path."""
    stub = {
        "feature_slug": feature_slug,
        "predicate_fired": predicate_fired,
        "triggers": (
            [
                {
                    "condition": "1",
                    "description": "synthetic trigger for smoke test",
                    "evidence": "1 agent file touched",
                    "files": [".claude/agents/design-cc.md"],
                    "mechanical_only": False,
                }
            ]
            if predicate_fired
            else []
        ),
        "advisory_message": (
            "Matrix authoring recommended — feature touches agent surface"
            if predicate_fired
            else "No matrix required — clean run"
        ),
        "ref_baseline": "HEAD",
        "changed_files_scanned": 3,
        "elapsed_ms": 12,
    }
    stub_path = fixture_dir / "predicate_output.json"
    stub_path.write_text(json.dumps(stub, indent=2), encoding="utf-8")
    return stub_path


def _make_repo_skeleton(tmp: Path, n_agents: int) -> Path:
    """Create a minimal repo skeleton with n_agents fake agent files.

    Returns the repo root path.
    """
    repo = tmp / "repo"
    agents_dir = repo / ".claude" / "agents"
    agents_dir.mkdir(parents=True)

    for i in range(n_agents):
        agent_file = agents_dir / f"agent-{i:02d}.md"
        agent_file.write_text(
            f"---\nid: agent-{i:02d}\n---\n# Agent {i}\n",
            encoding="utf-8",
        )

    # Create the feature directory
    feature_dir = repo / "working" / "feature" / FEATURE_SLUG
    feature_dir.mkdir(parents=True)

    return repo


def _write_matrix_multi_table(feature_dir: Path, rows: list) -> None:
    """Write a matrix file containing a preamble table followed by the canonical matrix.

    This reproduces the exact structure of the T8.1 eat-own-dogfood matrix:
    a Trigger-Evidence Record table (different columns) appears BEFORE the
    canonical 5-column matrix, separated by a markdown horizontal rule.
    The parser must skip the preamble table and identify the canonical one.
    """
    # Preamble: 4-row, 4-column trigger-evidence table (no canonical columns)
    preamble_lines = [
        "## Trigger-Evidence Record",
        "",
        "| Condition | Description | Fired? | Evidence |",
        "| --- | --- | --- | --- |",
        "| **1** | Agent files modified | **YES** | 1 agent file touched |",
        "| **2** | MCP server changed | **NO** | No .mcp.json change |",
        "| **3** | New skill created | **NO** | No new SKILL.md |",
        "| **4** | New domain concept | **NO** | No new concept named |",
        "",
        "---",
        "",
        "## The Matrix",
        "",
    ]

    matrix_lines = [
        "| Agent | Tools | Skills | Model | Effort | Prompt Body |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        while len(r) < 6:
            r = list(r) + [""]
        matrix_lines.append(
            f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |"
        )

    content = "\n".join(preamble_lines + matrix_lines) + "\n"
    (feature_dir / "agent-roster-impact-matrix.md").write_text(
        content, encoding="utf-8"
    )


def _write_matrix(feature_dir: Path, rows: list) -> None:
    """Write a synthetic agent-roster-impact-matrix.md to feature_dir.

    *rows* is a list of 5-cell tuples:
        (agent_name, tools_cell, skills_cell, model_cell, effort_cell, prompt_body_cell)
    Each cell is written verbatim.
    """
    lines = [
        "# Agent Roster Impact Matrix",
        "",
        "| Agent | Tools | Skills | Model | Effort | Prompt Body |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        # r may be 5 or 6 elements; pad if needed
        while len(r) < 6:
            r = list(r) + [""]
        lines.append(
            f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |"
        )
    (feature_dir / "agent-roster-impact-matrix.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def _run_audit(
    repo_root: str,
    predicate_stub_path: str,
    feature_slug: str = FEATURE_SLUG,
) -> subprocess.CompletedProcess:
    """Invoke audit_feature_touch_coverage.py with synthetic fixtures."""
    cmd = [
        sys.executable,
        AUDIT_SCRIPT,
        "--feature-slug", feature_slug,
        "--predicate-output", predicate_stub_path,
        "--repo-root", repo_root,
    ]
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=30, cwd=repo_root
    )


# ---------------------------------------------------------------------------
# Scenario implementations
# ---------------------------------------------------------------------------

def _scenario_a(tmp: Path) -> str:
    """A: predicate did NOT fire → not_applicable + PASS + exit 0."""
    repo = _make_repo_skeleton(tmp, n_agents=3)
    feature_dir = repo / "working" / "feature" / FEATURE_SLUG
    stub_path = _write_predicate_stub(feature_dir, predicate_fired=False)

    proc = _run_audit(str(repo), str(stub_path))
    _eq("A.exit_code", proc.returncode, 0)

    data = json.loads(proc.stdout)
    _eq("A.sa14_status", data["sa14_status"], "not_applicable")
    _eq("A.verdict", data["verdict"], "PASS")
    _false("A.findings_nonempty", data["findings"])
    return "A passed — predicate silent → not_applicable PASS"


def _scenario_b(tmp: Path) -> str:
    """B: predicate fired + matrix present + fully compliant → clean + PASS + exit 0."""
    n_agents = 3
    repo = _make_repo_skeleton(tmp, n_agents=n_agents)
    feature_dir = repo / "working" / "feature" / FEATURE_SLUG
    stub_path = _write_predicate_stub(feature_dir, predicate_fired=True)

    # Write a compliant matrix: 3 agents × 5 cells (tools, skills, model, effort, prompt body)
    # Column 0 = agent name (not one of the 5 required dimensions — decorative)
    rows = [
        [
            f"agent-{i:02d}",
            "no-change — inspected tool list; no MCP server in scope for this feature",
            "no-change — agent prompt does not reference any new skill introduced this run",
            "no-change — model remains claude-sonnet-4-6 per current roster spec",
            "no-change — effort level unchanged; task complexity unchanged",
            "no-change — prompt body not touched; agent purpose unaffected by this feature",
        ]
        for i in range(n_agents)
    ]
    _write_matrix(feature_dir, rows)

    proc = _run_audit(str(repo), str(stub_path))
    _eq("B.exit_code", proc.returncode, 0)

    data = json.loads(proc.stdout)
    _eq("B.sa14_status", data["sa14_status"], "clean")
    _eq("B.verdict", data["verdict"], "PASS")
    _false("B.findings_nonempty", data["findings"])
    _eq("B.row_count_observed", data["row_count_observed"], n_agents)
    _eq("B.agent_count_expected", data["agent_count_expected"], n_agents)
    return "B passed — predicate fired + compliant matrix → clean PASS"


def _scenario_c(tmp: Path) -> str:
    """C: predicate fired + matrix missing → findings + FAIL + exit 1 (BLOCKER)."""
    repo = _make_repo_skeleton(tmp, n_agents=3)
    feature_dir = repo / "working" / "feature" / FEATURE_SLUG
    stub_path = _write_predicate_stub(feature_dir, predicate_fired=True)

    # Deliberately do NOT write any matrix file

    proc = _run_audit(str(repo), str(stub_path))
    _eq("C.exit_code", proc.returncode, 1)

    data = json.loads(proc.stdout)
    _eq("C.sa14_status", data["sa14_status"], "findings")
    _eq("C.verdict", data["verdict"], "FAIL")
    _true("C.has_findings", data["findings"])

    blocker_found = any(
        f.get("severity") == "BLOCKER" and "SA-14.matrix_missing" in f.get("rule", "")
        for f in data["findings"]
    )
    _true("C.blocker_finding_present", blocker_found)
    return "C passed — predicate fired + matrix absent → BLOCKER FAIL"


def _scenario_d(tmp: Path) -> str:
    """D: predicate fired + matrix present + bare no-change cell → findings + FAIL + exit 1 (MAJOR)."""
    n_agents = 3
    repo = _make_repo_skeleton(tmp, n_agents=n_agents)
    feature_dir = repo / "working" / "feature" / FEATURE_SLUG
    stub_path = _write_predicate_stub(feature_dir, predicate_fired=True)

    # Write a matrix with one bare "no-change" cell (agent-01, tools column)
    rows = [
        [
            "agent-00",
            "no-change — inspected tool list; no MCP server in scope for this feature",
            "no-change — agent prompt does not reference any new skill introduced this run",
            "no-change — model remains claude-sonnet-4-6",
            "no-change — effort level unchanged",
            "no-change — prompt body not touched",
        ],
        [
            "agent-01",
            "no-change",  # <-- bare — structurally insufficient per ADR-0064 Clause 2
            "no-change — agent prompt does not reference any new skill introduced this run",
            "no-change — model remains claude-sonnet-4-6",
            "no-change — effort level unchanged",
            "no-change — prompt body not touched",
        ],
        [
            "agent-02",
            "no-change — inspected tool list; no MCP server in scope for this feature",
            "no-change — agent prompt does not reference any new skill introduced this run",
            "no-change — model remains claude-sonnet-4-6",
            "no-change — effort level unchanged",
            "no-change — prompt body not touched",
        ],
    ]
    _write_matrix(feature_dir, rows)

    proc = _run_audit(str(repo), str(stub_path))
    _eq("D.exit_code", proc.returncode, 1)

    data = json.loads(proc.stdout)
    _eq("D.sa14_status", data["sa14_status"], "findings")
    _eq("D.verdict", data["verdict"], "FAIL")
    _true("D.has_findings", data["findings"])

    cell_finding = any(
        "SA-14.cell_bare_no_change" in f.get("rule", "")
        for f in data["findings"]
    )
    _true("D.cell_bare_finding_present", cell_finding)

    major_found = any(
        f.get("severity") == "MAJOR" for f in data["findings"]
    )
    _true("D.major_severity_present", major_found)
    return "D passed — bare no-change cell → MAJOR cell finding FAIL"


def _scenario_e(tmp: Path) -> str:
    """E: predicate fired + matrix present + row count mismatch → findings + FAIL + exit 1 (MAJOR)."""
    n_agents = 5  # repo has 5 agents
    n_rows_in_matrix = 3  # matrix only has 3 rows — MISMATCH
    repo = _make_repo_skeleton(tmp, n_agents=n_agents)
    feature_dir = repo / "working" / "feature" / FEATURE_SLUG
    stub_path = _write_predicate_stub(feature_dir, predicate_fired=True)

    # Write a matrix with only 3 rows (should be 5)
    rows = [
        [
            f"agent-{i:02d}",
            "no-change — inspected tool list; no MCP server in scope for this feature",
            "no-change — agent prompt does not reference any new skill introduced this run",
            "no-change — model remains claude-sonnet-4-6",
            "no-change — effort level unchanged",
            "no-change — prompt body not touched",
        ]
        for i in range(n_rows_in_matrix)
    ]
    _write_matrix(feature_dir, rows)

    proc = _run_audit(str(repo), str(stub_path))
    _eq("E.exit_code", proc.returncode, 1)

    data = json.loads(proc.stdout)
    _eq("E.sa14_status", data["sa14_status"], "findings")
    _eq("E.verdict", data["verdict"], "FAIL")
    _true("E.has_findings", data["findings"])

    row_count_finding = any(
        "SA-14.row_count_mismatch" in f.get("rule", "")
        for f in data["findings"]
    )
    _true("E.row_count_finding_present", row_count_finding)

    _eq("E.row_count_observed", data["row_count_observed"], n_rows_in_matrix)
    _eq("E.agent_count_expected", data["agent_count_expected"], n_agents)

    major_found = any(
        f.get("severity") == "MAJOR" for f in data["findings"]
    )
    _true("E.major_severity_present", major_found)
    return "E passed — row count mismatch (3 vs 5 agents) → MAJOR row-count finding FAIL"


def _scenario_f(tmp: Path) -> str:
    """F: multi-table matrix file — preamble table before canonical matrix → clean PASS.

    Reproduces the T8.1 eat-own-dogfood regression: a 4-row Trigger-Evidence
    Record table (wrong columns) appears before the 37-row canonical matrix,
    separated by a markdown horizontal rule.  The parser must skip the preamble
    table and return the canonical 5-column table.
    """
    n_agents = 3
    repo = _make_repo_skeleton(tmp, n_agents=n_agents)
    feature_dir = repo / "working" / "feature" / FEATURE_SLUG
    stub_path = _write_predicate_stub(feature_dir, predicate_fired=True)

    rows = [
        [
            f"agent-{i:02d}",
            "no-change — inspected tool list; no MCP server in scope for this feature",
            "no-change — agent prompt does not reference any new skill introduced this run",
            "no-change — model remains claude-sonnet-4-6 per current roster spec",
            "no-change — effort level unchanged; task complexity unchanged",
            "no-change — prompt body not touched; agent purpose unaffected by this feature",
        ]
        for i in range(n_agents)
    ]
    # Write a multi-table file: preamble table + separator + canonical matrix
    _write_matrix_multi_table(feature_dir, rows)

    proc = _run_audit(str(repo), str(stub_path))
    _eq("F.exit_code", proc.returncode, 0)

    data = json.loads(proc.stdout)
    _eq("F.sa14_status", data["sa14_status"], "clean")
    _eq("F.verdict", data["verdict"], "PASS")
    _false("F.findings_nonempty", data["findings"])
    _eq("F.row_count_observed", data["row_count_observed"], n_agents)
    return (
        "F passed — multi-table matrix (preamble table + canonical matrix) "
        "→ parser finds canonical table → clean PASS"
    )


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

SCENARIOS = [
    ("A", _scenario_a),
    ("B", _scenario_b),
    ("C", _scenario_c),
    ("D", _scenario_d),
    ("E", _scenario_e),
    ("F", _scenario_f),
]


def main() -> int:
    passed = 0
    failed = 0

    for label, scenario_fn in SCENARIOS:
        with tempfile.TemporaryDirectory(prefix=f"sa14-smoke-{label}-") as tmp_str:
            tmp = Path(tmp_str)
            try:
                msg = scenario_fn(tmp)
                print(f"[PASS] {msg}", flush=True)
                passed += 1
            except SmokeFailure as exc:
                print(f"[FAIL] Scenario {label}: {exc}", file=sys.stderr, flush=True)
                failed += 1
            except Exception as exc:  # noqa: BLE001
                print(
                    f"[ERROR] Scenario {label}: unexpected exception: "
                    f"{type(exc).__name__}: {exc}",
                    file=sys.stderr,
                    flush=True,
                )
                failed += 1

    total = passed + failed
    print(f"\n{passed}/{total} scenarios passed.", flush=True)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
