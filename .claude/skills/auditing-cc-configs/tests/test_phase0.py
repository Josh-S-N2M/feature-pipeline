#!/usr/bin/env python3
"""
test_phase0.py — Consolidated tests for Phase 0 deterministic scripts.

Covers tasks 0.17, 0.18, 0.19 of the execution plan:
  0.17 — verdict_compute.py calibration tests
  0.18 — pedagogical_marker_check.py matrix tests
  0.19 — triage_with_judge.py dry-run + schema validation

Run from the auditing-cc-configs/ root:
    python3 tests/test_phase0.py
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"

# ---------- Test infrastructure ----------

TEST_RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = ""):
    TEST_RESULTS.append((name, condition, detail))
    if condition:
        print(f"  ✓ {name}")
    else:
        print(f"  ✗ {name} — {detail}")


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_dims() -> list[dict]:
    return [{"number": i, "name": f"d{i}", "applicable": True} for i in range(1, 11)]


# ---------- 0.17 — verdict_compute calibration ----------

def test_verdict_compute():
    print("\n=== 0.17 — verdict_compute.py calibration ===")
    vc = load_module(SCRIPTS / "verdict_compute.py")
    dims = make_dims()

    # Clean PASS
    r = vc.compute({"target": "/t", "mode": "single", "findings": [],
                    "cross_file_findings": [], "dimensions": dims})
    check("clean = 100/PASS",
          r["score"] == 100 and r["verdict"] == "PASS",
          str(r))

    # 1 BLOCKER → 78 / NEEDS-WORK
    r = vc.compute({"target": "/t", "mode": "single",
                    "findings": [{"dimension": 1, "severity": "BLOCKER",
                                  "location": "x:1", "what": "x", "fix": "x"}],
                    "cross_file_findings": [], "dimensions": dims})
    check("1 BLOCKER = 78/NEEDS-WORK",
          r["score"] == 78 and r["verdict"] == "NEEDS-WORK",
          str(r))

    # 2 BLOCKERs → 56 / FAIL
    r = vc.compute({"target": "/t", "mode": "single",
                    "findings": [
                        {"dimension": 1, "severity": "BLOCKER", "location": "x:1", "what": "x", "fix": "x"},
                        {"dimension": 2, "severity": "BLOCKER", "location": "x:1", "what": "x", "fix": "x"},
                    ],
                    "cross_file_findings": [], "dimensions": dims})
    check("2 BLOCKERs = 56/FAIL",
          r["score"] == 56 and r["verdict"] == "FAIL",
          str(r))

    # 3 MAJORs across dims → 85 / PASS-WITH-MINOR-FIXES
    r = vc.compute({"target": "/t", "mode": "single",
                    "findings": [
                        {"dimension": 1, "severity": "MAJOR"},
                        {"dimension": 2, "severity": "MAJOR"},
                        {"dimension": 3, "severity": "MAJOR"},
                    ],
                    "cross_file_findings": [], "dimensions": dims})
    check("3 MAJORs = 85/PASS-WITH-MINOR-FIXES",
          r["score"] == 85 and r["verdict"] == "PASS-WITH-MINOR-FIXES",
          str(r))

    # 6 MAJORs → 70 / NEEDS-WORK
    r = vc.compute({"target": "/t", "mode": "single",
                    "findings": [{"dimension": i, "severity": "MAJOR"} for i in range(1, 7)],
                    "cross_file_findings": [], "dimensions": dims})
    check("6 MAJORs = 70/NEEDS-WORK",
          r["score"] == 70 and r["verdict"] == "NEEDS-WORK",
          str(r))

    # Security CRITICAL BLOCKER → SECURITY-BLOCK regardless of score
    r = vc.compute({"target": "/t", "mode": "single",
                    "findings": [{"dimension": 8, "severity": "BLOCKER",
                                  "is_security_critical": True}],
                    "cross_file_findings": [], "dimensions": dims})
    check("security CRITICAL → SECURITY-BLOCK",
          r["verdict"] == "SECURITY-BLOCK" and r["security_block"],
          str(r))


# ---------- 0.18 — pedagogical_marker_check matrix ----------

def setup_marker_fixtures(tmp: Path) -> dict[str, Path]:
    """Build fixtures for marker tests."""
    s1 = tmp / "skill1"
    (s1 / "references").mkdir(parents=True)
    (s1 / "SKILL.md").write_text(
        "---\n"
        "name: skill1\n"
        "description: test\n"
        "pedagogical_sections:\n"
        "  - references/attack-catalog.md\n"
        "---\n"
    )
    (s1 / "references" / "attack-catalog.md").write_text(
        "# Attacks\n"
        "\n"
        "Live keys like AKIAIOSFODNN7EXAMPLE.\n"
        "\n"
        "```audit-example\n"
        "AWS_KEY=AKIA1234567890EXAMPLE\n"
        "```\n"
        "\n"
        "Done.\n"
    )
    (s1 / "references" / "unmarked.md").write_text(
        "# Unmarked\n"
        "\n"
        "Has AKIAIOSFODNN7EXAMPLE in plain text.\n"
    )

    # Skill 2: anti-laundering case — declared non-md file
    s2 = tmp / "skill2"
    (s2 / "scripts").mkdir(parents=True)
    (s2 / "SKILL.md").write_text(
        "---\n"
        "name: skill2\n"
        "description: x\n"
        "pedagogical_sections:\n"
        "  - scripts/exfil.sh\n"
        "---\n"
    )
    (s2 / "scripts" / "exfil.sh").write_text("#!/bin/bash\n")

    # Skill 3: live credential in pedagogical file (real attack)
    s3 = tmp / "skill3"
    (s3 / "references").mkdir(parents=True)
    (s3 / "SKILL.md").write_text(
        "---\n"
        "name: skill3\n"
        "description: x\n"
        "pedagogical_sections:\n"
        "  - references/dangerous.md\n"
        "---\n"
    )
    (s3 / "references" / "dangerous.md").write_text(
        "# Dangerous\n"
        "\n"
        "```audit-example\n"
        "AWS_KEY=AKIATHISISAREALKEY00\n"
        "```\n"
    )

    return {"s1": s1, "s2": s2, "s3": s3}


def test_pedagogical_marker():
    print("\n=== 0.18 — pedagogical_marker_check.py matrix ===")
    mod = load_module(SCRIPTS / "pedagogical_marker_check.py")

    with tempfile.TemporaryDirectory() as tmpdir:
        fixtures = setup_marker_fixtures(Path(tmpdir))

        # FULL_MARKER: declared file + audit-example fence
        r = mod.process(fixtures["s1"], [{
            "dimension": 8, "severity": "BLOCKER",
            "location": "references/attack-catalog.md:6",
            "pattern_id": "AWS_KEY", "what": "x", "fix": "y"
        }])
        f = r["findings"][0]
        check("FULL_MARKER → INFO",
              f["marker_decision"] == "FULL_MARKER" and f["final_severity"] == "INFO",
              str(f))

        # MARKER_MISMATCH: declared file but not in fence
        r = mod.process(fixtures["s1"], [{
            "dimension": 8, "severity": "BLOCKER",
            "location": "references/attack-catalog.md:3",
            "pattern_id": "AWS_KEY", "what": "x", "fix": "y"
        }])
        f = r["findings"][0]
        check("MARKER_MISMATCH → MAJOR + new finding",
              f["marker_decision"] == "MARKER_MISMATCH" and
              f["final_severity"] == "MAJOR" and
              len(r["marker_findings"]) == 1,
              str(f))

        # NO_MARKER: file not declared, no fence
        r = mod.process(fixtures["s1"], [{
            "dimension": 8, "severity": "BLOCKER",
            "location": "references/unmarked.md:3",
            "pattern_id": "AWS_KEY", "what": "x", "fix": "y"
        }])
        f = r["findings"][0]
        check("NO_MARKER → unchanged",
              f["marker_decision"] == "NO_MARKER" and f["final_severity"] == "BLOCKER",
              str(f))

        # Anti-laundering: declare a non-md file
        r = mod.process(fixtures["s2"], [])
        check("anti-laundering: non-md declaration → MAJOR finding",
              any("not markdown" in mf.get("what", "")
                  for mf in r["marker_findings"]),
              str(r["marker_findings"]))

        # Anti-laundering: live credential (no EXAMPLE marker) in pedagogical file
        r = mod.process(fixtures["s3"], [{
            "dimension": 8, "severity": "BLOCKER",
            "location": "references/dangerous.md:4",
            "pattern_id": "AWS_KEY", "what": "x", "fix": "y"
        }])
        f = r["findings"][0]
        check("anti-laundering: live key → severity preserved",
              f["marker_decision"] == "LAUNDERING_OVERRIDE" and
              f["final_severity"] == "BLOCKER",
              str(f))


# ---------- 0.19 — triage_with_judge dry-run + schema validation ----------

def test_triage_schema():
    print("\n=== 0.19 — triage_with_judge.py dry-run + schema ===")
    mod = load_module(SCRIPTS / "triage_with_judge.py")

    # Schema validation cases
    check("invalid JSON → None",
          mod.validate_judge_output("not json") is None)
    check("missing fields → None",
          mod.validate_judge_output('{"decision": "CONFIRMED"}') is None)
    check("invalid decision value → None",
          mod.validate_judge_output(
              '{"decision":"OTHER","justification":"x",'
              '"recommended_severity_adjustment":0,"recommend_human_review":false}'
          ) is None)
    check("invalid adjustment → None",
          mod.validate_judge_output(
              '{"decision":"CONFIRMED","justification":"x",'
              '"recommended_severity_adjustment":99,"recommend_human_review":false}'
          ) is None)

    valid = mod.validate_judge_output(
        '{"decision":"CONFIRMED","justification":"x",'
        '"recommended_severity_adjustment":0,"recommend_human_review":false}'
    )
    check("valid JSON parses", valid is not None and valid["decision"] == "CONFIRMED")

    # CRITICAL never zeroed (asymmetric rule)
    with tempfile.TemporaryDirectory() as tmpdir:
        # write a fake target file
        target = Path(tmpdir) / "f.md"
        target.write_text("\n".join("line " + str(i) for i in range(50)))
        f = {
            "dimension": 8, "severity": "BLOCKER", "is_security_critical": True,
            "location": str(target) + ":10",
            "pattern_id": "X", "what": "x", "fix": "y",
            "marker_decision": "NO_MARKER",
        }
        # Force mock PEDAGOGICAL output
        prompt_template = mod.load_prompt_template()
        result = mod.triage(Path(tmpdir), [f], prompt_template, mod.call_judge_mock)
        # Mock returns CONFIRMED unless 'audit-example' in prompt
        # The prompt doesn't have it for this fixture; so mock returns CONFIRMED
        # CRITICAL stays BLOCKER and human review remains true
        ff = result["findings"][0]
        check("CRITICAL CONFIRMED → severity unchanged + human review",
              ff["final_severity"] == "BLOCKER" and
              ff["human_review_recommended"] == True,
              str(ff))

        # Now force PEDAGOGICAL: add 'audit-example' to file content
        target2 = Path(tmpdir) / "g.md"
        target2.write_text("```audit-example\nstuff\n```\n")
        f2 = dict(f)
        f2["location"] = str(target2) + ":2"
        result = mod.triage(Path(tmpdir), [f2], prompt_template, mod.call_judge_mock)
        ff = result["findings"][0]
        check("CRITICAL judged PEDAGOGICAL → max one-notch (MAJOR) + human review",
              ff["final_severity"] == "MAJOR" and
              ff["human_review_recommended"] == True,
              str(ff))

    # MINOR is skipped
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / "f.md"
        target.write_text("hello")
        f = {"dimension": 1, "severity": "MINOR",
             "location": str(target) + ":1",
             "pattern_id": "X", "what": "x", "fix": "y"}
        result = mod.triage(Path(tmpdir), [f], mod.load_prompt_template(), mod.call_judge_dry_run)
        ff = result["findings"][0]
        check("MINOR is skipped (not triaged)",
              ff["judge_decision"] == "SKIPPED" and ff["final_severity"] == "MINOR",
              str(ff))


# ---------- Summary ----------

def main():
    print("Phase 0 test suite — auditing-cc-configs")
    print(f"Script root: {SCRIPTS}")

    test_verdict_compute()
    test_pedagogical_marker()
    test_triage_schema()

    total = len(TEST_RESULTS)
    passed = sum(1 for _, ok, _ in TEST_RESULTS if ok)
    print(f"\nSummary: {passed}/{total} tests passed")
    failed = [(n, d) for n, ok, d in TEST_RESULTS if not ok]
    if failed:
        print("\nFailures:")
        for n, d in failed:
            print(f"  ✗ {n}: {d}")
        return 1
    print("All Phase 0 tests pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
