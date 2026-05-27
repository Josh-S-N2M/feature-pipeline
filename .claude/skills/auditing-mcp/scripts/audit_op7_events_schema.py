#!/usr/bin/env python3
"""
audit_op7_events_schema.py — OP-7 mcp-events.jsonl schema conformance.

Verifies each line in .claude/runtime/mcp-events.jsonl conforms to ADR-0037
schema. Four event types:
  - install_complete: {event, timestamp, server, install_method, version, duration_ms, status}
  - readiness_probe:  {event, timestamp, server, probe_method, latency_ms, status}
  - structured_failure: {event, timestamp, server, failure_layer, primary_degraded, fallback_invoked,
                         fallback_server, redaction_applied, message}
  - calibration_result: {event, timestamp, server, mechanism, version, duration_ms, outcome,
                         signals, note}   (ADR-0058; FR-4b emission)

Each record MUST be valid JSON on its own line. Records may carry optional fields
(e.g., redaction_applied annotation per OP-6).

Usage:
    python3 audit_op7_events_schema.py <repo-root>
"""
import json
import sys
from pathlib import Path


REQUIRED_FIELDS = {
    "install_complete": {"event", "timestamp", "server", "install_method", "version", "status"},
    "readiness_probe": {"event", "timestamp", "server", "probe_method", "status"},
    "structured_failure": {"event", "timestamp", "server", "failure_layer", "message"},
    # ADR-0058 calibration_result schema (the FR-4b gitnexus grammar-skip
    # mechanism was retired with the 2026-05-27 gitnexus removal per ADR-0066;
    # the schema is preserved for future calibration mechanisms).
    "calibration_result": {
        "event",
        "timestamp",
        "server",
        "mechanism",
        "version",
        "duration_ms",
        "outcome",
        "signals",
        "note",
    },
}

VALID_EVENT_TYPES = set(REQUIRED_FIELDS.keys())

# Backward-compatible field aliases. Historical records (pre-schema-ratification)
# used different field names that conveyed the same information. The auditor
# treats an alias as satisfying the canonical field requirement so historical
# entries don't generate false-positive "missing required field" findings.
FIELD_ALIASES = {
    "readiness_probe": {
        # Legacy `result: "fail"` is equivalent to `status: "fail"` (the
        # records that use `result` predate the status-vocabulary ratification).
        "status": ("result",),
    },
    "structured_failure": {
        # Legacy `note` was used in place of `message` in some early records.
        "message": ("note",),
    },
}


def _canonical_keys(event: str, rec: dict) -> set:
    """Return the set of canonical field names this record satisfies, treating
    documented historical aliases as the canonical name."""
    keys = set(rec.keys())
    aliases = FIELD_ALIASES.get(event, {})
    for canonical, alias_tuple in aliases.items():
        if canonical not in keys and any(a in keys for a in alias_tuple):
            keys.add(canonical)
    return keys


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: audit_op7_events_schema.py <repo-root>"}))
        return 2

    repo = Path(sys.argv[1]).resolve()
    jsonl = repo / ".claude" / "runtime" / "mcp-events.jsonl"

    findings = []
    line_count = 0

    if not jsonl.exists() or jsonl.stat().st_size == 0:
        out = {
            "rule": "OP-7",
            "name": "mcp-events.jsonl schema conformance",
            "jsonl_path": str(jsonl.relative_to(repo)),
            "line_count": 0,
            "findings": [],
            "note": "JSONL is empty or missing — schema can't be checked. Run postCreate + postStart first.",
        }
        print(json.dumps(out, indent=2))
        return 0

    for idx, line in enumerate(jsonl.read_text().splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        line_count += 1
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as e:
            findings.append({
                "rule": "OP-7",
                "severity": "BLOCKER",
                "line": idx,
                "message": f"invalid JSON: {e}",
            })
            continue

        event = rec.get("event")
        if event not in VALID_EVENT_TYPES:
            findings.append({
                "rule": "OP-7",
                "severity": "MAJOR",
                "line": idx,
                "message": f"unknown event type: {event}",
            })
            continue

        missing = REQUIRED_FIELDS[event] - _canonical_keys(event, rec)
        if missing:
            findings.append({
                "rule": "OP-7",
                "severity": "MAJOR",
                "line": idx,
                "event": event,
                "missing_fields": sorted(missing),
                "message": f"record missing required fields for {event}",
            })

        if event == "calibration_result" and not missing:
            valid_outcomes = {"pass", "fail", "drift_detected"}
            outcome_val = rec.get("outcome")
            if outcome_val not in valid_outcomes:
                findings.append({
                    "rule": "OP-7",
                    "severity": "MAJOR",
                    "line": idx,
                    "event": event,
                    "message": (
                        f"calibration_result outcome must be one of "
                        f"{sorted(valid_outcomes)}, got: {outcome_val!r}"
                    ),
                })

    out = {
        "rule": "OP-7",
        "name": "mcp-events.jsonl schema conformance",
        "jsonl_path": str(jsonl.relative_to(repo)),
        "line_count": line_count,
        "findings": findings,
    }
    print(json.dumps(out, indent=2))
    return 1 if any(f["severity"] == "BLOCKER" for f in findings) else (2 if findings else 0)


if __name__ == "__main__":
    sys.exit(main())
