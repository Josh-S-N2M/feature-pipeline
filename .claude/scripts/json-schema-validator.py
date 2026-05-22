#!/usr/bin/env python3
"""
json-schema-validator.py — Layer A schema validator for synthesis-pipeline phase artifacts.

Invoked from the PostToolUse hook when Claude writes a file matching
working/synthesis/<run-id>/0[1-5]-*.json. Validates against the schema for
that artifact type and exits non-zero with a single-line error if validation
fails. Silent on success.

Usage:
    python3 json-schema-validator.py <artifact_path>

The artifact's schema is selected by filename pattern:
  01-claims.json       → claim.schema.json
  02-graph.json        → entity-graph.schema.json
  03-critique.json     → critique.schema.json
  04-decision-frames.json → decision-frame.schema.json
  05-substrate-map.json → substrate-mapping.schema.json
  00-manifest.json     → manifest.schema.json

Schema files are resolved relative to the project's .claude/ directory
($CLAUDE_PROJECT_DIR/.claude/skills/synthesize/references/schemas/).

Per Design §8: silent on success, verbose on failure. Errors emitted as
JSON Pointer paths.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


SCHEMA_BY_PATTERN = [
    (re.compile(r"00-manifest\.json$"),       "manifest.schema.json"),
    (re.compile(r"01-claims.*\.json$"),       "claim.schema.json"),
    (re.compile(r"02-graph\.json$"),          "entity-graph.schema.json"),
    (re.compile(r"03-critique.*\.json$"),     "critique.schema.json"),
    (re.compile(r"04-decision-frames\.json$"), "decision-frame.schema.json"),
    (re.compile(r"05-substrate-map\.json$"),  "substrate-mapping.schema.json"),
]


def select_schema(artifact_path: Path) -> str | None:
    """Pick the schema filename matching the artifact filename, or None."""
    name = artifact_path.name
    for pat, schema in SCHEMA_BY_PATTERN:
        if pat.search(name):
            return schema
    return None


def schema_dir() -> Path:
    """Resolve the schema directory under .claude/.

    Prefers $CLAUDE_PROJECT_DIR (set by Claude Code in hooks). Falls back
    to a path relative to this script's parent if the env var is unset
    (e.g., when invoked manually for debugging).
    """
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir:
        return Path(project_dir) / ".claude" / "skills" / "synthesize" / "references" / "schemas"
    # Fallback: scripts/ is sibling to skills/ inside .claude/
    here = Path(__file__).resolve().parent
    return here.parent / "skills" / "synthesize" / "references" / "schemas"


def validate(artifact_path: Path, schema_path: Path) -> tuple[bool, list[dict]]:
    """Validate artifact against schema. Returns (ok, errors)."""
    try:
        import jsonschema
    except ImportError:
        # If jsonschema isn't available, skip validation (don't block writes).
        # Production deployments should ensure jsonschema is installed.
        print(
            f"WARN: jsonschema not installed; skipping validation of {artifact_path}",
            file=sys.stderr,
        )
        return True, []

    try:
        with open(schema_path) as f:
            schema = json.load(f)
    except FileNotFoundError:
        return False, [{"path": "/", "message": f"schema not found: {schema_path}"}]
    except json.JSONDecodeError as e:
        return False, [{"path": "/", "message": f"schema is not valid JSON: {e}"}]

    try:
        with open(artifact_path) as f:
            instance = json.load(f)
    except json.JSONDecodeError as e:
        return False, [{"path": "/", "message": f"artifact is not valid JSON: {e}"}]

    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
    if not errors:
        return True, []
    return False, [
        {
            "path": "/" + "/".join(str(p) for p in e.absolute_path),
            "message": e.message,
        }
        for e in errors
    ]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: json-schema-validator.py <artifact_path>", file=sys.stderr)
        return 2

    artifact_path = Path(sys.argv[1])
    if not artifact_path.is_file():
        # Don't fail the hook for a missing file — that's not our concern.
        return 0

    schema_filename = select_schema(artifact_path)
    if schema_filename is None:
        # Filename doesn't match any phase-artifact pattern; nothing to validate.
        return 0

    schema_path = schema_dir() / schema_filename
    ok, errors = validate(artifact_path, schema_path)
    if ok:
        return 0

    # Verbose on failure: one error per line, JSON Pointer-formatted.
    print(f"FAIL: {artifact_path} does not validate against {schema_filename}", file=sys.stderr)
    for err in errors[:10]:  # Cap at 10 errors to keep output manageable.
        print(f"  {err['path']}: {err['message']}", file=sys.stderr)
    if len(errors) > 10:
        print(f"  ... and {len(errors) - 10} more", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
