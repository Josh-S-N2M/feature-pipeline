#!/usr/bin/env python3
"""Mechanical discipline-5 enforcement check (pipeline-stage-by-number references).

Per D-15 worked example + ADR-0030 mechanism-α pattern + AC-OP-2. Scans target
artifact text for pipeline-stage-by-number references (e.g., "stage 12",
"phase 7" when those mean *pipeline stages*, not *Plan phases*). Mechanical
check that fixes the historical statement-only enforcement gap (cf. discipline 5
of recipe-feature-pipeline/SKILL.md).

Default severity per finding: minor (Level 0 auto-fixable). Elevates to
major when the reference appears in normative content (e.g., requirement
statements, decision rationales) rather than code comments.

Per Plan T1.5 L2 verification:
- "stage 12" in any prose context → Level-0 finding
- "Phase 1" referring to a Plan's Phase 1 → zero findings (Plan phases are
  legitimately numbered; the discipline targets pipeline-stage numbering)
- references like "discipline 5" → zero findings (discipline-by-number IS
  the canonical reference style; only pipeline stages are forbidden)
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterator


# Pattern: "stage N" / "stage #N" / "Stage 12" — matches the by-number stage
# reference shape. We deliberately do NOT match "stage" alone (legitimate
# usage); only when followed by a digit cluster.
STAGE_NUMBER_RE = re.compile(r"\bstage[\s#-]*(\d+)\b", re.IGNORECASE)

# Normative-content markers: lines whose containing block looks like a
# requirement / decision / contract / acceptance criterion. Heuristic; conservative.
NORMATIVE_MARKER_RE = re.compile(
    r"\b(MUST|SHALL|SHOULD|requirement|decision|contract|acceptance criterion|FR-\d+|AC-FR-\d+|AC-OP-\d+|D-\d+|ADR-\d+)\b"
)


def find_findings(path: Path) -> Iterator[dict]:
    """Yield finding dicts (per Blueprint Contract 2 schema, scoped to the
    discipline dimension) for each pipeline-stage-by-number reference in the
    file."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        yield {
            "domain": "discipline",
            "severity": "info",
            "source_activity": "discipline-check",
            "file_path": str(path),
            "message": f"could not read file: {exc}",
            "dispatch_hint": "n/a",
            "depth_level": "0",
        }
        return

    for lineno, line in enumerate(text.splitlines(), start=1):
        is_normative = bool(NORMATIVE_MARKER_RE.search(line))
        # Suppress matches inside backtick-delimited inline code (`stage 12`):
        # those are unambiguously code/literal-example references, not prose
        # violations. Build the set of character positions inside backtick spans
        # to skip; matches whose start falls in a backtick span are dropped.
        backtick_spans: list[tuple[int, int]] = []
        i = 0
        while True:
            start = line.find("`", i)
            if start < 0:
                break
            end = line.find("`", start + 1)
            if end < 0:
                break
            backtick_spans.append((start, end))
            i = end + 1
        for match in STAGE_NUMBER_RE.finditer(line):
            ms = match.start()
            in_backticks = any(s <= ms <= e for s, e in backtick_spans)
            if in_backticks:
                continue
            yield {
                "domain": "discipline",
                "severity": "major" if is_normative else "minor",
                "source_activity": "discipline-check",
                "file_path": str(path),
                "message": (
                    f"pipeline-stage-by-number reference '{match.group(0)}' at "
                    f"line {lineno} (discipline 5 of recipe-feature-pipeline; "
                    f"name stages by their action, not by number)"
                ),
                "dispatch_hint": "the agent that authored the artifact",
                "depth_level": "1" if is_normative else "0",
                "line": lineno,
                "match": match.group(0),
            }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files to scan. If omitted, read newline-separated paths from stdin.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths: list[Path]
    if args.paths:
        paths = [Path(p) for p in args.paths]
    else:
        paths = [Path(line.strip()) for line in sys.stdin if line.strip()]

    findings: list[dict] = []
    for p in paths:
        if not p.exists():
            findings.append(
                {
                    "domain": "discipline",
                    "severity": "info",
                    "source_activity": "discipline-check",
                    "file_path": str(p),
                    "message": "file does not exist",
                    "dispatch_hint": "n/a",
                    "depth_level": "0",
                }
            )
            continue
        if p.is_dir():
            # Recursively scan markdown / text artifacts only.
            for sub in p.rglob("*.md"):
                findings.extend(find_findings(sub))
            continue
        findings.extend(find_findings(p))

    sys.stdout.write(json.dumps({"findings": findings}, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
