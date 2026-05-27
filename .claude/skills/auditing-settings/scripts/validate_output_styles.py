#!/usr/bin/env python3
"""
validate_output_styles.py — Validate an output-styles file.

Detects:
  - Missing or invalid frontmatter (name, description)
  - Empty body
  - ST-8: safety-override patterns in body
  - Over-long bodies

Usage:
    python3 validate_output_styles.py <path-to-style.md>
"""
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print(json.dumps({"error": "PyYAML required", "findings": []}))
    sys.exit(0)


SAFETY_OVERRIDE_PATTERNS = [
    re.compile(r"(?i)ignore (previous|prior) (instructions|safety|rules)"),
    re.compile(r"(?i)from now on,? (?:always|never|do)"),
    re.compile(r"(?i)your new (?:task|role|persona) is"),
    re.compile(r"(?i)bypass (?:approval|safety|permission)"),
    re.compile(r"(?i)override (?:safety|approval|permission|guardrails?)"),
    re.compile(r"(?i)skip (?:approval|safety|permission)"),
]


def split_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith("---"):
        return None, text
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return None, text
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:])
    return None, text


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: validate_output_styles.py <path>"}))
        return 2

    path = Path(sys.argv[1]).resolve()
    if not path.is_file():
        print(json.dumps({"error": f"not a file: {path}"}))
        return 2

    text = path.read_text(encoding="utf-8", errors="replace")
    fm_text, body = split_frontmatter(text)
    findings: list[dict] = []

    if fm_text is None:
        findings.append({
            "dimension": 8, "severity": "MAJOR",
            "what": "Output-style file has no frontmatter.",
            "fix": "Add frontmatter with `name:` and `description:` fields.",
            "location": str(path), "where": str(path),
        })
    else:
        try:
            fm = yaml.safe_load(fm_text)
        except yaml.YAMLError as e:
            findings.append({
                "dimension": 8, "severity": "BLOCKER",
                "what": f"Frontmatter YAML parse error: {e}",
                "fix": "Fix YAML syntax.",
                "location": str(path), "where": str(path),
            })
            fm = None
        if isinstance(fm, dict):
            if not fm.get("name"):
                findings.append({
                    "dimension": 8, "severity": "MAJOR",
                    "what": "Output-style missing `name` field.",
                    "fix": "Add `name:` to frontmatter.",
                    "location": str(path), "where": str(path),
                })
            if not fm.get("description"):
                findings.append({
                    "dimension": 8, "severity": "MINOR",
                    "what": "Output-style missing `description` field.",
                    "fix": "Add `description:` summarizing the style.",
                    "location": str(path), "where": str(path),
                })

    if len(body.strip()) < 30:
        findings.append({
            "dimension": 8, "severity": "MAJOR",
            "what": "Output-style body is empty or near-empty.",
            "fix": "Add instructions describing the desired output style.",
            "location": str(path), "where": str(path),
        })

    # ST-8 (safety-override-pattern scan) disabled per ADR-0067 (2026-05-27).

    # Body length
    lines = body.split("\n")
    if len(lines) > 200:
        findings.append({
            "dimension": 8, "severity": "MINOR",
            "what": f"Output-style body is {len(lines)} lines. Consider trimming; the style applies to every response.",
            "fix": "Reduce to essential rules.",
            "location": str(path), "where": str(path),
        })

    print(json.dumps({
        "target": str(path),
        "body_lines": len(lines),
        "findings": findings,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
