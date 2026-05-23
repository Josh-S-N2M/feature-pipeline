#!/usr/bin/env python3
"""Append a state-transition payload to working/feature/<slug>/state-transitions.log.

Per FR-5 + D-16 + Blueprint Contract 5. Reads one JSON object from stdin
(conforming to Contract 5 payload schema) and appends one JSONL line to the
feature's state-transitions.log. Observer-only per D-16: a failure here
does NOT block the substantive transition; failure is surfaced as a
Level-1 finding per AC-FR-5-e.

Per I-AA-609 (cycle-3 correction): the payload schema explicitly includes
T0 (`from_state: INIT, to_state: pending, transition_name: T0`) and
T13 (`to_state: TERMINATED, transition_name: T13`) boundary transitions.
This script does NOT special-case boundary transitions — they use the
same append protocol. Boundary transitions do NOT increment cycle counters
(only T4 + T10 increment per Invariant 10 scope clarification).
"""
import argparse
import json
import sys
from pathlib import Path

# Contract 5 required field set.
REQUIRED_FIELDS = {
    "timestamp",
    "transition_name",
    "from_state",
    "to_state",
    "trigger",
    "invoking_agent",
}


def validate_payload(payload: dict) -> list[str]:
    """Return a list of validation errors (empty if valid)."""
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["payload is not a JSON object"]
    missing = REQUIRED_FIELDS - set(payload.keys())
    if missing:
        errors.append(f"missing required fields: {sorted(missing)}")
    # task_id / phase_id / cycle_counter / artifact_paths_affected / context are optional
    # but if present must have correct types.
    if "artifact_paths_affected" in payload:
        if not isinstance(payload["artifact_paths_affected"], list):
            errors.append("artifact_paths_affected must be a JSON array")
    if "cycle_counter" in payload and payload["cycle_counter"] is not None:
        if not isinstance(payload["cycle_counter"], int):
            errors.append("cycle_counter must be integer or null")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--feature-slug",
        required=True,
        help="Feature slug; log lives at working/feature/<slug>/state-transitions.log",
    )
    parser.add_argument(
        "--log-root",
        default="working/feature",
        help="Root directory containing per-feature dirs (default: working/feature)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero on validation failure (default: observer-only, exit 0 with stderr warning)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"log_state_transition: stdin not valid JSON: {exc}\n")
        return 1 if args.strict else 0

    errors = validate_payload(payload)
    if errors:
        sys.stderr.write(
            "log_state_transition: payload validation failed: "
            + "; ".join(errors)
            + "\n"
        )
        if args.strict:
            return 2
        # Observer-only: surface as a Level-1 finding (caller scans stderr / exit
        # code 0 with stderr non-empty); do not block.

    log_dir = Path(args.log_root) / args.feature_slug
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "state-transitions.log"

    with log_path.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(payload, separators=(",", ":")) + "\n")

    sys.stdout.write(json.dumps({"status": "appended", "log_path": str(log_path)}) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
