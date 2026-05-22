#!/usr/bin/env python3
"""
cross_file_duplication.py — Detect duplicate rules across CLAUDE.md and rules/*.md.

Reads CLAUDE.md and all rules files, identifies substring matches longer than
a threshold, and emits findings. This is the per-skill check; the coordinator's
X6 cross-file check uses the same logic at project level.

Usage:
    python3 cross_file_duplication.py <project-root>
"""
import json
import re
import sys
from pathlib import Path

MIN_SUBSTRING_LEN = 40  # below this, false positives dominate


def normalize_line(s: str) -> str:
    """Lowercase, collapse whitespace."""
    return re.sub(r"\s+", " ", s.lower().strip())


def extract_rule_sentences(text: str) -> list[tuple[str, str]]:
    """Extract sentence-like lines (the kind that look like rules).
    Skip headings, list markers alone, code fences, etc.
    Returns list of (original_line, normalized) for matching."""
    out = []
    in_fence = False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # Skip headings
        if line.lstrip().startswith("#"):
            continue
        # Skip empty
        if not line.strip():
            continue
        # Skip lone list markers
        if re.match(r"^[\s\*\-]+$", line):
            continue
        # Skip very short
        normalized = normalize_line(line.lstrip("- *#").strip())
        if len(normalized) < MIN_SUBSTRING_LEN:
            continue
        out.append((line, normalized))
    return out


def find_duplicates(file_a_lines: list[tuple[str, str]],
                     file_b_lines: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Find lines that match between two files. Returns list of (line_a, line_b)."""
    matches = []
    b_normalized = {b_norm: b_line for b_line, b_norm in file_b_lines}
    for a_line, a_norm in file_a_lines:
        if a_norm in b_normalized:
            matches.append((a_line, b_normalized[a_norm]))
    return matches


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: cross_file_duplication.py <project-root>"}))
        return 2

    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"not a directory: {root}"}))
        return 2

    # Gather candidate files
    candidates = []
    for name in ("CLAUDE.md", "CLAUDE.local.md", ".claude/CLAUDE.md"):
        p = root / name
        if p.is_file():
            candidates.append(p)
    rules_dir = root / ".claude" / "rules"
    if rules_dir.is_dir():
        candidates.extend(p for p in rules_dir.glob("*.md") if p.is_file())

    if len(candidates) < 2:
        print(json.dumps({
            "target": str(root),
            "files_examined": [str(c) for c in candidates],
            "findings": [],
            "note": "Fewer than 2 candidate files; no duplication check needed.",
        }))
        return 0

    # Parse each
    file_lines = {}
    for f in candidates:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        file_lines[f] = extract_rule_sentences(text)

    # Pair-wise compare
    findings: list = []
    seen_pairs = set()
    files = list(file_lines.keys())
    for i, fa in enumerate(files):
        for fb in files[i+1:]:
            pair_key = tuple(sorted([str(fa), str(fb)]))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)
            matches = find_duplicates(file_lines[fa], file_lines[fb])
            for a_line, b_line in matches:
                findings.append({
                    "dimension": 10,
                    "severity": "MINOR",
                    "location": f"{fa.relative_to(root)} ↔ {fb.relative_to(root)}",
                    "what": f"Duplicate rule across files: {a_line.strip()[:80]}",
                    "fix": "Keep one canonical copy; remove from the other.",
                })

    for f in findings:
        f.setdefault("where", f["location"])

    print(json.dumps({
        "target": str(root),
        "files_examined": [str(c) for c in candidates],
        "findings": findings,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
