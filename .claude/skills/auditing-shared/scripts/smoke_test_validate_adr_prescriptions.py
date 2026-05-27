#!/usr/bin/env python3
"""smoke_test_validate_adr_prescriptions.py — Smoke tests for validate_adr_prescriptions.py.

Exercises the linter (T4.1) against synthetic fixture YAML files per ADR-0059 and
FR-1 of pipeline-design-time-discipline-r1. Gates PV-4.C1 and PV-4.C2.

Scenarios:
    A  well-formed companion            → exit 0 (valid)
    B  missing required top-level key   → exit 1 (invalid)
    C  prescription with invalid kind   → exit 1 (invalid)
    D  prescription with missing field  → exit 1 (invalid)
    E  file does not exist              → exit 2 (file not found)

Run as:
    python3 .claude/skills/auditing-shared/scripts/smoke_test_validate_adr_prescriptions.py
Exit 0 = all pass; non-zero = failure with diagnostic on stderr.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

LINTER = str(Path(__file__).parent / "validate_adr_prescriptions.py")


class SmokeFailure(Exception):
    pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(path: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", LINTER, path], capture_output=True, text=True, timeout=30
    )


def _eq(label: str, got, want) -> None:
    if got != want:
        raise SmokeFailure(f"{label}: got {got!r}, want {want!r}")


def _in(label: str, needle: str, haystack: str) -> None:
    if needle not in haystack:
        raise SmokeFailure(f"{label}: {needle!r} not found in output: {haystack!r}")


class _fixture:
    """Context manager: writes *content* to a temp .yaml file, yields the path."""

    def __init__(self, content: str):
        self._content = content
        self._path: str | None = None

    def __enter__(self) -> str:
        fd, path = tempfile.mkstemp(suffix=".prescriptions.yaml")
        try:
            with os.fdopen(fd, "w") as fh:
                fh.write(self._content)
        except Exception:
            os.unlink(path)
            raise
        self._path = path
        return path

    def __exit__(self, *_) -> None:
        if self._path:
            Path(self._path).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fixtures (canonical YAML strings)
# ---------------------------------------------------------------------------

WELL_FORMED_YAML = """\
adr_id: ADR-0059-adr-prescriptions-companion-file
version: 1.0.0
prescriptions:
  - assertion: "The linter validate_adr_prescriptions.py must exist in auditing-shared/scripts/"
    kind: file_exists
    target: .claude/skills/auditing-shared/scripts/validate_adr_prescriptions.py
    evidence: Check presence of the file at the declared path
    enforcement: required
  - assertion: "mcp.json must not reference the removed mcp-openapi-schema server"
    kind: substring_absent
    target: .mcp.json
    evidence: grep -c mcp-openapi-schema .mcp.json should return 0
    enforcement: required
"""

MISSING_TOP_LEVEL_KEY_YAML = """\
adr_id: ADR-0059-adr-prescriptions-companion-file
prescriptions:
  - assertion: "something"
    kind: file_exists
    target: some/file
    evidence: check it
    enforcement: required
"""
# 'version' key is absent

INVALID_KIND_YAML = """\
adr_id: ADR-0059-adr-prescriptions-companion-file
version: 1.0.0
prescriptions:
  - assertion: "some check"
    kind: nonexistent_kind
    target: some/file
    evidence: check it
    enforcement: required
"""

MISSING_REQUIRED_FIELD_YAML = """\
adr_id: ADR-0059-adr-prescriptions-companion-file
version: 1.0.0
prescriptions:
  - assertion: "some check"
    kind: file_exists
    target: some/file
"""
# 'evidence' and 'enforcement' fields are absent


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

def scenario_well_formed() -> None:
    """A: well-formed companion → exit 0, valid=true, no errors."""
    with _fixture(WELL_FORMED_YAML) as path:
        r = _run(path)
        _eq("A exit", r.returncode, 0)
        d = json.loads(r.stdout)
        _eq("A valid", d["valid"], True)
        _eq("A no errors", d["errors"], [])


def scenario_missing_top_level_key() -> None:
    """B: missing required top-level key ('version') → exit 1, valid=false, error named."""
    with _fixture(MISSING_TOP_LEVEL_KEY_YAML) as path:
        r = _run(path)
        _eq("B exit", r.returncode, 1)
        d = json.loads(r.stdout)
        _eq("B valid", d["valid"], False)
        if not d["errors"]:
            raise SmokeFailure("B: expected at least one error")
        combined = " ".join(d["errors"]).lower()
        _in("B error mentions 'version'", "version", combined)


def scenario_invalid_kind() -> None:
    """C: prescription with invalid assertion.kind → exit 1, error names the bad kind."""
    with _fixture(INVALID_KIND_YAML) as path:
        r = _run(path)
        _eq("C exit", r.returncode, 1)
        d = json.loads(r.stdout)
        _eq("C valid", d["valid"], False)
        if not d["errors"]:
            raise SmokeFailure("C: expected at least one error")
        combined = " ".join(d["errors"])
        _in("C error mentions bad kind", "nonexistent_kind", combined)


def scenario_missing_required_field() -> None:
    """D: prescription missing required fields ('evidence', 'enforcement') → exit 1."""
    with _fixture(MISSING_REQUIRED_FIELD_YAML) as path:
        r = _run(path)
        _eq("D exit", r.returncode, 1)
        d = json.loads(r.stdout)
        _eq("D valid", d["valid"], False)
        if not d["errors"]:
            raise SmokeFailure("D: expected at least one error")
        # Both missing fields should be named in errors
        combined = " ".join(d["errors"]).lower()
        _in("D error mentions 'evidence'", "evidence", combined)
        _in("D error mentions 'enforcement'", "enforcement", combined)


def scenario_file_not_found() -> None:
    """E: file does not exist → exit 2, error mentions file-not-found."""
    nonexistent = "/tmp/does_not_exist_adr_prescriptions_smoke_test.yaml"
    Path(nonexistent).unlink(missing_ok=True)  # ensure it really doesn't exist
    r = _run(nonexistent)
    _eq("E exit", r.returncode, 2)
    d = json.loads(r.stdout)
    _eq("E valid", d["valid"], False)
    if not d["errors"]:
        raise SmokeFailure("E: expected at least one error")
    combined = " ".join(d["errors"]).lower()
    _in("E error mentions 'not found'", "not found", combined)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

SCENARIOS = [
    ("A: well-formed → exit 0", scenario_well_formed),
    ("B: missing top-level key → exit 1", scenario_missing_top_level_key),
    ("C: invalid assertion.kind → exit 1", scenario_invalid_kind),
    ("D: missing required prescription field → exit 1", scenario_missing_required_field),
    ("E: file not found → exit 2", scenario_file_not_found),
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
