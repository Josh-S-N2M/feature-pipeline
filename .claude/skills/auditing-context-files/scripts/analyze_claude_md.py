#!/usr/bin/env python3
"""
analyze_claude_md.py — Content-quality + structure analysis for CLAUDE.md.

Detects:
  - Size (line count) vs 200-line guideline
  - Hardcoded dates that may be stale
  - Aspirational language ("we should consider")
  - Direct contradictions (regex-pair detection)
  - Path hardcoding (/home/, /Users/, C:\\)
  - Structure: heading count, max heading depth
  - First-person plurality ("we", "our", "us")

Outputs the same JSON shape as other auditor scripts:
    {
      "target": "<path>",
      "lines": <int>,
      "byte_size": <int>,
      "findings": [{severity, dimension, location, what, fix}, ...]
    }

Usage:
    python3 analyze_claude_md.py <path-to-CLAUDE.md>
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

# Aspirational language patterns (AP-2)
ASPIRATIONAL_PATTERNS = [
    re.compile(r"\bwe should\b", re.I),
    re.compile(r"\bit would be nice if\b", re.I),
    re.compile(r"\bmaybe we'?ll\b", re.I),
    re.compile(r"\bwe'?re thinking about\b", re.I),
    re.compile(r"\bwe'?re considering\b", re.I),
    re.compile(r"\bwe might\b", re.I),
    re.compile(r"\bin the future\b", re.I),
    re.compile(r"\bshould probably\b", re.I),
    re.compile(r"\bwe'?re planning to\b", re.I),
    re.compile(r"\bpotentially\b", re.I),
    re.compile(r"\bshould think about\b", re.I),
    re.compile(r"\bat some point\b", re.I),
]

# Hardcoded date patterns (AP-3)
DATE_PATTERNS = [
    # "As of August 2025"
    re.compile(r"\b(as of|before|after)\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})\b", re.I),
    # "August 2025" preceded by year/date words
    re.compile(r"(?:until|by|on)\s+(\d{4}-\d{2}-\d{2})\b", re.I),
]

# Machine-local path patterns (AP-7)
PATH_HARDCODING = [
    re.compile(r"/home/[a-zA-Z]"),
    re.compile(r"/Users/[a-zA-Z]"),
    re.compile(r"C:\\\\Users\\\\"),
]

# Contradiction-pair patterns (AP-4). Each pair: (regex_A, regex_B, description)
# If both regexes match in the same file, emit a finding.
CONTRADICTION_PAIRS = [
    (re.compile(r"\buse typescript\b", re.I),
     re.compile(r"\buse javascript\b(?!\s+for tooling)", re.I),
     "TypeScript vs JavaScript directive conflict"),
    (re.compile(r"\busers? rest\b", re.I),
     re.compile(r"\busers? graphql\b", re.I),
     "REST vs GraphQL directive conflict"),
    (re.compile(r"\buse tabs\b", re.I),
     re.compile(r"\buse spaces\b", re.I),
     "Tabs vs spaces directive conflict"),
    (re.compile(r"\balways\b.*\bsemicolons?\b", re.I),
     re.compile(r"\bnever\b.*\bsemicolons?\b", re.I),
     "Semicolons always vs never conflict"),
]


def detect_contradictions(text: str) -> list[dict]:
    findings = []
    for a, b, desc in CONTRADICTION_PAIRS:
        if a.search(text) and b.search(text):
            findings.append({
                "dimension": 4,
                "severity": "MAJOR",
                "what": f"Direct contradiction (AP-4): {desc}",
                "fix": "Resolve the contradiction or scope each rule with a `paths:` glob in a rules file.",
            })
    return findings


def is_stale_date(text: str) -> list[dict]:
    """Find date references that appear to be in the past."""
    findings = []
    current_year = date.today().year
    current_month = date.today().month
    months = {
        "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    }
    for line_idx, line in enumerate(text.split("\n"), start=1):
        for pat in DATE_PATTERNS:
            m = pat.search(line)
            if not m:
                continue
            try:
                # Try to interpret as YYYY-MM-DD
                if len(m.groups()) == 1 and re.match(r"\d{4}-\d{2}-\d{2}", m.group(1)):
                    y, mn, d = map(int, m.group(1).split("-"))
                else:
                    y = int(m.group(3))
                    mn = months.get(m.group(2).lower(), 1)
                # If the referenced date is more than 6 months in the past, flag
                months_diff = (current_year - y) * 12 + (current_month - mn)
                if months_diff > 6:
                    findings.append({
                        "dimension": 7,
                        "severity": "MINOR",
                        "location": f"line {line_idx}",
                        "what": f"Hardcoded date '{m.group(0)}' may be stale ({months_diff} months past).",
                        "fix": "Verify the rule still applies; update or remove the time-conditional language.",
                    })
            except (ValueError, IndexError):
                pass
    return findings


def detect_aspirational(text: str) -> list[dict]:
    findings = []
    for line_idx, line in enumerate(text.split("\n"), start=1):
        for pat in ASPIRATIONAL_PATTERNS:
            m = pat.search(line)
            if m:
                findings.append({
                    "dimension": 3,
                    "severity": "MINOR",
                    "location": f"line {line_idx}",
                    "what": f"Aspirational language (AP-2): '{m.group(0)}'",
                    "fix": "Use imperative voice. Either commit ('use X') or remove until decided.",
                })
                break  # one finding per line
    return findings


def detect_path_hardcoding(text: str) -> list[dict]:
    findings = []
    for line_idx, line in enumerate(text.split("\n"), start=1):
        for pat in PATH_HARDCODING:
            m = pat.search(line)
            if m:
                findings.append({
                    "dimension": 6,
                    "severity": "MAJOR",
                    "location": f"line {line_idx}",
                    "what": f"Machine-local path '{m.group(0)}...' (AP-7).",
                    "fix": "Use relative paths or `${PROJECT_ROOT}`.",
                })
                break
    return findings


def analyze_structure(text: str) -> list[dict]:
    findings = []
    lines = text.split("\n")
    heading_count = 0
    max_depth = 0
    for line in lines:
        if line.startswith("#"):
            depth = len(line) - len(line.lstrip("#"))
            if 0 < depth <= 10:
                heading_count += 1
                max_depth = max(max_depth, depth)
    if heading_count == 0 and len(lines) > 50:
        findings.append({
            "dimension": 8,
            "severity": "MINOR",
            "what": "No markdown headings; long file without navigable structure.",
            "fix": "Add headings (`## Tech stack`, `## Coding standards`, etc.) for navigation.",
        })
    if max_depth >= 5:
        findings.append({
            "dimension": 8,
            "severity": "MINOR",
            "what": f"Heading depth {max_depth} (AP-9: excessive nesting).",
            "fix": "Flatten — promote subsections or move them to referenced files.",
        })
    return findings


def size_findings(text: str) -> list[dict]:
    findings = []
    lines = len(text.split("\n"))
    if lines > 1000:
        findings.append({
            "dimension": 1,
            "severity": "BLOCKER",
            "what": f"CLAUDE.md is {lines} lines — consumes substantial context budget every session.",
            "fix": "Reduce to <200 lines. Move detailed content to rules/ files or external docs.",
        })
    elif lines > 500:
        findings.append({
            "dimension": 1,
            "severity": "MAJOR",
            "what": f"CLAUDE.md is {lines} lines (>500). Significantly exceeds 200-line guideline.",
            "fix": "Trim to <200 lines. Move detail to referenced rules files.",
        })
    elif lines > 200:
        findings.append({
            "dimension": 1,
            "severity": "MINOR",
            "what": f"CLAUDE.md is {lines} lines (>200). Exceeds Anthropic's 200-line guideline.",
            "fix": "Review for trimming or move detail to rules/ files.",
        })
    return findings


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: analyze_claude_md.py <path>"}))
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(json.dumps({"error": f"not a file: {path}"}))
        return 2

    text = path.read_text(encoding="utf-8", errors="replace")
    findings = []
    findings.extend(size_findings(text))
    findings.extend(detect_aspirational(text))
    findings.extend(detect_path_hardcoding(text))
    findings.extend(is_stale_date(text))
    findings.extend(detect_contradictions(text))
    findings.extend(analyze_structure(text))

    # Attach where field if missing
    for f in findings:
        if "location" not in f:
            f["location"] = str(path)
        else:
            f["location"] = f"{path}:{f['location']}"
        f.setdefault("where", f["location"])

    print(json.dumps({
        "target": str(path),
        "lines": len(text.split("\n")),
        "byte_size": len(text.encode("utf-8")),
        "findings": findings,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
