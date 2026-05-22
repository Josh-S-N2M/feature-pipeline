#!/usr/bin/env python3
"""
test_audit_project.py — Integration tests for the project walker.

Tests that audit_project.py:
  - Discovers all primitives correctly
  - Dispatches to each sub-skill auditor
  - Aggregates findings
  - Runs cross-file checks
  - Computes a verdict
  - Writes a Markdown report

Run:
    python3 tests/test_audit_project.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

WALKER = Path(__file__).resolve().parent.parent / "scripts" / "audit_project.py"


def run_walker(project_root: Path, *flags: str) -> dict:
    """Run the walker and return the JSON summary."""
    r = subprocess.run(
        [sys.executable, str(WALKER), str(project_root), *flags],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0:
        raise RuntimeError(f"walker failed (rc={r.returncode}): {r.stderr}\nstdout: {r.stdout}")
    return json.loads(r.stdout)


def test_empty_project_passes():
    """A project with only an empty .claude/ should score 100."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".claude").mkdir()
        result = run_walker(root)
        v = result["verdict"]
        assert v["score"] == 100, f"expected 100, got {v['score']}: {v}"
        assert v["verdict"] == "PASS"
        print("  Empty project: 100 PASS (OK)")


def test_clean_project_passes():
    """A project with minimal valid config should pass."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".claude").mkdir()
        (root / "CLAUDE.md").write_text("# Project\n\nUse pytest.\n")
        result = run_walker(root)
        v = result["verdict"]
        assert v["score"] >= 95, f"expected ≥95, got {v['score']}: {v}"
        assert v["verdict"] in ("PASS", "PASS-WITH-MINOR-FIXES")
        print(f"  Clean project: {v['score']} {v['verdict']} (OK)")


def test_bad_project_fails():
    """A project with several BLOCKERs should fail."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".claude" / "rules").mkdir(parents=True)
        # Rule glob matches nothing
        (root / ".claude" / "rules" / "rust.md").write_text(
            "---\npaths:\n  - '**/*.rs'\n---\n# Rust\n"
        )
        # Missing hook script
        settings = {
            "hooks": {
                "PreToolUse": [{
                    "matcher": "Bash",
                    "hooks": [{"type": "command", "command": ".claude/hooks/missing.sh"}]
                }]
            }
        }
        (root / ".claude" / "settings.json").write_text(json.dumps(settings))
        # Local settings without gitignore
        (root / ".claude" / "settings.local.json").write_text("{}")
        (root / ".gitignore").write_text("")
        result = run_walker(root)
        v = result["verdict"]
        # We expect at least NEEDS-WORK
        assert v["score"] < 95, f"expected <95, got {v['score']}: {v}"
        # And we expect cross-file findings (X1, X7, X10)
        assert result["cross_file_findings"] >= 2, f"expected ≥2 cross-file, got {result['cross_file_findings']}"
        print(f"  Bad project: {v['score']} {v['verdict']} ({result['cross_file_findings']} cross-file findings) (OK)")


def test_walker_writes_report():
    """The walker must write a Markdown report to the expected path."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".claude").mkdir()
        result = run_walker(root)
        report_path = Path(result["report_path"])
        assert report_path.exists(), f"report not written: {report_path}"
        content = report_path.read_text()
        assert "Claude Code Configuration Audit" in content
        assert "Verdict:" in content
        print(f"  Report written: {report_path.name} (OK)")


def test_walker_writes_json_sidecar():
    """With --json, the walker writes a JSON sidecar."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".claude").mkdir()
        result = run_walker(root, "--json")
        assert "json_path" in result
        json_path = Path(result["json_path"])
        assert json_path.exists()
        data = json.loads(json_path.read_text())
        assert "summary" in data
        assert "per_primitive" in data
        assert "cross_file" in data
        print(f"  JSON sidecar: {json_path.name} (OK)")


def test_walker_discovers_skills():
    """The walker discovers skill directories under .claude/skills/."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".claude" / "skills" / "skill-a").mkdir(parents=True)
        (root / ".claude" / "skills" / "skill-a" / "SKILL.md").write_text(
            "---\nname: skill-a\ndescription: A skill. Use when foo.\n---\n# Body\n"
        )
        (root / ".claude" / "skills" / "skill-b").mkdir(parents=True)
        (root / ".claude" / "skills" / "skill-b" / "SKILL.md").write_text(
            "---\nname: skill-b\ndescription: Another skill. Use when bar.\n---\n# Body\n"
        )
        result = run_walker(root)
        assert result["primitives_audited"]["skills"] == 2, \
            f"expected 2 skills, got {result['primitives_audited']['skills']}"
        print(f"  Discovered 2 skills (OK)")


def test_walker_discovers_subagents():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".claude" / "agents").mkdir(parents=True)
        (root / ".claude" / "agents" / "a.md").write_text(
            "---\nname: a\ndescription: x. Use when y.\ntools: Read\n---\nbody\n"
        )
        result = run_walker(root)
        assert result["primitives_audited"]["subagents"] == 1
        print(f"  Discovered 1 subagent (OK)")


def test_walker_discovers_hooks_and_settings():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / ".claude").mkdir()
        settings = {"hooks": {"PreToolUse": [{"hooks": [{"type": "command", "command": "echo"}]}]}}
        (root / ".claude" / "settings.json").write_text(json.dumps(settings))
        result = run_walker(root)
        assert result["primitives_audited"]["hooks_configs"] == 1
        assert result["primitives_audited"]["settings_files"] == 1
        print(f"  Discovered hooks + settings (OK)")


TESTS = [
    test_empty_project_passes,
    test_clean_project_passes,
    test_bad_project_fails,
    test_walker_writes_report,
    test_walker_writes_json_sidecar,
    test_walker_discovers_skills,
    test_walker_discovers_subagents,
    test_walker_discovers_hooks_and_settings,
]


def main() -> int:
    print("Running project-walker integration tests...")
    passed = 0
    failed = 0
    for t in TESTS:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {t.__name__}: {e}")
            failed += 1

    print(f"\nSummary: {passed}/{len(TESTS)} tests passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
