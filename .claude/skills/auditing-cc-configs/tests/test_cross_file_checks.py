#!/usr/bin/env python3
"""
test_cross_file_checks.py — Unit tests for cross_file_checks.py.

Tests each implemented check against a fixture project. Uses Python's tempfile
to create isolated fixtures per test.

Run:
    python3 tests/test_cross_file_checks.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "cross_file_checks.py"


def run_checks(fixture: Path) -> list[dict]:
    r = subprocess.run([sys.executable, str(SCRIPT), str(fixture)],
                        capture_output=True, text=True, timeout=15)
    if r.returncode != 0:
        raise RuntimeError(f"script failed: {r.stderr}")
    data = json.loads(r.stdout)
    return data.get("cross_file_findings", [])


def find_by_check(findings: list[dict], check_id: str) -> list[dict]:
    return [f for f in findings if f.get("check") == check_id]


def setup_minimal_project(root: Path) -> None:
    (root / ".claude").mkdir(parents=True, exist_ok=True)
    (root / ".gitignore").write_text("")


# ---- Per-check tests ----

def test_X1_hook_script_missing():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        settings = {
            "hooks": {
                "PreToolUse": [{
                    "matcher": "Bash",
                    "hooks": [{"type": "command", "command": ".claude/hooks/missing.sh"}]
                }]
            }
        }
        (root / ".claude" / "settings.json").write_text(json.dumps(settings))
        findings = run_checks(root)
        x1 = find_by_check(findings, "X1")
        assert len(x1) == 1, f"expected 1 X1 finding, got {len(x1)}"
        assert x1[0]["severity"] == "BLOCKER"
        print("  X1: OK (missing hook script detected)")


def test_X1_hook_script_present():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        (root / ".claude" / "hooks").mkdir()
        (root / ".claude" / "hooks" / "real.sh").write_text("#!/bin/bash\nexit 0\n")
        settings = {
            "hooks": {
                "PreToolUse": [{
                    "matcher": "Bash",
                    "hooks": [{"type": "command", "command": ".claude/hooks/real.sh"}]
                }]
            }
        }
        (root / ".claude" / "settings.json").write_text(json.dumps(settings))
        findings = run_checks(root)
        x1 = find_by_check(findings, "X1")
        assert len(x1) == 0, f"expected 0 X1 findings, got {len(x1)}"
        print("  X1: OK (existing script not flagged)")


def test_X4_name_collision():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        (root / ".claude" / "agents").mkdir()
        (root / ".claude" / "commands").mkdir()
        (root / ".claude" / "agents" / "deploy.md").write_text("---\nname: deploy\ndescription: x. Use when\n---\nbody")
        (root / ".claude" / "commands" / "deploy.md").write_text("body")
        findings = run_checks(root)
        x4 = find_by_check(findings, "X4")
        assert len(x4) == 1
        assert "deploy" in x4[0]["what"]
        print("  X4: OK (name collision detected)")


def test_X10_settings_local_no_gitignore():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        (root / ".claude" / "settings.local.json").write_text("{}")
        findings = run_checks(root)
        x10 = find_by_check(findings, "X10")
        assert len(x10) == 1
        assert x10[0]["severity"] == "MAJOR"
        print("  X10: OK (settings.local.json without gitignore)")


def test_X10_settings_local_with_gitignore():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        (root / ".claude" / "settings.local.json").write_text("{}")
        (root / ".gitignore").write_text(".claude/settings.local.json\n")
        findings = run_checks(root)
        x10 = find_by_check(findings, "X10")
        assert len(x10) == 0
        print("  X10: OK (gitignore-covered settings.local.json not flagged)")


def test_X11_outside_at_import():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        (root / "CLAUDE.md").write_text("# project\n\n@/etc/somefile.md\n")
        findings = run_checks(root)
        x11 = find_by_check(findings, "X11")
        assert len(x11) >= 1
        assert "/etc/somefile.md" in x11[0]["what"]
        print("  X11: OK (outside-root @-import detected)")


def test_X13_local_memory_no_gitignore():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        (root / ".claude" / "agents").mkdir()
        (root / ".claude" / "agents" / "a.md").write_text(
            "---\nname: a\ndescription: x. Use when. Use for.\nmemory: local\n---\nbody"
        )
        findings = run_checks(root)
        x13 = find_by_check(findings, "X13")
        assert len(x13) == 1
        print("  X13: OK (memory:local without gitignore detected)")


def test_X14_missing_output_style():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        settings = {"outputStyles": ["does-not-exist"]}
        (root / ".claude" / "settings.json").write_text(json.dumps(settings))
        findings = run_checks(root)
        x14 = find_by_check(findings, "X14")
        assert len(x14) == 1
        print("  X14: OK (missing output style detected)")


def test_X21_orphan_memory():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        (root / ".claude" / "agent-memory" / "orphan").mkdir(parents=True)
        findings = run_checks(root)
        x21 = find_by_check(findings, "X21")
        assert len(x21) == 1
        assert "orphan" in x21[0]["what"]
        print("  X21: OK (orphan memory dir detected)")


def test_X22_automemory_wrong_scope():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        settings = {"autoMemoryDirectory": "/tmp/mem"}
        (root / ".claude" / "settings.json").write_text(json.dumps(settings))
        findings = run_checks(root)
        x22 = find_by_check(findings, "X22")
        assert len(x22) == 1
        print("  X22: OK (autoMemoryDirectory at project scope detected)")


def test_X23_local_memory_dir_no_gitignore():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        (root / ".claude" / "agent-memory-local").mkdir()
        findings = run_checks(root)
        x23 = find_by_check(findings, "X23")
        assert len(x23) == 1
        print("  X23: OK (agent-memory-local dir without gitignore detected)")


def test_empty_project_no_findings():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        findings = run_checks(root)
        assert findings == [], f"expected no findings, got {findings}"
        print("  Empty project: OK (no findings)")


# ---- Tests for the 13 newly-added checks ----

def test_X3_subagent_skills_disable_invocation():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        (root / ".claude" / "agents").mkdir()
        (root / ".claude" / "skills" / "noinvoke").mkdir(parents=True)
        (root / ".claude" / "skills" / "noinvoke" / "SKILL.md").write_text(
            "---\nname: noinvoke\ndescription: x. Use when.\ndisable-model-invocation: true\n---\nbody"
        )
        (root / ".claude" / "agents" / "my.md").write_text(
            "---\nname: my\ndescription: x. Use when.\ntools: Read\nskills:\n  - noinvoke\n---\nbody"
        )
        findings = run_checks(root)
        x3 = find_by_check(findings, "X3")
        assert len(x3) == 1, f"expected 1 X3 finding, got {len(x3)}"
        assert x3[0]["severity"] == "BLOCKER"
        print("  X3: OK (subagent preloads disable-model-invocation skill detected)")


def test_X5_command_references_missing_skill():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        (root / ".claude" / "commands").mkdir()
        (root / ".claude" / "commands" / "deploy.md").write_text(
            "---\ndescription: Deploy\n---\nUse the kubectl-helper skill to deploy."
        )
        findings = run_checks(root)
        x5 = find_by_check(findings, "X5")
        assert len(x5) == 1, f"expected 1 X5 finding, got {len(x5)}"
        assert "kubectl-helper" in x5[0]["what"]
        print("  X5: OK (missing skill reference detected)")


def test_X5_command_references_present_skill():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        (root / ".claude" / "commands").mkdir()
        (root / ".claude" / "skills" / "real-skill").mkdir(parents=True)
        (root / ".claude" / "skills" / "real-skill" / "SKILL.md").write_text("---\nname: real-skill\ndescription: x.\n---\nbody")
        (root / ".claude" / "commands" / "deploy.md").write_text(
            "---\ndescription: Deploy\n---\nUse the real-skill skill to deploy."
        )
        findings = run_checks(root)
        x5 = find_by_check(findings, "X5")
        assert len(x5) == 0, f"expected 0 X5 findings, got {len(x5)}"
        print("  X5: OK (existing skill reference not flagged)")


def test_X6_claude_md_rule_duplication():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        (root / ".claude" / "rules").mkdir()
        duplicated = "Always run tests before committing changes to the main branch of this repository."
        (root / "CLAUDE.md").write_text(f"# Project\n\n{duplicated}\n")
        (root / ".claude" / "rules" / "ts.md").write_text(
            "---\npaths: ['**/*.ts']\n---\n\n# Rules\n\n" + duplicated + "\n"
        )
        findings = run_checks(root)
        x6 = find_by_check(findings, "X6")
        assert len(x6) >= 1, f"expected at least 1 X6 finding, got {len(x6)}"
        print("  X6: OK (duplicated rule detected)")


def test_X7_rule_paths_glob_matches_nothing():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        (root / ".claude" / "rules").mkdir()
        # Glob pointing at a language not in this repo
        (root / ".claude" / "rules" / "rust.md").write_text(
            "---\npaths:\n  - '**/*.rs'\n  - '**/Cargo.toml'\n---\n\n# Rust rules"
        )
        findings = run_checks(root)
        x7 = find_by_check(findings, "X7")
        assert len(x7) == 1, f"expected 1 X7 finding, got {len(x7)}"
        assert x7[0]["severity"] == "BLOCKER"
        print("  X7: OK (paths glob matching nothing detected)")


def test_X8_env_var_unset():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        settings = {
            "env": {
                "DERIVED_KEY": "${UNDEFINED_BASE_VAR}"
            }
        }
        (root / ".claude" / "settings.json").write_text(json.dumps(settings))
        findings = run_checks(root)
        x8 = find_by_check(findings, "X8")
        assert len(x8) == 1, f"expected 1 X8 finding, got {len(x8)}"
        print("  X8: OK (unset env var reference detected)")


def test_X9_subagent_with_skills_emits_info():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        (root / ".claude" / "agents").mkdir()
        (root / ".claude" / "agents" / "my.md").write_text(
            "---\nname: my\ndescription: x. Use when.\ntools: Read\nskills:\n  - some-skill\n---\nbody"
        )
        findings = run_checks(root)
        x9 = find_by_check(findings, "X9")
        assert len(x9) == 1, f"expected 1 X9 finding, got {len(x9)}"
        print("  X9: OK (subagent skills list flagged for review)")


def test_X12_hook_string_match_should_be_permission():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        (root / ".claude" / "hooks").mkdir()
        (root / ".claude" / "hooks" / "check.sh").write_text(
            "#!/usr/bin/env bash\n"
            "event=$(cat)\n"
            "cmd=$(echo \"$event\" | jq -r '.tool_input.command')\n"
            "case \"$cmd\" in\n"
            "  'git push origin master') exit 2 ;;\n"
            "esac\n"
        )
        findings = run_checks(root)
        x12 = find_by_check(findings, "X12")
        assert len(x12) == 1, f"expected 1 X12 finding, got {len(x12)}"
        print("  X12: OK (hook string-matching detected)")


def test_X15_project_hook_uses_home():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        settings = {
            "hooks": {
                "PreToolUse": [{
                    "hooks": [{"type": "command", "command": "~/scripts/audit.sh"}]
                }]
            }
        }
        (root / ".claude" / "settings.json").write_text(json.dumps(settings))
        findings = run_checks(root)
        x15 = find_by_check(findings, "X15")
        assert len(x15) == 1, f"expected 1 X15 finding, got {len(x15)}"
        assert x15[0]["severity"] == "MAJOR"
        print("  X15: OK ($HOME path in project hook detected)")


def test_X16_mcp_name_multiscope():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        settings_proj = {"mcpServers": {"github": {"command": "npx"}}}
        settings_local = {"mcpServers": {"github": {"command": "npx"}}}
        (root / ".claude" / "settings.json").write_text(json.dumps(settings_proj))
        (root / ".claude" / "settings.local.json").write_text(json.dumps(settings_local))
        # Cover gitignore so X10 doesn't pollute output
        (root / ".gitignore").write_text(".claude/settings.local.json\n")
        findings = run_checks(root)
        x16 = find_by_check(findings, "X16")
        assert len(x16) == 1, f"expected 1 X16 finding, got {len(x16)}"
        assert "github" in x16[0]["what"]
        print("  X16: OK (MCP name at multiple scopes detected)")


def test_X17_command_bypasses_subagent_permissions():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        (root / ".claude" / "agents").mkdir()
        (root / ".claude" / "commands").mkdir()
        (root / ".claude" / "agents" / "reviewer.md").write_text(
            "---\nname: reviewer\ndescription: x. Use when.\ntools: Read\n---\nbody"
        )
        (root / ".claude" / "commands" / "review.md").write_text(
            "---\ndescription: Review\n---\nInvoke @reviewer and bypass all prompts."
        )
        findings = run_checks(root)
        x17 = find_by_check(findings, "X17")
        assert len(x17) == 1, f"expected 1 X17 finding, got {len(x17)}"
        print("  X17: OK (bypass language in subagent invocation detected)")


def test_X19_memory_cites_inactive_rule():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        (root / ".claude" / "rules").mkdir()
        (root / ".claude" / "rules" / "swift.md").write_text(
            "---\npaths:\n  - '**/*.swift'\n---\n\n# Swift rules"
        )
        (root / ".claude" / "agent-memory" / "myagent").mkdir(parents=True)
        (root / ".claude" / "agent-memory" / "myagent" / "MEMORY.md").write_text(
            "# Memory\n\nFollow the rules in swift.md when reviewing.\n"
        )
        # Also create a dummy subagent declaring this name so X21 doesn't fire
        (root / ".claude" / "agents").mkdir(exist_ok=True)
        (root / ".claude" / "agents" / "myagent.md").write_text(
            "---\nname: myagent\ndescription: x. Use when.\ntools: Read\nmemory: project\n---\nbody"
        )
        findings = run_checks(root)
        x19 = find_by_check(findings, "X19")
        assert len(x19) >= 1, f"expected at least 1 X19 finding, got {len(x19)}"
        print("  X19: OK (memory cites inactive rule detected)")


def test_X20_memory_with_disallowed_write():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        (root / ".claude" / "agents").mkdir()
        (root / ".claude" / "agents" / "my.md").write_text(
            "---\nname: my\ndescription: x. Use when.\ntools: Read\nmemory: project\n"
            "disallowedTools: Write, Edit\n---\nbody"
        )
        findings = run_checks(root)
        x20 = find_by_check(findings, "X20")
        assert len(x20) == 1, f"expected 1 X20 finding, got {len(x20)}"
        assert x20[0]["severity"] == "BLOCKER"
        print("  X20: OK (memory + disallowed Write detected)")


def test_X24_committed_memory_machine_local():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setup_minimal_project(root)
        (root / ".claude" / "agent-memory" / "myagent").mkdir(parents=True)
        (root / ".claude" / "agent-memory" / "myagent" / "MEMORY.md").write_text(
            "# Memory\n\nProject is at /home/alice/code/myproject.\n"
        )
        findings = run_checks(root)
        x24 = find_by_check(findings, "X24")
        assert len(x24) >= 1, f"expected at least 1 X24 finding, got {len(x24)}"
        assert x24[0]["severity"] == "MAJOR"
        print("  X24: OK (machine-local path in committed memory detected)")


TESTS = [
    test_X1_hook_script_missing,
    test_X1_hook_script_present,
    test_X4_name_collision,
    test_X10_settings_local_no_gitignore,
    test_X10_settings_local_with_gitignore,
    test_X11_outside_at_import,
    test_X13_local_memory_no_gitignore,
    test_X14_missing_output_style,
    test_X21_orphan_memory,
    test_X22_automemory_wrong_scope,
    test_X23_local_memory_dir_no_gitignore,
    test_empty_project_no_findings,
    # Phase 7 continuation: 13 new checks
    test_X3_subagent_skills_disable_invocation,
    test_X5_command_references_missing_skill,
    test_X5_command_references_present_skill,
    test_X6_claude_md_rule_duplication,
    test_X7_rule_paths_glob_matches_nothing,
    test_X8_env_var_unset,
    test_X9_subagent_with_skills_emits_info,
    test_X12_hook_string_match_should_be_permission,
    test_X15_project_hook_uses_home,
    test_X16_mcp_name_multiscope,
    test_X17_command_bypasses_subagent_permissions,
    test_X19_memory_cites_inactive_rule,
    test_X20_memory_with_disallowed_write,
    test_X24_committed_memory_machine_local,
]


def main() -> int:
    print("Running cross-file check unit tests...")
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
