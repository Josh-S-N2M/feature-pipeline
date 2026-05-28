#!/usr/bin/env python3
"""
analyze_subagent.py — Subagent body & description analysis.

Detects:
  - SA-2 vague descriptions (filler patterns, missing triggers)
  - SA-9 empty body
  - SA-10 body-in-description
  - SA-12 over-broad WebFetch/WebSearch (when present in tools)
  - Body-tool mismatch (body references tools not in `tools:`)
  - Aspirational language in body

Usage:
    python3 analyze_subagent.py <path-to-subagent.md>
"""
import json
import re
import sys
from pathlib import Path

# Filler patterns (SA-2)
FILLER_PATTERNS = [
    re.compile(r"\bhelpful assistant\b", re.I),
    re.compile(r"\bvarious tasks\b", re.I),
    re.compile(r"\bdo (?:its|my) best\b", re.I),
    re.compile(r"\bdesigned to be\b", re.I),
    re.compile(r"\bmodern best practices\b", re.I),
    re.compile(r"\bleverages?\b", re.I),
    re.compile(r"\bpowerful\b", re.I),
    re.compile(r"\bcutting[\- ]edge\b", re.I),
    re.compile(r"\bworld[\- ]class\b", re.I),
]

# Triggering language (presence is good)
# v4.6.0 (D-4): extended with 5 project-convention patterns. The original 5
# patterns missed common project phrasings used by genuine triggers, causing
# 29 false-positive SA-2 findings. Per AC-FR-4-b option (ii) the regex is
# tightened — original patterns retained, new ones added below.
TRIGGER_PATTERNS = [
    re.compile(r"\buse\s+(?:when|for)\b", re.I),
    re.compile(r"\bwhen\s+\w+ing\b", re.I),
    re.compile(r"\bdelegate\b", re.I),
    re.compile(r"\bcalled?\s+when\b", re.I),
    re.compile(r"\binvoke\s+when\b", re.I),
    # D-4 extensions:
    re.compile(r"\bat\s+the\s+[\w-]+(\s+[\w-]+)?\s+stage\b", re.I),     # "at the PRD stage", "at the Cross-Artifact Audit stage"
    re.compile(r"\bduring\s+\w+(\s+\w+){0,3}\b", re.I),            # "during planning", "during the discovery sweep"
    re.compile(r"\bone\s+invocation\s+per\b", re.I),               # "one invocation per pipeline run"
    re.compile(r"\buse\s+at\b", re.I),                              # "use at <stage>", "use at every gate"
    re.compile(r"\bafter\s+\w+(\s+\w+)?\s+(?:passes|completes|finishes)\b", re.I),  # "after the audit passes"
]

# Tool name mentions in body
TOOL_MENTIONS = re.compile(r"\b(Bash|Read|Write|Edit|Grep|Glob|WebFetch|WebSearch)\b")


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """Forwarder to canonical split_frontmatter (ADR-0068)."""
    import sys as _sys
    from pathlib import Path as _Path
    _here = _Path(__file__).resolve()
    for _p in _here.parents:
        if (_p / ".claude" / "canonical").is_dir():
            _sys.path.insert(0, str(_p / ".claude" / "skills" / "auditing-shared" / "scripts"))
            break
    from frontmatter import split_frontmatter as _shared
    return _shared(text)


def parse_tools_from_frontmatter(fm_text: str) -> list[str]:
    """Extract tools list from frontmatter using simple line parsing.

    Handles three YAML shapes:
      tools: A, B, C           (inline comma-separated)
      tools: [A, B, C]         (inline flow-sequence)
      tools:                   (block sequence on subsequent lines)
        - A
        - B
    """
    tools: list[str] = []
    in_tools_block = False
    for line in fm_text.split("\n"):
        if line.startswith("tools:"):
            rest = line.split(":", 1)[1].strip()
            if rest:
                # Strip YAML flow-sequence brackets if present: [A, B, C] → A, B, C
                if rest.startswith("[") and rest.endswith("]"):
                    rest = rest[1:-1]
                # Inline comma-separated
                tools = [t.strip() for t in rest.split(",") if t.strip()]
            else:
                in_tools_block = True
            continue
        if in_tools_block:
            m = re.match(r"^\s+-\s+(.+)$", line)
            if m:
                tools.append(m.group(1).strip())
            else:
                in_tools_block = False
    return tools


