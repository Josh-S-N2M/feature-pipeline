#!/usr/bin/env python3
"""validate_adr_prescriptions.py — Schema validator for ADR companion prescription files.

Validates a single `adrs/ADR-NNNN-<slug>.prescriptions.yaml` companion file per
ADR-0059 (Companion-File Schema for ADR Design-Realization Audits) and FR-1 of
`pipeline-design-time-discipline-r1`.

Usage:
    python3 validate_adr_prescriptions.py <path-to-prescriptions.yaml>

Output: JSON to stdout with shape:
    {"file": "<path>", "valid": <bool>, "errors": [...]}

Exit codes:
    0  valid — schema is well-formed, all assertions are valid
    1  invalid — one or more schema violations found
    2  file not found or YAML parse error

Assertion kind vocabulary (8 values per ADR-0059 §Consequences §Neutral Consequences):
    regex_present, regex_not_present, jsonpath_equals, jsonpath_count,
    file_exists, file_not_exists, substring_present, substring_absent
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Schema constants (per ADR-0059)
# ---------------------------------------------------------------------------

REQUIRED_TOP_LEVEL_KEYS = {"adr_id", "version", "prescriptions"}

VALID_ASSERTION_KINDS = frozenset({
    "regex_present",
    "regex_not_present",
    "jsonpath_equals",
    "jsonpath_count",
    "file_exists",
    "file_not_exists",
    "substring_present",
    "substring_absent",
})

REQUIRED_PRESCRIPTION_KEYS = {"assertion", "kind", "target", "evidence", "enforcement"}

VALID_ENFORCEMENT_VALUES = {"required", "recommended", "informational"}


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _validate_top_level(data: dict, errors: list) -> bool:
    """Check required top-level keys are present. Returns True if structure is usable."""
    missing = REQUIRED_TOP_LEVEL_KEYS - set(data.keys())
    for key in sorted(missing):
        errors.append(f"missing required top-level key: '{key}'")
    if "prescriptions" in data and not isinstance(data["prescriptions"], list):
        errors.append(
            f"'prescriptions' must be a list, got {type(data['prescriptions']).__name__}"
        )
        return False
    return "prescriptions" not in missing


def _validate_prescription(entry: object, index: int, errors: list) -> None:
    """Validate a single prescription entry."""
    if not isinstance(entry, dict):
        errors.append(
            f"prescriptions[{index}]: expected a mapping, got {type(entry).__name__}"
        )
        return

    # Check required fields
    missing_fields = REQUIRED_PRESCRIPTION_KEYS - set(entry.keys())
    for field in sorted(missing_fields):
        errors.append(f"prescriptions[{index}]: missing required field '{field}'")

    # Validate assertion.kind (flat field, not nested — spec uses kind at the entry level)
    if "kind" in entry:
        kind = entry["kind"]
        if kind not in VALID_ASSERTION_KINDS:
            errors.append(
                f"prescriptions[{index}]: invalid assertion.kind '{kind}'; "
                f"must be one of: {', '.join(sorted(VALID_ASSERTION_KINDS))}"
            )

    # Validate enforcement value if present
    if "enforcement" in entry:
        enforcement = entry["enforcement"]
        if enforcement not in VALID_ENFORCEMENT_VALUES:
            errors.append(
                f"prescriptions[{index}]: invalid enforcement '{enforcement}'; "
                f"must be one of: {', '.join(sorted(VALID_ENFORCEMENT_VALUES))}"
            )

    # Validate non-empty required string fields
    for field in ("assertion", "target", "evidence"):
        if field in entry:
            value = entry[field]
            if not isinstance(value, str) or not value.strip():
                errors.append(
                    f"prescriptions[{index}]: '{field}' must be a non-empty string"
                )


def validate(file_path: str) -> tuple[bool, list[str]]:
    """
    Validate the companion prescriptions YAML at *file_path*.

    Returns (valid: bool, errors: list[str]).
    Raises FileNotFoundError if the file does not exist.
    Raises yaml.YAMLError on parse failure.
    """
    path = Path(file_path)
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)

    errors: list[str] = []

    if not isinstance(data, dict):
        errors.append(
            f"document root must be a YAML mapping, got {type(data).__name__ if data is not None else 'null'}"
        )
        return False, errors

    prescriptions_usable = _validate_top_level(data, errors)

    if prescriptions_usable and "prescriptions" in data:
        for i, entry in enumerate(data["prescriptions"]):
            _validate_prescription(entry, i, errors)

    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate an ADR companion .prescriptions.yaml file per ADR-0059."
    )
    parser.add_argument(
        "file",
        help="Path to the .prescriptions.yaml companion file to validate.",
    )
    args = parser.parse_args()

    result: dict = {"file": args.file, "valid": False, "errors": []}

    try:
        valid, errors = validate(args.file)
        result["valid"] = valid
        result["errors"] = errors
        print(json.dumps(result, indent=2))
        return 0 if valid else 1

    except FileNotFoundError:
        result["errors"] = [f"file not found: {args.file}"]
        print(json.dumps(result, indent=2))
        return 2

    except yaml.YAMLError as exc:
        result["errors"] = [f"YAML parse error: {exc}"]
        print(json.dumps(result, indent=2))
        return 2

    except Exception as exc:  # noqa: BLE001 — top-level catch-all per ADR-0035
        result["errors"] = [f"unexpected error: {type(exc).__name__}: {exc}"]
        print(json.dumps(result, indent=2))
        return 2


if __name__ == "__main__":
    sys.exit(main())
