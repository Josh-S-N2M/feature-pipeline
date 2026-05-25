#!/usr/bin/env python3
"""Golden-file harness for intercept-issue-capture-agent.sh hook.

Per Plan T5.3 (single-fixture early-verification) + T5.4 (5-fixture full suite).

Each test case:
  1. Constructs a synthetic PreToolUse event JSON
  2. Pipes it to bash .claude/hooks/intercept-issue-capture-agent.sh via subprocess
  3. Parses the hook's stdout as JSON
  4. Asserts the JSON matches the expected golden value

Exit code: 0 if all fixtures PASS; non-zero if any FAIL.

Results JSON is written to RESULTS_JSON_PATH on every run.
"""
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HOOK_PATH = Path(__file__).parent / "intercept-issue-capture-agent.sh"

# Deliverable path for the structured results JSON (T5.4 requirement).
RESULTS_JSON_PATH = (
    Path(__file__).parent.parent.parent
    / "working"
    / "feature"
    / "issue-capture-mechanism-r1"
    / "hook-golden-results.json"
)


def run_hook(event_json: dict | str) -> tuple[dict, str, int]:
    """Run the hook with the given event on stdin; return (parsed_stdout_json, stderr, exit_code)."""
    stdin_payload = json.dumps(event_json) if isinstance(event_json, dict) else event_json
    result = subprocess.run(
        ["bash", str(HOOK_PATH)],
        input=stdin_payload,
        capture_output=True,
        text=True,
        timeout=10,
    )
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"hook stdout not valid JSON: {e}\nstdout: {result.stdout!r}")
    return parsed, result.stderr, result.returncode


def assert_decision(parsed: dict, expected_decision: str, label: str) -> str:
    """Assert the hook's permissionDecision matches expected; return the actual decision."""
    actual = parsed.get("hookSpecificOutput", {}).get("permissionDecision")
    assert actual == expected_decision, (
        f"{label}: expected permissionDecision={expected_decision!r}, got {actual!r}\n"
        f"full output: {parsed}"
    )
    return actual


# ---- Fixture 1 (single-fixture for T5.3): issue-capture-author spawn → ask ----

def fixture_1_issue_capture_author_ask():
    """T5.3 single-fixture: issue-capture-author spawn must produce permissionDecision: 'ask'."""
    event = {
        "session_id": "test-session-001",
        "transcript_path": "/tmp/test-transcript.jsonl",
        "tool_name": "Task",
        "tool_input": {
            "subagent_type": "issue-capture-author",
            "description": "Capture an issue about pipeline gate-7 missing rollback-on-failure",
            "prompt": "create-mode: pipeline gate-7 needs rollback-on-failure",
        },
    }
    parsed, stderr, exit_code = run_hook(event)
    assert exit_code == 0, f"hook exited non-zero: {exit_code}; stderr: {stderr}"
    actual = assert_decision(parsed, "ask", "fixture_1")
    # Verify the reason is non-empty and mentions issue-capture-author OR contains the prompt preview
    reason = parsed.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
    assert len(reason) > 0, f"fixture_1: permissionDecisionReason is empty"
    # Optionally assert the reason mentions key content
    assert "issue-capture-author" in reason or "Capture an issue" in reason or "rollback-on-failure" in reason, \
        f"fixture_1: reason should reference key content; got: {reason[:200]}"
    print("  PASS  fixture_1: issue-capture-author → ask")
    return actual


# ---- Fixture 2: non-issue-capture spawn (cc-critique) → fast-path allow ----

def fixture_2_cc_critique_allow():
    """Non-issue-capture spawn (cc-critique) → fast-path allow."""
    event = {
        "tool_name": "Task",
        "tool_input": {
            "subagent_type": "cc-critique",
            "description": "Audit .claude/ tree",
        },
    }
    parsed, stderr, exit_code = run_hook(event)
    assert exit_code == 0, f"hook exited non-zero: {exit_code}; stderr: {stderr}"
    actual = assert_decision(parsed, "allow", "fixture_2")
    print("  PASS  fixture_2: cc-critique → allow")
    return actual


# ---- Fixture 3: another non-issue-capture spawn → fast-path allow ----

