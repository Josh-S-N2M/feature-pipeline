#!/usr/bin/env python3
"""parse_blocks_x_markers.py — Canonical parser for Blocks-X HTML-comment markers per ADR-0063.

Reads a markdown file (single positional arg: path), scans for HTML-comment markers
matching the canonical grammar defined in ADR-0063, and emits a JSON report to stdout.

Canonical grammar (ADR-0063 §Decision):
    <!-- BLOCKS: <stage-slug>-completion -->
where <stage-slug> is a kebab-case identifier (lowercase alphanumeric + hyphens).

Optional payload (ignored by parser, retained in raw_match):
    <!-- BLOCKS: design-cc-completion — A-5 grammar undecided -->

Parser regex per ADR-0063:
    <!--\\s*BLOCKS:\\s*([a-z0-9-]+)-completion(?:\\s+—\\s+[^\\n]*)?\\s*-->

Three reserved transition_name values for state-transitions log (ADR-0063 §Decision):
    BLOCKS_X_RESOLVED, BLOCKS_X_DEFERRED_WITH_OI, BLOCKS_X_FALSE_POSITIVE

FR-9 of pipeline-cross-artifact-discipline-r1 requires this parser to be shared
across auditing surfaces (orchestrator stage-transition checkpoints, run_phase_checks.py).

Exit codes:
  0 = all markers found and well-formed (at least one marker present, zero malformed)
  1 = one or more malformed markers present (regardless of well-formed count)
  2 = no markers found (informational; not an error condition)

NFR-8: Python 3.8+ stdlib only.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Grammar constants — ADR-0063 canonical definition
# ---------------------------------------------------------------------------

# The well-formed marker regex.  Captures: (stage_slug_without_completion_suffix).
# The optional em-dash payload is captured in group 2 (may be None).
_WELLFORMED_RE = re.compile(
    r"<!--\s*BLOCKS:\s*([a-z0-9][a-z0-9-]*)-completion"
    r"(?:\s+—\s+([^\n-][^\n]*?))?\s*-->"
)

# Broader regex to catch anything that *looks like* a BLOCKS marker but is
# malformed — used to surface candidate malformed markers in the findings.
_CANDIDATE_RE = re.compile(
    r"<!--\s*BLOCKS\s*:?\s*[^\-\n>][^\n>]*-->",
    re.IGNORECASE,
)

# Slug validity: only lowercase kebab-case alphanumeric
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def _classify_malformed(raw: str) -> str:
    """Return a human-readable reason why a candidate marker is malformed."""
    # Check for wrong-case BLOCKS token
    if re.search(r"<!--\s*[Bb][Ll][Oo][Cc][Kk][Ss]", raw) and "BLOCKS:" not in raw:
        return "BLOCKS token wrong case (must be uppercase 'BLOCKS:')"
    # Missing colon after BLOCKS
    if re.search(r"<!--\s*BLOCKS\s+", raw):
        return "missing colon after BLOCKS token"
    # Missing -completion suffix: extract what slug looks like
    inner = re.search(r"<!--\s*BLOCKS:\s*([^\s>-][^\s>]*)\s*-->", raw)
    if inner and not inner.group(1).endswith("-completion"):
        return f"stage slug missing '-completion' suffix: {inner.group(1)!r}"
    # Uppercase slug
    inner2 = re.search(r"<!--\s*BLOCKS:\s*([A-Z][^\s>-][^\s>]*)-completion", raw)
    if inner2:
        return f"stage slug must be kebab-case (lowercase): {inner2.group(1)!r}"
    return "does not conform to canonical grammar: <!-- BLOCKS: <stage-slug>-completion -->"


def scan_file(path: Path) -> dict:
    """Scan *path* for Blocks-X markers and return the report dict.

    Report shape:
        {
            "file": "<absolute path>",
            "markers": [
                {
                    "line_number": <int>,
                    "raw_match": "<str>",
                    "stage_slug": "<str>",
                    "payload_description": "<str | null>"
                },
                ...
            ],
            "malformed": [
                {
                    "line_number": <int>,
                    "raw_match": "<str>",
                    "reason": "<str>"
                },
                ...
            ]
        }
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    markers = []
    malformed = []
    # Track which character offsets have been matched as well-formed so we
    # don't double-report them as malformed.
    wellformed_spans: list[tuple[int, int]] = []

    # First pass: collect well-formed markers with their line numbers.
    for m in _WELLFORMED_RE.finditer(text):
        # Compute line number (1-based) from match start offset.
        line_no = text.count("\n", 0, m.start()) + 1
        stage_slug = m.group(1)
        payload = m.group(2)
        markers.append({
            "line_number": line_no,
            "raw_match": m.group(0),
            "stage_slug": stage_slug,
            "payload_description": payload.strip() if payload else None,
        })
        wellformed_spans.append((m.start(), m.end()))

    # Second pass: look for candidate (potentially malformed) markers that
    # were not already captured as well-formed.
    for m in _CANDIDATE_RE.finditer(text):
        span = (m.start(), m.end())
        # Skip if this span overlaps any well-formed match.
        if any(ws <= span[0] < we or ws < span[1] <= we for ws, we in wellformed_spans):
            continue
        line_no = text.count("\n", 0, m.start()) + 1
        reason = _classify_malformed(m.group(0))
        malformed.append({
            "line_number": line_no,
            "raw_match": m.group(0),
            "reason": reason,
        })

    return {
        "file": str(path.resolve()),
        "markers": markers,
        "malformed": malformed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse Blocks-X HTML-comment markers per ADR-0063.",
        epilog=(
            "Exit codes: 0=all markers well-formed (>=1 found); "
            "1=malformed markers present; 2=no markers found."
        ),
    )
    parser.add_argument("file", help="Markdown file to scan")
    args = parser.parse_args()

    target = Path(args.file)
    if not target.exists():
        err = {
            "file": str(target),
            "markers": [],
            "malformed": [],
            "error": f"file not found: {target}",
        }
        print(json.dumps(err, indent=2), file=sys.stderr)
        return 1

    report = scan_file(target)
    print(json.dumps(report, indent=2))

    # Exit code logic:
    #   1 if any malformed markers
    #   2 if no markers at all (and no malformed)
    #   0 if markers present and all well-formed
    if report["malformed"]:
        return 1
    if not report["markers"]:
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 — top-level catch-all per ADR-0035
        err = {
            "file": "",
            "markers": [],
            "malformed": [],
            "error": f"unexpected error: {type(exc).__name__}: {exc}",
        }
        print(json.dumps(err, indent=2), file=sys.stderr)
        sys.exit(1)
