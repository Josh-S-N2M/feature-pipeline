#!/usr/bin/env python3
"""smoke_test_parse_blocks_x_markers.py — Smoke tests for parse_blocks_x_markers.py.

Exercises the parser (T3.1) against synthetic fixture files per ADR-0063 and FR-9
of pipeline-cross-artifact-discipline-r1.  Gates PV-3.C1 and PV-3.C2.

Run as:
    python3 .claude/skills/auditing-shared/scripts/smoke_test_parse_blocks_x_markers.py
Exit 0 = all pass; non-zero = failure with diagnostic on stderr.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

PARSER = str(Path(__file__).parent / "parse_blocks_x_markers.py")


class SmokeFailure(Exception):
    pass


def _run(path: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", PARSER, path], capture_output=True, text=True, timeout=30
    )


def _eq(label: str, got, want) -> None:
    if got != want:
        raise SmokeFailure(f"{label}: got {got!r}, want {want!r}")


def _in(label: str, needle, haystack) -> None:
    if needle not in haystack:
        raise SmokeFailure(f"{label}: {needle!r} not in {haystack!r}")


def _fixture(content: str):
    """Context manager returning a path to a temp .md file with *content*."""
    import contextlib
    import os

    @contextlib.contextmanager
    def _ctx():
        fd, path = tempfile.mkstemp(suffix=".md")
        try:
            with os.fdopen(fd, "w") as fh:
                fh.write(content)
            yield path
        finally:
            Path(path).unlink(missing_ok=True)

    return _ctx()


# ---------------------------------------------------------------------------
# Scenarios (A-G)
# ---------------------------------------------------------------------------

def scenario_wellformed_only() -> None:
    """A: well-formed marker only → exit 0, slug captured, no malformed."""
    with _fixture("# Doc\n\n<!-- BLOCKS: phase-3-completion -->\n\nMore.\n") as p:
        r = _run(p)
        _eq("A exit", r.returncode, 0)
        d = json.loads(r.stdout)
        _eq("A markers", len(d["markers"]), 1)
        _eq("A slug", d["markers"][0]["stage_slug"], "phase-3")
        _eq("A no malformed", d["malformed"], [])
        _eq("A payload null", d["markers"][0]["payload_description"], None)


def scenario_malformed_wrong_case() -> None:
    """B: wrong-case 'blocks:' token → exit 1, malformed entry with reason."""
    with _fixture("# Doc\n\n<!-- blocks: phase-3-completion -->\n") as p:
        r = _run(p)
        _eq("B exit", r.returncode, 1)
        d = json.loads(r.stdout)
        _eq("B markers empty", d["markers"], [])
        if not d["malformed"]:
            raise SmokeFailure("B: expected malformed entry")
        _in("B reason", "case", d["malformed"][0]["reason"].lower())


def scenario_wellformed_and_malformed() -> None:
    """C: good + bad marker in same file → exit 1."""
    content = (
        "<!-- BLOCKS: task-decomposition-completion -->\n"
        "<!-- blocks: deliverable-packaging-completion -->\n"
    )
    with _fixture(content) as p:
        r = _run(p)
        _eq("C exit", r.returncode, 1)
        d = json.loads(r.stdout)
        _eq("C one good", len(d["markers"]), 1)
        _eq("C good slug", d["markers"][0]["stage_slug"], "task-decomposition")
        if not d["malformed"]:
            raise SmokeFailure("C: expected malformed entry")


def scenario_marker_with_payload() -> None:
    """D: em-dash payload → exit 0, payload_description populated."""
    with _fixture("<!-- BLOCKS: design-cc-completion — A-5 grammar undecided -->\n") as p:
        r = _run(p)
        _eq("D exit", r.returncode, 0)
        d = json.loads(r.stdout)
        _eq("D slug", d["markers"][0]["stage_slug"], "design-cc")
        payload = d["markers"][0]["payload_description"]
        if not payload or "A-5 grammar undecided" not in payload:
            raise SmokeFailure(f"D: unexpected payload {payload!r}")
        _eq("D no malformed", d["malformed"], [])


def scenario_no_markers() -> None:
    """E: no BLOCKS markers → exit 2 (informational)."""
    with _fixture("# Discovery\n\nNo blocking issues found.\n") as p:
        r = _run(p)
        _eq("E exit", r.returncode, 2)
        d = json.loads(r.stdout)
        _eq("E markers empty", d["markers"], [])
        _eq("E malformed empty", d["malformed"], [])


def scenario_multiple_markers() -> None:
    """F: three well-formed markers → all captured, exit 0."""
    content = (
        "<!-- BLOCKS: synthesis-completion -->\n"
        "<!-- BLOCKS: design-cc-completion -->\n"
        "<!-- BLOCKS: plan-authoring-completion — backlog open -->\n"
    )
    with _fixture(content) as p:
        r = _run(p)
        _eq("F exit", r.returncode, 0)
        d = json.loads(r.stdout)
        _eq("F count", len(d["markers"]), 3)
        _eq(
            "F slugs",
            sorted(m["stage_slug"] for m in d["markers"]),
            sorted(["synthesis", "design-cc", "plan-authoring"]),
        )
        _eq("F no malformed", d["malformed"], [])


def scenario_missing_completion_suffix() -> None:
    """G: slug without -completion suffix → exit 1 / malformed."""
    with _fixture("<!-- BLOCKS: phase-3 -->\n") as p:
        r = _run(p)
        _eq("G exit", r.returncode, 1)
        d = json.loads(r.stdout)
        if not d["malformed"]:
            raise SmokeFailure("G: expected malformed entry")
        reason = d["malformed"][0]["reason"].lower()
        if "completion" not in reason and "grammar" not in reason:
            raise SmokeFailure(f"G: reason should mention 'completion' or 'grammar': {reason!r}")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

SCENARIOS = [
    ("A: well-formed only → exit 0", scenario_wellformed_only),
    ("B: malformed wrong-case → exit 1", scenario_malformed_wrong_case),
    ("C: well-formed + malformed → exit 1", scenario_wellformed_and_malformed),
    ("D: em-dash payload → exit 0, payload captured", scenario_marker_with_payload),
    ("E: no markers → exit 2", scenario_no_markers),
    ("F: multiple markers → all captured", scenario_multiple_markers),
    ("G: missing -completion suffix → exit 1", scenario_missing_completion_suffix),
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
