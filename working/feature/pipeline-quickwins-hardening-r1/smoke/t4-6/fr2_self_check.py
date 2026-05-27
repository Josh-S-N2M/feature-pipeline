"""
FR-2 dispatch self-check harness — T4.6 smoke test.

Applies the absence-default rule from ADR-0057 and the FR-2 gate logic
documented in recipe-feature-pipeline/SKILL.md §FR-2 dispatch self-check.

Exit codes:
  0 — self-check passes (PASS verdict)
  1 — self-check refuses (REFUSE verdict, diagnostic printed)
  2 — internal error (missing field, malformed JSON, etc.)
"""

import json
import sys
from pathlib import Path


WORKAROUND = "parent-driven-workaround"
SPECIALIST = "specialist-dispatch"


def load_fixture(path: str) -> dict:
    try:
        text = Path(path).read_text()
    except FileNotFoundError:
        print(f"ERROR: checkpoint file not found: {path}", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"ERROR: malformed JSON in {path}: {exc}", file=sys.stderr)
        sys.exit(2)


def effective_mode(stage: dict) -> str:
    """
    Return the effective execution_mode for a stage.

    Per ADR-0057 absence-default rule: if the field is absent, treat it as
    specialist-dispatch. This is the backward-compatible safe default for
    checkpoints written before ADR-0057 promoted the field.
    """
    return stage.get("execution_mode", SPECIALIST)


def run_self_check(checkpoint: dict) -> dict:
    """
    Execute the FR-2 gate logic.

    Returns a result dict with keys:
      verdict       — "PASS" or "REFUSE"
      scope_class   — the value read from the fixture
      stages        — list of {stage_name, resolved_mode} for all stages
      diagnostic    — None or the four FR-6 diagnostic fields
    """
    scope_class = checkpoint.get("scope_class")
    if not scope_class:
        print(
            "ERROR: checkpoint has no scope_class field — cannot run self-check.",
            file=sys.stderr,
        )
        sys.exit(2)

    stages = checkpoint.get("stages", [])
    resolved = []
    for stage in stages:
        name = stage.get("stage_name", "<unnamed>")
        mode = effective_mode(stage)
        resolved.append({"stage_name": name, "resolved_mode": mode})

    # Gate logic per SKILL.md §FR-2 dispatch self-check
    if scope_class == "FULL":
        offenders = [r for r in resolved if r["resolved_mode"] == WORKAROUND]
        if offenders:
            offender = offenders[0]
            return {
                "verdict": "REFUSE",
                "scope_class": scope_class,
                "stages": resolved,
                "diagnostic": {
                    "mechanism": "FR-2 dispatch self-check",
                    "offending_artifact": offender["stage_name"],
                    "rule_violated": (
                        "FULL-scope features prohibit parent-driven-workaround "
                        "execution mode per PRD §FR-2 and ADR-0057"
                    ),
                    "remedial_hint": (
                        "either change scope_class to MINOR/PATCH OR "
                        "reconfigure the stage to specialist-dispatch"
                    ),
                },
            }
        return {
            "verdict": "PASS",
            "scope_class": scope_class,
            "stages": resolved,
            "diagnostic": None,
        }

    # MINOR or PATCH: both modes are permissible
    return {
        "verdict": "PASS",
        "scope_class": scope_class,
        "stages": resolved,
        "diagnostic": None,
    }


def print_result(result: dict, fixture_path: str) -> None:
    print(f"fixture: {fixture_path}")
    print(f"scope_class: {result['scope_class']}")
    print(f"verdict: {result['verdict']}")
    print()
    print("stage resolution (absence-default applied):")
    for s in result["stages"]:
        absent_marker = " [absent→default]" if s.get("_was_absent") else ""
        print(f"  {s['stage_name']}: {s['resolved_mode']}{absent_marker}")
    print()
    if result["diagnostic"]:
        d = result["diagnostic"]
        print("diagnostic:")
        print(f"  mechanism: {d['mechanism']}")
        print(f"  offending_artifact: {d['offending_artifact']}")
        print(f"  rule_violated: {d['rule_violated']}")
        print(f"  remedial_hint: {d['remedial_hint']}")
    else:
        print("diagnostic: none")


def annotate_absent(checkpoint: dict, resolved: list) -> list:
    """Re-annotate resolved list with absence flag for display."""
    stages = checkpoint.get("stages", [])
    annotated = []
    for stage, r in zip(stages, resolved):
        was_absent = "execution_mode" not in stage
        annotated.append({**r, "_was_absent": was_absent})
    return annotated


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <checkpoint-fixture.json>", file=sys.stderr)
        sys.exit(2)

    fixture_path = sys.argv[1]
    checkpoint = load_fixture(fixture_path)
    result = run_self_check(checkpoint)

    # Annotate for display (mark which stages had the field absent)
    result["stages"] = annotate_absent(checkpoint, result["stages"])
    print_result(result, fixture_path)

    if result["verdict"] == "PASS":
        sys.exit(0)
    else:
        sys.exit(1)
