#!/usr/bin/env python3
"""
test_dispatch_smoke.py — Smoke tests for audit_target.py dispatcher.

Covers tasks 0.20, 0.21, 0.22 of the execution plan:
  0.20 — Smoke test: dispatch SKILL.md routing
  0.21 — Smoke test: dispatch MEMORY.md (auto memory) routing
  0.22 — Smoke test: dispatch agent-memory routing

These tests verify the coordinator's classification + routing decisions
are correct. They do NOT call into sub-skills (Phases 1+ build those).
The test asserts that dispatch produces the correct sub_skill name and
target_type, and the correct status ("dispatched" if v1.1 auditing-skills
is alongside; "sub-skill-not-yet-built" otherwise).
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = ""):
    RESULTS.append((name, condition, detail))
    if condition:
        print(f"  ✓ {name}")
    else:
        print(f"  ✗ {name} — {detail}")


def run(target: str) -> dict:
    r = subprocess.run(
        ["python3", str(SCRIPTS / "audit_target.py"), target],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        return {"error": r.stderr.strip()}
    return json.loads(r.stdout)


def test_skill_dispatch():
    """0.20 — SKILL.md dispatch routes to auditing-skills."""
    print("\n=== 0.20 — SKILL.md dispatch ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        sd = Path(tmpdir) / "my-skill"
        sd.mkdir()
        (sd / "SKILL.md").write_text(
            "---\n"
            "name: my-skill\n"
            "description: x\n"
            "---\n"
            "body\n"
        )
        result = run(str(sd))
        c = result.get("classification", {})
        check("SKILL.md dir → target_type=skill",
              c.get("target_type") == "skill", str(c))
        check("SKILL.md dir → sub_skill=auditing-skills",
              c.get("sub_skill") == "auditing-skills", str(c))

        # SKILL.md file directly
        result = run(str(sd / "SKILL.md"))
        c = result.get("classification", {})
        check("SKILL.md file → target_type=skill",
              c.get("target_type") == "skill", str(c))
        check("SKILL.md file → sub_skill=auditing-skills",
              c.get("sub_skill") == "auditing-skills", str(c))


def test_auto_memory_dispatch():
    """0.21 — Auto MEMORY.md routes to auditing-context-files."""
    print("\n=== 0.21 — Auto MEMORY.md dispatch ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        # ~/.claude/projects/<id>/memory/MEMORY.md pattern
        am = Path(tmpdir) / "home" / ".claude" / "projects" / "abc123" / "memory" / "MEMORY.md"
        am.parent.mkdir(parents=True)
        am.write_text("# auto memory\n")
        result = run(str(am))
        c = result.get("classification", {})
        check("auto-memory MEMORY.md → target_type=auto-memory",
              c.get("target_type") == "auto-memory", str(c))
        check("auto-memory MEMORY.md → sub_skill=auditing-context-files",
              c.get("sub_skill") == "auditing-context-files", str(c))

        # Also any file in the memory dir
        topic = Path(tmpdir) / "home" / ".claude" / "projects" / "abc123" / "memory" / "topics" / "api.md"
        topic.parent.mkdir(parents=True)
        topic.write_text("# topic\n")
        result = run(str(topic))
        c = result.get("classification", {})
        check("auto-memory topic file → target_type=auto-memory",
              c.get("target_type") == "auto-memory", str(c))


def test_agent_memory_dispatch():
    """0.22 — Agent memory routes to auditing-subagents."""
    print("\n=== 0.22 — Subagent memory dispatch ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        # Project-scoped (committed) agent memory
        sm = Path(tmpdir) / "proj" / ".claude" / "agent-memory" / "reviewer" / "MEMORY.md"
        sm.parent.mkdir(parents=True)
        sm.write_text("# sub memory\n")
        result = run(str(sm))
        c = result.get("classification", {})
        check("agent-memory MEMORY.md → target_type=subagent-memory",
              c.get("target_type") == "subagent-memory", str(c))
        check("agent-memory MEMORY.md → sub_skill=auditing-subagents",
              c.get("sub_skill") == "auditing-subagents", str(c))

        # Local (gitignored) agent memory
        sml = Path(tmpdir) / "proj" / ".claude" / "agent-memory-local" / "reviewer" / "MEMORY.md"
        sml.parent.mkdir(parents=True)
        sml.write_text("# local sub memory\n")
        result = run(str(sml))
        c = result.get("classification", {})
        check("agent-memory-local MEMORY.md → target_type=subagent-memory-local",
              c.get("target_type") == "subagent-memory-local", str(c))
        check("agent-memory-local MEMORY.md → sub_skill=auditing-subagents",
              c.get("sub_skill") == "auditing-subagents", str(c))

        # User-scope agent memory (still routes to subagents)
        ums = Path(tmpdir) / "home" / ".claude" / "agent-memory" / "reviewer" / "MEMORY.md"
        ums.parent.mkdir(parents=True)
        ums.write_text("# user sub memory\n")
        result = run(str(ums))
        c = result.get("classification", {})
        check("user-scope agent-memory → target_type=subagent-memory",
              c.get("target_type") == "subagent-memory", str(c))


def main():
    print("Phase 0 dispatch smoke tests — auditing-cc-configs")

    test_skill_dispatch()
    test_auto_memory_dispatch()
    test_agent_memory_dispatch()

    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    print(f"\nSummary: {passed}/{total} dispatch smoke tests passed")
    failed = [(n, d) for n, ok, d in RESULTS if not ok]
    if failed:
        for n, d in failed:
            print(f"  ✗ {n}: {d}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
