#!/usr/bin/env python3
"""Codespaces audit stub.

Per AC-FR-8-b + Q-CC-4 resolution: returns exactly `{"stub": true, "findings": []}`.
The `stub: true` field is what distinguishes a stub from a real-but-empty clean
audit; the downstream phase-quality-reviewer treats stub as "not measured"
rather than "measured zero" per the Q-CC-4 implementation note.
"""
import json
import sys


def main() -> int:
    sys.stdout.write(json.dumps({"stub": True, "findings": []}) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