def check_description(desc: str, body: str) -> list[dict]:
    findings = []

    if not desc:
        return findings

    if len(desc) < 50:
        findings.append({
            "dimension": 2, "severity": "MAJOR",
            "what": f"Description is {len(desc)} chars. Too short to convey intent.",
            "fix": "Expand to 50-500 chars with: action verb, input/output, when-to-use.",
        })

    # Filler patterns
    for pat in FILLER_PATTERNS:
        if pat.search(desc):
            findings.append({
                "dimension": 2, "severity": "MINOR",
                "what": f"Filler phrase in description: '{pat.pattern[:30]}'. (SA-2)",
                "fix": "Remove filler. Lead with concrete action verbs.",
            })
            break  # one filler finding is enough

    # Triggering language
    has_trigger = any(p.search(desc) for p in TRIGGER_PATTERNS)
    if not has_trigger:
        findings.append({
            "dimension": 2, "severity": "MAJOR",
            "what": "Description has no triggering language ('use when', 'when reviewing', etc.). Claude has no signal for delegation. (SA-2)",
            "fix": "Add explicit trigger: 'Use when ...' or 'Use for ...'.",
        })

    # SA-10: body-in-description (description >1000 chars with numbered steps)
    if len(desc) > 1000 and re.search(r"^\s*\d+[\.\)]\s", desc, re.M):
        findings.append({
            "dimension": 2, "severity": "MINOR",
            "what": "Description contains numbered steps and is very long; looks like the body is in the description. (SA-10)",
            "fix": "Move the procedural content to the body; keep description as ad copy.",
        })

    return findings


def check_body(body: str, tools_declared: list[str]) -> list[dict]:
    findings = []
    body_stripped = body.strip()

    # SA-9: empty body
    if len(body_stripped) < 50:
        findings.append({
            "dimension": 4, "severity": "MAJOR",
            "what": "Body is empty or near-empty. Subagent has no system prompt. (SA-9)",
            "fix": "Add a body defining the subagent's role, scope, and constraints.",
        })
        return findings

    # Body-tool mismatch: body mentions tools not in `tools:`
    body_tools = set()
    for m in TOOL_MENTIONS.finditer(body):
        body_tools.add(m.group(1))

    declared_tool_names = set()
    for t in tools_declared:
        # Strip args: Bash(git diff *) → Bash
        name = re.split(r"\(", t)[0].strip()
        declared_tool_names.add(name)

    missing = body_tools - declared_tool_names
    if missing and tools_declared:
        findings.append({
            "dimension": 4, "severity": "MAJOR",
            "what": f"Body references tools {sorted(missing)} not in declared `tools:` list.",
            "fix": "Add the tools to `tools:` (with scoping) or remove the body references.",
        })

    # Body size
    line_count = len(body.split("\n"))
    if line_count > 500:
        findings.append({
            "dimension": 4, "severity": "MAJOR",
            "what": f"Body is {line_count} lines (>500). High spawn cost.",
            "fix": "Move detailed instructions to a referenced file the subagent reads on-demand.",
        })

    # Exclusion language
    has_exclusion = bool(re.search(r"\b(don't|do not|must not|never|refuse|reject)\b", body, re.I))
    if not has_exclusion:
        findings.append({
            "dimension": 6, "severity": "MINOR",
            "what": "Body has no exclusion language (don't, never, must not). Subagent will attempt anything asked.",
            "fix": "Add explicit don'ts; what should the subagent refuse to do?",
        })

    return findings


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: analyze_subagent.py <path>"}))
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(json.dumps({"error": f"not a file: {path}"}))
        return 2

    text = path.read_text(encoding="utf-8", errors="replace")
    fm_text, body = split_frontmatter(text)
    if fm_text is None:
        print(json.dumps({"findings": [], "note": "no frontmatter; cannot analyze"}))
        return 0

    # Parse description and tools from frontmatter using simple matching
    desc_match = re.search(r"^description:\s*(.+?)(?=\n[a-zA-Z_-]+:|\n---|\Z)",
                            fm_text, re.M | re.S)
    desc = ""
    if desc_match:
        desc = desc_match.group(1).strip().strip('"\'>').replace("\n  ", " ").strip()

    tools_declared = parse_tools_from_frontmatter(fm_text)

    findings: list = []
    findings.extend(check_description(desc, body))
    findings.extend(check_body(body, tools_declared))

    for f in findings:
        f["location"] = str(path)
        f.setdefault("where", str(path))

    print(json.dumps({
        "target": str(path),
        "description_length": len(desc),
        "body_lines": len(body.split("\n")),
        "tools_declared": tools_declared,
        "findings": findings,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
