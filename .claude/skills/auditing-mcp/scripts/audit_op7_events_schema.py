#!/usr/bin/env python3
"""
audit_op7_events_schema.py — OP-7 mcp-events.jsonl schema conformance.

Verifies each line in .claude/runtime/mcp-events.jsonl conforms to ADR-0037
schema. Three event types:
  - install_complete: {event, timestamp, server, install_method, version, duration_ms, status}
  - readiness_probe:  {event, timestamp, server, probe_method, latency_ms, status}
  - structured_failure: {event, timestamp, server, failure_layer, primary_degraded, fallback_invoked,
                         fallback_server, redaction_applied, message}

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

        missing = REQUIRED_FIELDS[event] - set(rec.keys())
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
