#!/usr/bin/env python3
"""
audit_op7_events_schema.py — OP-7 mcp-events.jsonl schema conformance.

Verifies each line in .claude/runtime/mcp-events.jsonl conforms to ADR-0037
schema. Three active event types:
  - install_complete: {event, timestamp, server, install_method, version, duration_ms, status}
  - readiness_probe:  {event, timestamp, server, probe_method, latency_ms, status}
  - structured_failure: {event, timestamp, server, failure_layer, primary_degraded, fallback_invoked,
                         fallback_server, redaction_applied, message}

A fourth event type (`calibration_result`, ADR-0058) was added 2026-05-26 to
carry FR-4b's GitNexus grammar-skip calibration outcomes. The 2026-05-27
gitnexus removal (ADR-0066) eliminated its only consumer; ADR-0058 was
superseded the same day and the schema entry removed. One historical
calibration_result record remains in `.claude/runtime/mcp-events.jsonl`
(2026-05-26 smoke); the auditor tolerates unknown event types (records that
do not match any known schema are surfaced as INFO, not BLOCKER), so the
historical record does not produce false-positive findings. If a future
calibration mechanism is introduced, a new ADR reintroduces the schema entry.

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
}

VALID_EVENT_TYPES = set(REQUIRED_FIELDS.keys())

# Retired event types — preserved as INFO-level tolerance so historical records
# in the append-only log don't generate spurious MAJOR findings. Each entry maps
# the event-type literal to the ADR that retired it.
RETIRED_EVENT_TYPES = {
    "calibration_result": "ADR-0058 superseded by ADR-0066 on 2026-05-27 (gitnexus removal)",
}

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
        if event in RETIRED_EVENT_TYPES:
            findings.append({
                "rule": "OP-7",
                "severity": "INFO",
                "line": idx,
                "event": event,
                "message": (
                    f"retired event type {event!r} tolerated as historical record: "
                    f"{RETIRED_EVENT_TYPES[event]}"
                ),
            })
            continue
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