def fixture_3_discovery_codebase_researcher_allow():
    """Another non-issue-capture spawn (discovery-codebase-researcher) → fast-path allow."""
    event = {
        "tool_name": "Task",
        "tool_input": {
            "subagent_type": "discovery-codebase-researcher",
            "description": "Run codebase analysis",
        },
    }
    parsed, stderr, exit_code = run_hook(event)
    assert exit_code == 0, f"hook exited non-zero: {exit_code}; stderr: {stderr}"
    actual = assert_decision(parsed, "allow", "fixture_3")
    print("  PASS  fixture_3: discovery-codebase-researcher → allow")
    return actual


# ---- Fixture 4: empty stdin → fail-OPEN allow ----

def fixture_4_empty_stdin_fail_open():
    """Empty stdin → fail-OPEN with allow."""
    parsed, stderr, exit_code = run_hook("")  # empty string
    assert exit_code == 0, f"hook exited non-zero on empty stdin: {exit_code}"
    actual = assert_decision(parsed, "allow", "fixture_4")
    # The hook emits a diagnostic to stderr for the empty-stdin path
    assert "empty stdin" in stderr.lower() or "fail-open" in stderr.lower(), \
        f"fixture_4: expected fail-open diagnostic in stderr; got: {stderr[:200]}"
    print("  PASS  fixture_4: empty stdin → fail-open allow")
    return actual


# ---- Fixture 5: malformed JSON stdin → fail-OPEN allow ----

def fixture_5_malformed_json_fail_open():
    """Malformed JSON stdin → fail-OPEN with allow.

    The hook uses jq to extract .tool_input.subagent_type; malformed JSON causes
    jq to return empty, so the hook takes the 'no subagent_type' fast-path allow.
    Exit code is still 0 and permissionDecision is 'allow'.
    """
    parsed, _stderr, exit_code = run_hook("{not valid json")
    assert exit_code == 0, f"hook exited non-zero on malformed JSON: {exit_code}"
    actual = assert_decision(parsed, "allow", "fixture_5")
    print("  PASS  fixture_5: malformed JSON → fail-open allow")
    return actual


def main() -> int:
    fixtures = [
        fixture_1_issue_capture_author_ask,
        fixture_2_cc_critique_allow,
        fixture_3_discovery_codebase_researcher_allow,
        fixture_4_empty_stdin_fail_open,
        fixture_5_malformed_json_fail_open,
    ]

    results = []
    failed = 0

    for fx in fixtures:
        t_start = time.perf_counter()
        verdict = "PASS"
        error_msg = None
        actual_decision = None
        try:
            actual_decision = fx()
        except AssertionError as e:
            verdict = "FAIL"
            error_msg = str(e)
            print(f"  FAIL  {fx.__name__}: {e}")
            failed += 1
        except Exception as e:
            verdict = "FAIL"
            error_msg = f"unexpected exception: {e}"
            print(f"  FAIL  {fx.__name__}: {e}")
            failed += 1
        elapsed_ms = round((time.perf_counter() - t_start) * 1000, 1)

        # Derive expected_decision from fixture docstring convention (fallback: unknown)
        doc = fx.__doc__ or ""
        if "ask" in doc.split("→")[-1] if "→" in doc else "":
            expected_decision = "ask"
        elif "allow" in doc.split("→")[-1] if "→" in doc else "":
            expected_decision = "allow"
        else:
            expected_decision = "ask" if fx.__name__ == "fixture_1_issue_capture_author_ask" else "allow"

        entry = {
            "name": fx.__name__,
            "verdict": verdict,
            "expected_decision": expected_decision,
            "actual_decision": actual_decision,
            "elapsed_ms": elapsed_ms,
        }
        if error_msg:
            entry["error"] = error_msg
        results.append(entry)

    total = len(fixtures)
    passed = total - failed
    overall_verdict = "PASS" if failed == 0 else "FAIL"

    results_payload = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "fixtures_total": total,
        "fixtures_passed": passed,
        "fixtures_failed": failed,
        "fixtures": results,
        "verdict": overall_verdict,
    }

    # Ensure the output directory exists before writing.
    RESULTS_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_JSON_PATH.write_text(json.dumps(results_payload, indent=2) + "\n", encoding="utf-8")
    print(f"\nResults written to: {RESULTS_JSON_PATH}")

    if failed == 0:
        print(f"\nALL PASS ({total}/{total} fixtures)")
        return 0
    else:
        print(f"\nFAILED {failed}/{total} fixtures")
        return 1


if __name__ == "__main__":
    sys.exit(main())
