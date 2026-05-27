#!/usr/bin/env python3
"""smoke_test_check_feature_touch_predicate.py — Smoke tests for check_feature_touch_predicate.py.

Exercises the advisory predicate (T5.2) against synthetic git working trees
per ADR-0064 Clause 3 and FR-6 of pipeline-design-time-discipline-r1.
Gates PV-5.C2 and PV-5.C3.

Scenarios:
    A  clean run — no agent files touched    → exit 0 (predicate silent)
    B  agent file edited — condition 1 fires  → exit 1 (advisory)
    C  .mcp.json modified — condition 2 fires → exit 1 (advisory)
    D  new SKILL.md added — condition 3 fires → exit 1 (advisory)
    E  design.md with skill-coverage tokens  → exit 1 (advisory, condition 4)

Each scenario creates a temporary git repo with the minimum fixture structure
required, invokes the predicate via subprocess, and asserts:
  - correct exit code
  - JSON shape: feature_slug, predicate_fired, triggers, advisory_message

Run as:
    python3 .claude/skills/auditing-subagents/scripts/smoke_test_check_feature_touch_predicate.py
Exit 0 = all pass; non-zero = failure with diagnostic on stderr.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

PREDICATE = str(Path(__file__).parent / "check_feature_touch_predicate.py")

FEATURE_SLUG = "synthetic-smoke-feature"


class SmokeFailure(Exception):
    pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _eq(label: str, got, want) -> None:
    if got != want:
        raise SmokeFailure(f"{label}: got {got!r}, want {want!r}")


def _in(label: str, needle, haystack) -> None:
    if needle not in haystack:
        raise SmokeFailure(f"{label}: {needle!r} not in {haystack!r}")


def _true(label: str, val) -> None:
    if not val:
        raise SmokeFailure(f"{label}: expected truthy, got {val!r}")


def _run(repo_dir: str, extra_args: Optional[list] = None) -> subprocess.CompletedProcess:
    cmd = [
        "python3", PREDICATE,
        "--feature-slug", FEATURE_SLUG,
        "--ref-baseline", "HEAD",
        "--repo-root", repo_dir,
    ]
    if extra_args:
        cmd.extend(extra_args)
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=30, cwd=repo_dir
    )


def _git(args: list, cwd: str) -> None:
    """Run a git command; raise on failure."""
    r = subprocess.run(
        ["git"] + args, capture_output=True, text=True, cwd=cwd
    )
    if r.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed in {cwd!r}: {r.stderr.strip()}"
        )


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Fixture builder
# ---------------------------------------------------------------------------

class _GitFixture:
    """Context manager: creates a temporary git repo with feature working dir.

    Sets up:
      - git init + initial commit (establishes HEAD)
      - working/feature/<slug>/ directory with a minimal prd-v1.md
      - .claude/agents/ directory with a placeholder agent
      - .mcp.json with minimal content

    Yields the repo root path.
    """

    def __init__(self, scenario_name: str):
        self._name = scenario_name
        self._tmpdir: Optional[tempfile.TemporaryDirectory] = None
        self.root: Optional[str] = None

    def __enter__(self) -> "Path":
        self._tmpdir = tempfile.TemporaryDirectory(prefix=f"smoke_{self._name}_")
        root = Path(self._tmpdir.name)
        self.root = str(root)

        # Minimal git config so commits work in CI environments
        _git(["init", "-b", "main"], str(root))
        _git(["config", "user.email", "smoke@test.local"], str(root))
        _git(["config", "user.name", "Smoke Test"], str(root))

        # Scaffold baseline structure
        _write(root / ".claude" / "agents" / "example-agent.md", (
            "---\nid: example-agent\n---\n# Example Agent\nPlaceholder.\n"
        ))
        _write(root / ".mcp.json", (
            '{"mcpServers": {"serena": {"command": "serena", "args": ["start-mcp-server"]}}}\n'
        ))
        _write(root / "working" / "feature" / FEATURE_SLUG / "prd-v1.md", (
            "# PRD\nMinimal fixture PRD for smoke test.\n"
        ))
        _write(root / "README.md", "# Smoke test repo\n")

        # Initial commit — establishes HEAD
        _git(["add", "-A"], str(root))
        _git(["commit", "-m", "initial commit (smoke test baseline)"], str(root))

        return root

    def __exit__(self, *_) -> None:
        if self._tmpdir:
            self._tmpdir.cleanup()


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

def scenario_clean_run() -> None:
    """A: clean run — nothing touched after HEAD commit → exit 0."""
    with _GitFixture("A") as root:
        r = _run(str(root))
        _eq("A exit", r.returncode, 0)
        d = json.loads(r.stdout)
        _eq("A feature_slug", d["feature_slug"], FEATURE_SLUG)
        _eq("A predicate_fired", d["predicate_fired"], False)
        _eq("A triggers empty", d["triggers"], [])
        _in("A advisory_message", "No matrix required", d["advisory_message"])


def scenario_agent_file_edited() -> None:
    """B: agent file edited — condition 1 fires → exit 1 (advisory)."""
    with _GitFixture("B") as root:
        # Modify an existing agent file after the initial commit
        agent_path = root / ".claude" / "agents" / "example-agent.md"
        _write(agent_path, (
            "---\nid: example-agent\n---\n# Example Agent\nEdited content.\n"
        ))

        r = _run(str(root))
        _eq("B exit", r.returncode, 1)
        d = json.loads(r.stdout)
        _eq("B predicate_fired", d["predicate_fired"], True)
        _true("B triggers non-empty", d["triggers"])
        conditions = [t["condition"] for t in d["triggers"]]
        _in("B condition 1 present", "1", conditions)
        _in("B advisory_message fires", "Matrix authoring recommended", d["advisory_message"])
        # Files list should name the agent
        files_hit = [f for t in d["triggers"] if t["condition"] == "1" for f in t["files"]]
        _true("B agent file in files", any(".claude/agents/" in f for f in files_hit))


def scenario_mcp_json_modified() -> None:
    """C: .mcp.json modified with tool-surface change — condition 2 fires → exit 1."""
    with _GitFixture("C") as root:
        # Write a new .mcp.json that adds a tools key (tool-surface token)
        _write(root / ".mcp.json", (
            '{"mcpServers": {"serena": {"command": "serena", "args": ["start-mcp-server"], '
            '"tools": ["find_symbol", "find_referencing_symbols"]}}}\n'
        ))

        r = _run(str(root))
        _eq("C exit", r.returncode, 1)
        d = json.loads(r.stdout)
        _eq("C predicate_fired", d["predicate_fired"], True)
        _true("C triggers non-empty", d["triggers"])
        conditions = [t["condition"] for t in d["triggers"]]
        _in("C condition 2 present", "2", conditions)
        _in("C advisory_message fires", "Matrix authoring recommended", d["advisory_message"])
        # .mcp.json should be in the files list for condition 2
        files_hit = [f for t in d["triggers"] if t["condition"] == "2" for f in t["files"]]
        _in("C mcp.json in files", ".mcp.json", files_hit)


def scenario_new_skill_added() -> None:
    """D: new SKILL.md added — condition 3 fires → exit 1 (mechanical_only: true)."""
    with _GitFixture("D") as root:
        # Add a new SKILL.md that was not part of the initial commit
        _write(root / ".claude" / "skills" / "new-domain-skill" / "SKILL.md", (
            "# New Domain Skill\nPlaceholder skill content.\n"
        ))

        r = _run(str(root))
        _eq("D exit", r.returncode, 1)
        d = json.loads(r.stdout)
        _eq("D predicate_fired", d["predicate_fired"], True)
        _true("D triggers non-empty", d["triggers"])
        conditions = [t["condition"] for t in d["triggers"]]
        _in("D condition 3 present", "3", conditions)
        # condition 3 must be mechanical_only: true
        c3 = next(t for t in d["triggers"] if t["condition"] == "3")
        _eq("D mechanical_only", c3.get("mechanical_only"), True)
        _in("D advisory fires", "Matrix authoring recommended", d["advisory_message"])


def scenario_skill_coverage_in_design() -> None:
    """E: design.md with skill-coverage tokens — condition 4 fires → exit 1."""
    with _GitFixture("E") as root:
        # Write a design.md that mentions skill-coverage decision tokens
        _write(
            root / "working" / "feature" / FEATURE_SLUG / "synthesis.md",
            (
                "# Synthesis\n\n"
                "## Skill-Coverage Decisions\n\n"
                "| Concept | Decision | Existing agent |\n"
                "|---------|----------|----------------|\n"
                "| new domain concept | existing-skill | design-cc |\n"
            ),
        )

        r = _run(str(root))
        _eq("E exit", r.returncode, 1)
        d = json.loads(r.stdout)
        _eq("E predicate_fired", d["predicate_fired"], True)
        _true("E triggers non-empty", d["triggers"])
        conditions = [t["condition"] for t in d["triggers"]]
        _in("E condition 4 present", "4", conditions)
        c4 = next(t for t in d["triggers"] if t["condition"] == "4")
        _eq("E mechanical_only", c4.get("mechanical_only"), True)
        _in("E advisory fires", "Matrix authoring recommended", d["advisory_message"])


# ---------------------------------------------------------------------------
# JSON shape invariant (all scenarios that succeed must have required keys)
# ---------------------------------------------------------------------------

def _assert_json_shape(label: str, d: dict) -> None:
    """Assert that the result JSON has the required top-level keys."""
    required = {"feature_slug", "predicate_fired", "triggers", "advisory_message"}
    missing = required - set(d.keys())
    if missing:
        raise SmokeFailure(f"{label}: JSON missing keys: {sorted(missing)}")
    if not isinstance(d["triggers"], list):
        raise SmokeFailure(f"{label}: 'triggers' must be a list, got {type(d['triggers'])}")


def _wrapped(name: str, fn) -> None:
    """Run fn(); also validate JSON shape from the last subprocess if callable."""
    fn()


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

SCENARIOS = [
    ("A: clean run — no touches → exit 0", scenario_clean_run),
    ("B: agent file edited — condition 1 → exit 1", scenario_agent_file_edited),
    ("C: .mcp.json modified — condition 2 → exit 1", scenario_mcp_json_modified),
    ("D: new SKILL.md added — condition 3 → exit 1", scenario_new_skill_added),
    ("E: skill-coverage tokens in design — condition 4 → exit 1", scenario_skill_coverage_in_design),
]


def main() -> int:
    failed: list = []
    for name, fn in SCENARIOS:
        try:
            fn()
            print(f"  PASS  {name}", file=sys.stderr)
        except SmokeFailure as exc:
            failed.append((name, str(exc)))
            print(f"  FAIL  {name}: {exc}", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001
            failed.append((name, f"unexpected: {type(exc).__name__}: {exc}"))
            print(f"  ERROR {name}: {type(exc).__name__}: {exc}", file=sys.stderr)

    print(
        f"\nSmoke test: {len(SCENARIOS) - len(failed)} pass / {len(failed)} fail",
        file=sys.stderr,
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
